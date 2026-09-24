# Yellowtail Half-Day Algorithm

Predict, at **9:00 pm PT on day D-1**, whether **at least one San Diego half-day
boat will catch at least one yellowtail on day D**.

| Goal | Definition used here (see DECISIONS.md) | Status |
|---|---|---|
| 1 | Beat both persistence baselines (B1 "yesterday had yt", B2 "any yt in last 7 days") by a noticeable margin: pooled dev MCC ≥ best baseline + 0.05 **and** 95% block-bootstrap CI of the MCC difference above 0, confirmed on the untouched holdout | see STATUS.md |
| 2 | Fewest-feature model whose dev MCC ≥ the Goal 1 best (and is confirmed on holdout) | see STATUS.md |
| 3 | Breakout calls (predict yes when no half-day yt was visible in D-7..D-1) with precision ≥ 40%, at least 10 calls, reported with Wilson 95% CI | see STATUS.md |

## Arena

Multi-agent day-picking competition built on this data layer: `arena/SPEC.md` (D-049).

## Data (read-only)

Only source: [`camchuckpete-max/Daily-Fishing-Prediction`](https://github.com/camchuckpete-max/Daily-Fishing-Prediction),
`db_dump/landing_counts.sql.gz` and `db_dump/conditions_daily.sql.gz`. Every run
records the source commit and the SHA-256 of each dump file it read
(`runs/<id>/data_manifest.json`).

## No-lookahead guarantees

1. Every observation carries `available_at` (PT). Half-day AM counts are public
   at 14:00, PM 19:00, 3/4-day 19:30, overnight 19:00 and 1.5-day 06:00 on return day
   (D-050/D-051); twilight, full-day and 2-day+ trips are treated as not public until the next day.
   NWS forecasts use their actual issue time.
2. Features for D read only `events[available_at <= D-1 21:00]` (`yt/features.py::_visible`),
   and `build()` asserts that the newest input used is ≤ the cutoff.
3. `tests/test_pit.py` poisons (random values) and separately deletes every
   post-cutoff event and checks features are bit-identical; also checks that
   no trip fished on/after D is ever visible and that D-1 twilight is hidden.
4. Walk-forward: a model scoring year Y is trained only on target days
   < (first day of Y) − 1, so all its training labels were known before its first
   prediction. Thresholds are chosen on inner walk-forward folds inside the
   training window.
5. Holdout (all days ≥ 2024-01-01 per D-033; earlier boundaries 2015 → 2017 → 2024, never accessed) is scored only with `--holdout`; every access
   is appended to `holdout_access.log`.
6. `--strict` re-runs everything with nothing from D-1 visible, as a robustness check.

## Audit trail

| File | Contents |
|---|---|
| `DECISIONS.md` | Every judgment call, numbered, with reasons |
| `LOG.md` | One line per saved run (dev or holdout) |
| `runs/<id>/config.json` | Exact spec (features, model, threshold rule) |
| `runs/<id>/data_manifest.json` | Source commit, dump hashes, dataset hash, algorithm commit |
| `runs/<id>/weights.json` | Per fold: training window, threshold + how it was picked, all weights, scaler, imputation values |
| `runs/<id>/inputs.csv.gz` | Every feature value fed to the model per day, the cutoff, the newest input timestamp used |
| `runs/<id>/predictions.csv` | Per day: probability, call, truth, baseline inputs |
| `runs/<id>/metrics.json` | Model vs baselines, bootstrap CI, breakout stats |
| `holdout_access.log` | Every holdout evaluation |
| `archive/` | Runs produced before the code was committed (not reproducible by commit; kept for transparency) |

Runs cannot be saved from uncommitted code (`evaluate.write_run` refuses).

## Reproduce

```bash
pip install pandas numpy scikit-learn
export YT_SOURCE_REPO=/path/to/Daily-Fishing-Prediction   # checkout the commit in data_manifest.json
python3 tests/test_pit.py
python3 -m yt.run <experiment-name>            # dev folds 2012-2023 (D-033)
python3 -m yt.run <experiment-name> --holdout  # holdout (logged)
```
