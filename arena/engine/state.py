"""`live/state.json` — the only contract between the engine and the dashboard (SPEC §9).

Schema 1. Everything agent-facing uses masked dates (season index, doy) when `mask_years` is on;
the operator-only fields (`calendar_year`, `adversary`) are dropped from the agent-facing copy
by the turn machinery, never by the dashboard.

{
  "schema": 1,
  "run": {id, arm, replicate, status ("running" | "paused_season_end" | "finished" | "error"),
          source_commit, arena_commit, config_hash, started_at, updated_at,
          sim: {season, calendar_year|null, doy, date_masked ("S03 d201"), tick ("16:00"|"21:00"),
                season_start_doy, season_end_doy, days_in_season},
          turns_in_progress: [agent, ...], seasons_done: int, seasons_total: int,
          warmup_seasons: int, paused_reason: str|null},
  "agents": [ {name, kind ("llm"|"baseline"|"adversary"|"owner"), persona, model,
               forum: bool (false = this agent neither reads nor posts, D-053),
               adversary: str|null (operator-only label),
               describe: str, strategy_version: int, last_strategy_change: {season, doy, summary, diff_path}|null,
               last_turn: {season, doy, queries: int, posts: int, adopted_from: [post_id, ...]}|null,
               season: {fish, undiluted, excess, skunk_rate, trips, trips_by_class: {cls: n},
                        budget_left, pto_left, pto_used, usd_per_fish, rank},
               cumulative: {fish, undiluted, excess, seasons_counted, rank},
               history: [ {season, fish, undiluted, excess, rank, counted: bool}, ... ],
               last_reasons: [ {season, doy, tick, action, text, valid: bool, reason_rejected: str|null}, ... ],
               trips: [ {season, doy, dep_doy, cls, boat, cost, pto, reason, ran, yt, anglers, competitors, share,
                         pooled_share, strategy_version, booked_at}, ... ],          # every settled trip, all seasons
               turns: [ {season, doy, tag, season_end, queries, posts, submitted, adopted, version, change_summary,
                         describe, summary, cost_usd, ok, error}, ... ],             # every LLM turn
               journal: [str, ...], judgment: {calls, cost_usd},                     # nightly decisions (D-058); trips[].via = "judgment"|"code"
               strip: [ {doy, pto: bool, cls: str|null, outcome: "fish"|"skunk"|"cancelled"|"pending"|null,
                         share: float|null, n_agents: int|null}, ... ]      # this season, sparse: only days with an action
             }, ... ],
  "leaderboard": {season: [name, ...], cumulative: [name, ...]},           # ranked, best first
  "forum": {enabled: bool, n_total: int, path: "forum.jsonl",
            posts: [ {post_id, season, doy, hour, agent, text, rank_at_post: int|null,
                      adversary: str|null, cited_by: [agent, ...]}, ... ]},   # last 200, newest first
  "field": {diversity_jaccard: float|null, herding: float|null,
            by_season: [ {season, mean_fish, diversity_jaccard, herding, counted: bool}, ... ]},
  "outcomes_recent": [ {season, doy, cls, ran: bool, yt: int, anglers: int, n_agents: int, share: float}, ... ]
}
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 1
FORUM_INLINE_POSTS = 200


def masked_date(season: int, doy: int) -> str:
    return f"S{season:02d} d{doy:03d}"


def write_atomic(path: Path, state: dict) -> None:
    """Write state.json atomically so a dashboard poll never sees a partial file."""
    state = dict(state)
    state["schema"] = SCHEMA
    state.setdefault("run", {})["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".state.", suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(state, f, separators=(",", ":"), default=_default)
    os.replace(tmp, path)


def _default(o):
    if hasattr(o, "isoformat"):
        return o.isoformat()
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(f"not JSON serialisable: {type(o)}")


def validate(state: dict) -> list[str]:
    """Cheap structural check used by tests and by the dashboard fixture build."""
    errs = []
    if state.get("schema") != SCHEMA:
        errs.append("schema")
    run = state.get("run", {})
    for k in ("id", "arm", "replicate", "status", "sim"):
        if k not in run:
            errs.append(f"run.{k}")
    if run.get("status") not in ("running", "paused_season_end", "finished", "error"):
        errs.append("run.status")
    for a in state.get("agents", []):
        for k in ("name", "kind", "season", "cumulative", "history", "strip"):
            if k not in a:
                errs.append(f"agent {a.get('name')}.{k}")
    for k in ("leaderboard", "forum", "field"):
        if k not in state:
            errs.append(k)
    return errs
