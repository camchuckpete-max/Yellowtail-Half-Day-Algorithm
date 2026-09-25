"""Build a publishable dashboard directory from a run: index.html, state.json and one detail file
per agent (`agents/<name>.json`) with every nightly decision (briefing, reasoning, actions,
rejections, outcome) and every planning turn.

    python3 -m arena.tools.export_dashboard --run arena/runs/<id> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ARENA = Path(__file__).resolve().parents[1]


def export(run: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    (out / "agents").mkdir(exist_ok=True)
    shutil.copy(ARENA / "dashboard" / "index.html", out / "index.html")
    state = json.loads((run / "live" / "state.json").read_text())
    shutil.copy(run / "live" / "state.json", out / "state.json")
    turns_all = [json.loads(l) for l in (run / "turns.jsonl").read_text().splitlines()] if (run / "turns.jsonl").exists() else []
    sizes = {}
    for a in state["agents"]:
        name = a["name"]
        nights = []
        f = run / "judgment" / f"{name}.jsonl"
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "skipped" in r:
                    nights.append({"masked": r["masked"], "date": r["date"], "skipped": r["skipped"]})
                    continue
                ans = r.get("answer") or {}
                nights.append({"masked": r["masked"], "date": r["date"], "model": r.get("model"), "cost_usd": r.get("cost_usd"),
                               "seconds": r.get("seconds"), "error": r.get("error"), "reasoning": ans.get("reasoning"),
                               "note": ans.get("note"), "book": ans.get("book") or [], "commit_pto": ans.get("commit_pto") or [],
                               "actions": r.get("actions") or [], "rejected": r.get("rejected") or [], "briefing": r.get("prompt")})
        turns = [{k: t.get(k) for k in ("tag", "season", "doy", "queries", "posts", "submitted", "adopted", "cost_usd", "ok", "error", "summary", "num_turns", "seconds")}
                 for t in turns_all if t.get("agent") == name]
        detail = {"name": name, "kind": a["kind"], "model": a.get("model"), "persona": a.get("persona"), "forum": a.get("forum"),
                  "nights": nights, "turns": turns, "trips": a.get("trips", [])}
        p = out / "agents" / f"{name}.json"
        p.write_text(json.dumps(detail, separators=(",", ":")))
        sizes[name] = p.stat().st_size
    (out / "agents" / "index.json").write_text(json.dumps({"agents": sorted(sizes), "run": state["run"]["id"]}))
    return sizes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sizes = export(Path(a.run), Path(a.out))
    print(f"exported {len(sizes)} agent files, {sum(sizes.values()) / 1e6:.1f} MB total, largest {max(sizes.values()) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
