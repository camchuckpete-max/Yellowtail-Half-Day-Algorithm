# Plan / loop state

Goals are worked **strictly in order** (user instruction, D-018): Goal 2 starts
only after Goal 1 is met on dev and confirmed on holdout; Goal 3 only after Goal 2.

## Current focus: Goal 1

Target: pooled dev MCC ≥ best baseline + 0.05 (B1 = 0.611 → ≥ 0.661) with the
bootstrap CI of the difference above 0; then one holdout confirmation, then the
same check under `--strict` timing.

### Done
- Iter 0/1: infrastructure, PIT test, logistic / boosting on all features. Best dev MCC 0.587 (e003, threshold 0.4). Ranking beats B1 (AUC 0.88 vs B1's ≈0.78) but the hard call doesn't.
- Diagnosis: the cases where B1 is wrong are near 50/50 on catch-history features alone (e.g. D-1 had exactly 1 yellowtail → 49% next day).

### Next
1. Iter 2: D-1 AM/PM split, per-landing and per-boat recency, interaction terms, C and threshold sweep (exploratory; results in `sweeps/`).
2. Register the best 1–3 configurations as specs and run them (saved).
3. If still short: the constraint is information, not model class. Candidates:
   - more half-day history (source backfill 2016–2026 in progress; re-check `git log` of the source each iteration),
   - FishDope reports for R ≤ D-2 with last-modified ≤ cutoff (usable from mid-2013; D-006),
   - SST (2020+) once half-day history for those years loads.
4. When source data changes: rebuild dataset (automatic via hash), re-run registered specs.

## Stop conditions
- All three goals met and documented, or
- Goal 1 demonstrably not achievable with the data available and no more data arriving (report honestly).

## Update after iteration 5
- Parallel round (agents A/B/C) + monthly refit sweep: best dev (2012–2014) 0.655, but on fresh 2015–2016 all finalists are within noise of B1 (D-025–D-027).
- Remaining levers: (1) more years of half-day history as the source backfill loads (re-run finalists each time the source changes; dev grows only by a logged decision made before looking); (2) SST/chlorophyll once 2020+ half-day years load; (3) a different Goal 1 criterion — only if the user decides (e.g. probability quality), never changed unilaterally.

# Goal C — conditions only (user, 2026-09-24)
Predict at 21:00 PT D-1 whether any SD half-day boat catches ≥1 yellowtail on D using **no fish
counts and no FishDope-derived inputs**; only conditions (calendar/season, moon, tides, NWS
forecasts, marine zone forecasts, later SST/chlorophyll/currents/buoys). Purpose: isolate how
much the environment alone explains. Loop until results stop improving.

- Label, evaluation days, dev folds (2012–2016), holdout (≥ 2017) and metrics are the same as
  Goal 1, so numbers are directly comparable.
- Benchmarks: **S0 season-only** model (day-of-year harmonics) — the honest bar for "do
  conditions add anything"; and B1 for reference (B1 uses catch data, so it is not a fair rival).
- Enforcement: specs set `inputs="conditions"`; `features.assert_conditions_only` rejects any
  feature from landing_counts or FishDope (tested in tests/test_pit.py).
- Tracks: (1) 2010–2016 forecasts/tides/moon history features now; (2) SST/chlorophyll/currents/
  buoys once 2020+ half-day counts load (source backfill in progress).
