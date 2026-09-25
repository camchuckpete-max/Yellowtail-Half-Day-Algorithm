"""LLM turns (SPEC §5.3): one headless Claude Code process per agent, sandboxed, bound to a
physical PIT snapshot through the arena MCP server. Batches the agents of one tick.

The engine calls `run_turns(...)` at turn ticks and at season end. Each turn gets
`runs/<id>/turns/<tag>/<agent>/` with `sandbox/` (what the model sees and may edit), `turn.json`
(server binding), `mcp.json`, `settings.json`, `prompt.md`, `claude.json` (the CLI's result),
`queries.jsonl`, `posts.jsonl`, `strategy_submitted.py` + `submission.json` (if accepted).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARENA = ROOT / "arena"
SANDBOXES = ARENA / "sandboxes"      # git-ignored; NOT under arena/runs, which the turn settings deny
CLAUDE = shutil.which("claude") or "claude"


def turn_dir_for(run_id: str, tag: str, agent: str) -> Path:
    return SANDBOXES / run_id / tag / agent


def archive_turn(turn_dir: Path, run_dir: Path, tag: str, agent: str) -> Path:
    """Copy the finished turn (sandbox included) under runs/<id>/turns/ and delete the live sandbox."""
    dst = run_dir / "turns" / tag / agent
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(turn_dir, dst)
    shutil.rmtree(turn_dir, ignore_errors=True)
    return dst


def _settings(source_repo: Path) -> dict:
    tpl = (ARENA / "claude" / "turn-settings.template.json").read_text()
    tpl = tpl.replace("{ROOT}", str(ROOT).lstrip("/")).replace("{SOURCE}", str(source_repo).lstrip("/"))
    d = json.loads(tpl)
    d.pop("_comment", None)
    return d


def build_prompt(agent: dict, ctx: dict) -> str:
    """ctx: season, doy, hour, season_end (bool), first_turn (bool), results (list), failures (list),
    leaderboard (list), forum_new (list|None), quota_left (int|None), budget_left, pto_left, season_counted."""
    lines = [f"You are **{agent['name']}**, an agent in the yellowtail arena. Read `RULES.md` and `persona.md` first, then `notes.md` and `strategy.py`.", ""]
    if ctx["season_end"]:
        lines.append(f"**Season {ctx['season']} has ended.** This is your season-end turn: write a retrospective into `notes.md` (what worked, what did not, what to test next season) and, if you want, submit a revised `strategy.py` for next season with `submit_strategy`.")
    elif ctx["first_turn"]:
        lines.append(f"**Season {ctx['season']} starts now** (day {ctx['doy']}). Budget ${ctx['budget_left']:.0f}, PTO {ctx['pto_left']:g} days.")
    else:
        lines.append(f"It is season {ctx['season']}, day {ctx['doy']}, {ctx['hour']:02d}:00. Budget left ${ctx['budget_left']:.0f}, PTO left {ctx['pto_left']:g} days.")
    lines.append("Objective: maximise this season's fish (sum of shares) and win the cumulative board." + ("" if ctx["season_counted"] else " (This season is practice: played, not counted.)"))
    lines.append("")
    lines.append("Since your last turn: see `results.json` (your trips and outcomes, rejected actions and strategy errors) and `leaderboard.json`."
                 + (" New forum posts are in `forum_new.json`; `forum_read` has the whole forum." if ctx["forum_new"] is not None else ""))
    lines.append("")
    lines.append("What to do in this turn:")
    lines.append("1. Look at the data with `describe_tables`, `arena_query` and `arena_eval` as much as you need (only rows public as of now exist).")
    lines.append("2. Decide whether to change `strategy.py`. If so, write the full file and call `submit_strategy` with it (it is validated; fix and resubmit if rejected). Keep `describe()` accurate and under 200 words. Remember PTO must be committed 14 days ahead in code (`CommitPTO`).")
    if ctx["quota_left"] is not None:
        lines.append(f"3. Optionally post to the forum with `forum_post` ({ctx['quota_left']} post(s) left this month).")
    lines.append(f"{4 if ctx['quota_left'] is not None else 3}. Update `notes.md` (private) with what you learned and what to check next time; use `write_notes` or edit the file.")
    lines.append("")
    lines.append("You have a limited number of tool calls in this turn; be deliberate. Finish with a two-line summary: what you changed and why.")
    return "\n".join(lines)


def prepare_turn(turn_dir: Path, agent: dict, run_agent_dir: Path, snapshot: Path, forum_path: Path, forum: bool,
                 quota_left: int, now: dict, first_year: int, mask_years: bool, source_repo: Path,
                 results: dict, leaderboard: list, forum_new: list | None) -> Path:
    sb = turn_dir / "sandbox"
    sb.mkdir(parents=True, exist_ok=True)
    shutil.copy(ARENA / "RULES.md", sb / "RULES.md")
    for name in ("persona.md", "strategy.py", "notes.md"):
        src = run_agent_dir / name
        if src.exists():
            shutil.copy(src, sb / name)
    (sb / "results.json").write_text(json.dumps(results, indent=1, default=str))
    (sb / "leaderboard.json").write_text(json.dumps(leaderboard, indent=1))
    if forum_new is not None:
        (sb / "forum_new.json").write_text(json.dumps(forum_new, indent=1))
    (turn_dir / "turn.json").write_text(json.dumps({
        "agent": agent["name"], "sandbox": str(sb), "snapshot": str(snapshot), "forum_path": str(forum_path),
        "forum": bool(forum), "forum_quota_left": int(quota_left), "now": now, "first_year": first_year,
        "mask_years": mask_years}, indent=1))
    (turn_dir / "mcp.json").write_text(json.dumps({"mcpServers": {"arena": {
        "command": sys.executable, "args": [str(ARENA / "mcp_server.py")], "env": {"ARENA_TURN_DIR": str(turn_dir)}}}}))
    (turn_dir / "settings.json").write_text(json.dumps(_settings(source_repo), indent=1))
    return sb


def run_claude(turn_dir: Path, prompt: str, model: str, max_turns: int, budget_usd: float, timeout_s: int) -> dict:
    sb = turn_dir / "sandbox"
    (turn_dir / "prompt.md").write_text(prompt)
    cmd = [CLAUDE, "-p", prompt, "--model", model, "--output-format", "json", "--max-turns", str(max_turns),
           "--max-budget-usd", str(budget_usd), "--mcp-config", str(turn_dir / "mcp.json"), "--strict-mcp-config",
           "--settings", str(turn_dir / "settings.json"), "--permission-mode", "dontAsk", "--restricted",
           "--no-session-persistence", "--setting-sources", ""]
    env = {k: v for k, v in os.environ.items() if not k.startswith("ARENA_")}
    env["CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"] = "0"
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=sb, capture_output=True, text=True, timeout=timeout_s, env=env)
        out = {"exit": r.returncode, "stderr": r.stderr[-4000:], "seconds": round(time.time() - t0, 1)}
        try:
            out["claude"] = json.loads(r.stdout)
        except json.JSONDecodeError:
            out["claude"] = None
            out["stdout"] = r.stdout[-4000:]
    except subprocess.TimeoutExpired:
        out = {"exit": -1, "stderr": f"timeout after {timeout_s}s", "seconds": round(time.time() - t0, 1), "claude": None}
    (turn_dir / "claude.json").write_text(json.dumps(out, indent=1))
    return out


def collect(turn_dir: Path) -> dict:
    """What the turn produced: submission, posts, notes, query count, cost."""
    res: dict = {"submission": None, "posts": [], "notes": None, "queries": 0, "cost_usd": 0.0, "num_turns": 0, "ok": False, "error": None}
    cj = turn_dir / "claude.json"
    if cj.exists():
        c = json.loads(cj.read_text())
        cl = c.get("claude") or {}
        res["ok"] = c.get("exit") == 0 and not cl.get("is_error", False)
        res["cost_usd"] = float(cl.get("total_cost_usd") or 0.0)
        res["num_turns"] = int(cl.get("num_turns") or 0)
        res["seconds"] = c.get("seconds")
        res["summary"] = (cl.get("result") or "")[-1500:]
        if not res["ok"]:
            res["error"] = (c.get("stderr") or "")[-800:] or (cl.get("result") or "")[-800:]
    q = turn_dir / "queries.jsonl"
    if q.exists():
        recs = [json.loads(l) for l in q.read_text().splitlines() if l.strip()]
        res["queries"] = sum(1 for r in recs if r.get("tool") in ("arena_query", "arena_eval"))
        sub_i = next((i for i, r in enumerate(recs) if r.get("tool") == "submit_strategy" and r.get("ok")), None)
        res["queries_before_submit"] = sum(1 for r in recs[:sub_i] if r.get("tool") in ("arena_query", "arena_eval")) if sub_i is not None else None
    if (turn_dir / "submission.json").exists() and (turn_dir / "strategy_submitted.py").exists():
        res["submission"] = json.loads((turn_dir / "submission.json").read_text())
        res["submission"]["code"] = (turn_dir / "strategy_submitted.py").read_text()
    p = turn_dir / "posts.jsonl"
    if p.exists():
        res["posts"] = [json.loads(l)["text"] for l in p.read_text().splitlines() if l.strip()]
    n = turn_dir / "sandbox" / "notes.md"
    if n.exists():
        res["notes"] = n.read_text()
    return res


def run_turns(jobs: list[dict], parallel: int, model_ids: dict, max_turns: int, budget_usd: float, timeout_s: int) -> dict[str, dict]:
    """jobs: [{turn_dir, agent (dict with name, model), prompt}] -> {agent name: collect()}"""
    def one(j):
        model = model_ids.get(j["agent"]["model"], j["agent"]["model"])
        run_claude(Path(j["turn_dir"]), j["prompt"], model, max_turns, budget_usd, timeout_s)
        return j["agent"]["name"], collect(Path(j["turn_dir"]))
    with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        return dict(ex.map(one, jobs))
