"""Arena MCP server for one agent turn (SPEC §5.3).

Started by `arena/turns.py` with `ARENA_TURN_DIR` pointing at a directory that holds `turn.json`:
  {agent, sandbox, snapshot, forum_path, forum: bool, forum_quota_left, now: {season, doy, hour, t},
   first_year, mask_years, poison_ticks: [[day_number, hour], ...], run_dir}
Everything the model can reach goes through these tools, bound to the physical PIT snapshot
(`available_at <= now`, masked dates). The source DB is never opened here. Every call is logged
to `<turn dir>/queries.jsonl`.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from arena.mcp_stdio import Server, ToolError  # noqa: E402

TURN_DIR = Path(os.environ["ARENA_TURN_DIR"])
CFG = json.loads((TURN_DIR / "turn.json").read_text())
SNAP = Path(CFG["snapshot"])
SANDBOX = Path(CFG["sandbox"])
META = json.loads((SNAP / "meta.json").read_text())
MAX_ROWS, MAX_CHARS, EVAL_TIMEOUT = 200, 20000, 60

server = Server("arena", instructions="Tools for the yellowtail arena: query the public data as of now, read/post the forum, submit a strategy, keep notes.")
_log_path = TURN_DIR / "queries.jsonl"


def _log(rec: dict) -> None:
    rec["ts"] = datetime.utcnow().isoformat(timespec="seconds")
    with open(_log_path, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


server.log = lambda rec: _log(rec) if rec.get("tool") not in ("arena_query", "arena_eval", "submit_strategy") else None  # those log themselves

# ------------------------------------------------------------------ data
_con = None
_tables: dict[str, pd.DataFrame] = {}


def _duck():
    global _con
    if _con is None:
        import duckdb
        _con = duckdb.connect(":memory:")
        for name in META["tables"]:
            _con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{(SNAP / name).as_posix()}.parquet')")
    return _con


def _table(name: str) -> pd.DataFrame:
    if name not in _tables:
        if name not in META["tables"]:
            raise ToolError(f"unknown table {name!r}; tables: {', '.join(META['tables'])}")
        _tables[name] = pd.read_parquet(SNAP / f"{name}.parquet")
    return _tables[name]


def _frame_text(df: pd.DataFrame, max_rows: int = MAX_ROWS) -> str:
    n = len(df)
    txt = df.head(max_rows).to_csv(index=False)
    if n > max_rows:
        txt += f"... {n - max_rows} more rows not shown (add LIMIT / aggregate)\n"
    if len(txt) > MAX_CHARS:
        txt = txt[:MAX_CHARS] + "\n... truncated\n"
    return txt


@server.tool("describe_tables", "List the tables you can query, their columns and row counts, and the masked-time conventions.",
             {"type": "object", "properties": {}})
def describe_tables() -> str:
    now = CFG["now"]
    lines = [f"Now: season {now['season']}, day {now['doy']}, {now['hour']:02d}:00 (t = {now['t']:.3f}). "
             "Every row below was public at this moment (available_at <= now).",
             "Time columns are masked: <col>_t = days on the arena timeline (fractional for timestamps), "
             "<col>_season, <col>_doy, <col>_hour. avail_* = when the row became public. "
             "Never a calendar year.", ""]
    for name, info in META["tables"].items():
        lines.append(f"- {name} ({info['rows']} rows): {', '.join(info['columns'])}")
    lines += ["", "Offer class -> trips.cls: HD_AM -> hd_am; HD_PM -> hd_pm + hd_unspecified; TWILIGHT -> hd_twilight; "
              "THREE_QUARTER -> three_quarter; FULL_DAY -> full_day; OVERNIGHT -> overnight; DAY_1_5 -> day_1_5 "
              "(multi_day = 2-day and longer, never offered). Your share on a trip = sum(yt) / (sum(anglers) + competitors) "
              "over all rows of that class with fish_date = the fishing date.",
              "Key tables: trips (per-boat counts; fish_date_* = day fished; yt = yellowtail kept+released; anglers), "
              "pier (Scripps Pier water temperature, wtmp_c, hourly), climate (index_id oni/pdo/npgo/mei_v2, monthly value), "
              "forecasts / marine_forecasts (NWS), tides / hourly_tides, ocean (SST/chl/currents tiles), chl, fishdope "
              "(daily report fields and narrative text), buoy, metar, upwelling, glider, sla, kelp."]
    return "\n".join(lines)


@server.tool("arena_query", "Run a read-only SQL query (DuckDB dialect) over the tables. Results are capped at 200 rows; aggregate or LIMIT.",
             {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]})
def arena_query(sql: str) -> str:
    low = sql.strip().lower()
    if not (low.startswith("select") or low.startswith("with") or low.startswith("describe") or low.startswith("show")):
        raise ToolError("read-only: the query must start with SELECT / WITH / DESCRIBE / SHOW")
    if any(k in low for k in ("read_parquet(", "read_csv", "copy ", "attach ", "install ", "load ", "pragma", "getenv", "glob(", "read_text")):
        raise ToolError("file and system functions are not allowed")
    t0 = time.time()
    try:
        df = _duck().execute(sql).fetchdf()
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"query error: {e}") from None
    _log({"tool": "arena_query", "sql": sql, "rows": int(len(df)), "seconds": round(time.time() - t0, 3)})
    return _frame_text(df)


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


@server.tool("arena_eval", "Run Python (pandas/numpy) over the tables: `tables['trips']` etc. are DataFrames; assign `result` or print. 60 s cap, no I/O.",
             {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]})
def arena_eval(code: str) -> str:
    from arena.engine.sandbox import SAFE_BUILTINS, _guarded_import, check_source
    errs = check_source(code)
    if errs:
        raise ToolError("not allowed: " + "; ".join(errs))

    class _Tables(dict):
        def __missing__(self, k):
            self[k] = _table(k)
            return self[k]

        def keys(self):
            return list(META["tables"])

    ns = {"__builtins__": {**SAFE_BUILTINS, "__import__": _guarded_import, "__build_class__": __builtins__["__build_class__"] if isinstance(__builtins__, dict) else __builtins__.__build_class__, "__name__": "arena_eval"},
          "tables": _Tables(), "pd": pd, "np": np, "now": dict(CFG["now"])}
    buf = io.StringIO()
    t0 = time.time()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(EVAL_TIMEOUT)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<arena_eval>", "exec"), ns)
    except _Timeout:
        raise ToolError(f"timed out after {EVAL_TIMEOUT}s") from None
    except Exception as e:  # noqa: BLE001
        _log({"tool": "arena_eval", "code": code, "error": repr(e)})
        raise ToolError(f"{type(e).__name__}: {e}") from None
    finally:
        signal.alarm(0)
    out = buf.getvalue()
    res = ns.get("result")
    if isinstance(res, pd.Series):
        res = res.to_frame()
    if isinstance(res, pd.DataFrame):
        if not isinstance(res.index, pd.RangeIndex):
            res = res.reset_index()   # keep group keys visible
        out += _frame_text(res)
    elif res is not None:
        out += str(res)
    _log({"tool": "arena_eval", "code": code, "seconds": round(time.time() - t0, 3), "chars": len(out)})
    return out[:MAX_CHARS] + ("\n... truncated" if len(out) > MAX_CHARS else "") if out else "(no output; assign `result` or print)"


# ------------------------------------------------------------------ forum
def _forum_posts() -> list[dict]:
    p = Path(CFG["forum_path"])
    if not p.exists():
        return []
    posts = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return [x for x in posts if x.get("t", 0) <= CFG["now"]["t"]]


if CFG.get("forum"):
    @server.tool("forum_read", "Read the forum (newest last). `limit` = how many of the latest posts (default 50); `agent` filters by author.",
                 {"type": "object", "properties": {"limit": {"type": "integer"}, "agent": {"type": "string"}}})
    def forum_read(limit: int = 50, agent: str | None = None) -> str:
        posts = _forum_posts()
        if agent:
            posts = [p for p in posts if p["agent"] == agent]
        posts = posts[-int(limit):] if limit else posts
        if not posts:
            return "(no posts yet)"
        return "\n\n".join(f"[{p['post_id']}] {p['agent']} — season {p['season']} day {p['doy']} {p['hour']:02d}:00"
                           f"{' (rank ' + str(p['rank_at_post']) + ' at post)' if p.get('rank_at_post') else ''}\n{p['text']}" for p in posts)

    @server.tool("forum_post", "Post to the forum (≤ 300 words, at most 2 posts per month, attributed to you). Optional.",
                 {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]})
    def forum_post(text: str) -> str:
        text = text.strip()
        words = len(text.split())
        if words == 0:
            raise ToolError("empty post")
        if words > 300:
            raise ToolError(f"{words} words; the limit is 300")
        pending = TURN_DIR / "posts.jsonl"
        n_pending = sum(1 for _ in open(pending)) if pending.exists() else 0
        if n_pending >= int(CFG.get("forum_quota_left", 0)):
            raise ToolError(f"quota: {CFG.get('forum_quota_left', 0)} post(s) left this month, already used in this turn")
        with open(pending, "a") as f:
            f.write(json.dumps({"agent": CFG["agent"], "text": text}) + "\n")
        return f"posted ({n_pending + 1} of {CFG.get('forum_quota_left', 0)} allowed this turn). It becomes visible to others after this turn."


# ------------------------------------------------------------------ strategy
@server.tool("submit_strategy",
             "Submit a new strategy.py. It is checked (allowed imports, describe() ≤ 200 words, no calendar years or season-specific constants, runs without error on past ticks, no lookahead) and adopted after this turn if it passes; otherwise the reason is returned. `adopted_from`: forum post ids you drew on, if any. `summary`: one line on what changed.",
             {"type": "object", "properties": {"code": {"type": "string"}, "summary": {"type": "string"},
                                               "adopted_from": {"type": "array", "items": {"type": "string"}}},
              "required": ["code", "summary"]})
def submit_strategy(code: str, summary: str, adopted_from: list[str] | None = None) -> str:
    from arena.engine.validate import validate_strategy
    report = validate_strategy(code, SNAP, CFG)
    _log({"tool": "submit_strategy", "ok": report["ok"], "reason": report.get("reason"), "summary": summary, "adopted_from": adopted_from or []})
    if not report["ok"]:
        raise ToolError("rejected: " + report["reason"] + ("\n" + "\n".join(report.get("details", [])) if report.get("details") else ""))
    (TURN_DIR / "strategy_submitted.py").write_text(code)
    (TURN_DIR / "submission.json").write_text(json.dumps({"summary": summary, "adopted_from": adopted_from or [],
                                                          "describe": report["describe"], "warnings": report.get("warnings", [])}))
    return "accepted; it takes effect after this turn. describe(): " + report["describe"] + \
        ("\nwarnings: " + "; ".join(report["warnings"]) if report.get("warnings") else "")


@server.tool("write_notes", "Replace your private notes.md with this text (you can also edit the file directly).",
             {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]})
def write_notes(text: str) -> str:
    (SANDBOX / "notes.md").write_text(text)
    return f"notes.md written ({len(text.split())} words)"


if __name__ == "__main__":
    server.serve()
