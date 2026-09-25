# Arena

Multi-agent yellowtail day-picking competition on top of this repo's point-in-time data layer.
Read `SPEC.md` (operator). Agents read `RULES.md` only (Phase 3).

## Status

| Phase (SPEC §11) | State |
|---|---|
| 0 Preflight, `events.py` changes (D-050, D-051), PIT suite extended, Goal 1 specs re-logged | done |
| 1 `state.json` schema (`engine/state.py`) + dashboard on fixtures, published as an artifact | done |
| 2 Engine core, scripted baselines, isolated arm end-to-end on seasons ≤ 2023, `tests/` | done |
| 3 Turn machinery (headless runner, MCP tools, `RULES.md`, personas, forum) | built; forum-arm smoke run done (see D-054) |
| 4 Adversaries, poisoned arm, metrics, grader | not started |
| 5 Owner's agent, sealed holdout run | not started |

## Run

```bash
pip install -r requirements.txt
export YT_SOURCE_REPO=/path/to/Daily-Fishing-Prediction
python3 -m arena.tools.preflight                     # coverage + source date semantics -> arena/preflight.md
python3 -m arena.run --arm isolated --replicate 1    # pauses at every season end
python3 -m arena.run --resume <run id>               # continue after the owner's word
python3 -m arena.run --dev --seasons 2012-2013 --no-pause   # development: uncommitted code, no pauses
python3 -m arena.tests.test_pit_arena --run arena/runs/<id> # no-lookahead proof for every strategy of a run
python3 -m pytest -q arena/tests                     # unit tests (calendar, scoring, sandbox, PIT, MCP server)
python3 -m arena.tools.seed_agents                   # create arena/agents/<name>/ from field.roster (once)
python3 -m arena.run --config arena/configs/smoke.yaml --arm forum --dev --no-pause   # 3 LLM agents, 1 season
ARENA_CANARY=1 python3 -m pytest -q arena/tests/test_canary.py   # real turn: forbidden paths must be denied
```

## LLM turns (Phase 3)

At 21:00 on the 1st and 15th (`turn_days`), at season start and at season end, every LLM agent
gets one headless Claude Code process (`arena/turns.py`): cwd = a per-turn sandbox with
`RULES.md`, `persona.md`, `strategy.py`, `notes.md`, `results.json`, `leaderboard.json`,
`forum_new.json`; tools = Read/Write/Edit inside the sandbox plus the arena MCP server
(`arena/mcp_server.py`: `describe_tables`, `arena_query` (DuckDB), `arena_eval` (pandas),
`forum_read` / `forum_post` (only with forum access), `submit_strategy`, `write_notes`), bound to
a parquet snapshot cut at `available_at <= now`. No Bash, no web, no reads outside the sandbox
(`arena/claude/turn-settings.template.json`). `submit_strategy` validates (allowlist, calendar
audit, `describe()` ≤ 200 words, runs and no-lookahead check on past ticks); an accepted strategy
replaces the agent's `strategy.py` after the turn and its worker restarts. Posts, notes, queries
and cost are logged per turn under `runs/<id>/turns/<tag>/<agent>/` and in `turns.jsonl`.
Models per agent come from `field.roster` (`field.models` maps haiku/sonnet/opus to model ids).

Cost: a turn costs roughly $0.02–0.10 on Haiku, $0.10–0.40 on Sonnet and $0.30–1.00 on Opus
(capped by `turns.budget_usd`). With 30 agents, two turns a month and 14 seasons, one run is
about 10,900 turns; the three arms with three replicates each are nine runs.

A run writes `arena/runs/<ts>_<arm>_r<k>/`: `manifest.json`, `config.yaml`, `decisions.jsonl`,
`outcomes.jsonl`, `forum.jsonl`, `agents/<name>/strategy_v*.py`, `results/season_<year>.json`,
`results/metrics.json`, `live/state.json` (dashboard contract, schema 1), `checkpoint.json`
(resume), `tables/` (masked parquet snapshot the strategy workers read; git-ignored).
Seasons ≥ 2024 are refused without `--holdout` (D-033; SPEC §12 #1).

## Booking rules in force (D-055)

Agents book a **named boat** (`Book(offer_id, reason, boat=...)`); the score is that boat's own
count, diluted by other agents on the same boat. The **sailing schedule** (`schedule` table: boat,
landing, class, fishing date; no counts) is public 14 days ahead; a booking on an unscheduled boat
is rejected at booking time. `booking_unit: class` in the config restores pooled, class-level booking.

## Run isolation

Every LLM turn runs with a fresh, empty `CLAUDE_CONFIG_DIR` and a sandbox outside the repository
(`../arena-sandboxes/<run>/…`, deleted after the batch), so nothing (memory, sessions, settings,
files) carries between agents, turns or runs. A run only ever edits its own copies under
`arena/runs/<id>/agents/`; the seeds in `arena/agents/` stay as committed.

## Dashboard

`dashboard/index.html` is a single file. Open it next to a `state.json`, or pass
`?src=<path or URL>`; it polls every 30 s. The published artifact reads its own `state.json`
copy (republished by the session driving the run) or an artifact-db document `state/current`.
Fixture: `python3 -m arena.dashboard.fixtures.make_sample`. The agent inspector (click a
leaderboard row) lists every trip with boat, the agent's reason, the boat's count and the share;
every LLM turn with the strategy change it made; and per-season / cumulative tables.
