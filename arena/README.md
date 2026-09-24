# Arena

Multi-agent yellowtail day-picking competition on top of this repo's point-in-time data layer.
Read `SPEC.md` (operator). Agents read `RULES.md` only (Phase 3).

## Status

| Phase (SPEC §11) | State |
|---|---|
| 0 Preflight, `events.py` changes (D-050, D-051), PIT suite extended, Goal 1 specs re-logged | done |
| 1 `state.json` schema (`engine/state.py`) + dashboard on fixtures, published as an artifact | done |
| 2 Engine core, scripted baselines, isolated arm end-to-end on seasons ≤ 2023, `tests/` | done |
| 3 Turn machinery (headless runner, MCP tools, `RULES.md`, personas, forum) | not started |
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
python3 -m pytest -q arena/tests                     # unit tests (calendar, scoring, sandbox, PIT)
```

A run writes `arena/runs/<ts>_<arm>_r<k>/`: `manifest.json`, `config.yaml`, `decisions.jsonl`,
`outcomes.jsonl`, `forum.jsonl`, `agents/<name>/strategy_v*.py`, `results/season_<year>.json`,
`results/metrics.json`, `live/state.json` (dashboard contract, schema 1), `checkpoint.json`
(resume), `tables/` (masked parquet snapshot the strategy workers read; git-ignored).
Seasons ≥ 2024 are refused without `--holdout` (D-033; SPEC §12 #1).

## Dashboard

`dashboard/index.html` is a single file. Open it next to a `state.json`, or pass
`?src=<path or URL>`; it polls every 30 s. The published artifact reads its own `state.json`
copy (republished by the session driving the run) or an artifact-db document `state/current`.
Fixture: `python3 -m arena.dashboard.fixtures.make_sample`.
