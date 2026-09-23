# Decisions

Numbered, append-only. Each entry: what, why, and what would change it.

## D-001 Label definition (2026-09-23)
Day D is **positive** if any per-boat half-day *fishing* trip (`1/2 Day AM`, `PM`,
`Twilight`, `1/2 Day`, `1/2 Day Trip`) from the San Diego landings, fished on D,
reports ≥1 yellowtail kept **or released**. Hoop-net/lobster half days are
excluded (not hook-and-line). Days with no half-day fishing trip reported are
**not evaluable** (no row), never counted as negatives.

## D-002 Landings
seaforth, fishermans, hm, point_loma. `oceanside` only appears in 2026 (3 rows);
including it would change the label definition mid-series. Revisit if its history is backfilled.

## D-003 Publication-time assumptions (landing counts)
The source only has the return date, not a post time, so the time a count
became public is assumed per trip class (`yt/events.py::PUBLISH_TIME`):
AM half-day 14:00, PM/unspecified half-day 19:00, 3/4-day 19:30, overnight 12:00
on return day. Twilight, hoop-net, full-day and 1.5-day+ trips: not visible until
00:00 the next day (return times too close to or after 21:00). This is the
**main** timing mode. `--strict` makes nothing from D-1 visible; any claimed win
must also be checked in strict mode.

## D-004 Baselines use the same information set
B1 "yesterday" = any yellowtail on D-1 among trips public at 21:00 D-1 (so D-1
twilight is not part of it). B2 = any half-day yellowtail on D-7..D-1 (visible).
Both baselines therefore have exactly the information the model has.

## D-005 Forecasts
`conditions_daily`, zone `t_sd_coast`, NWS forecast rows only, stamped with the
`issue_utc` in their `vintage`. Rows without a provable issue time are dropped.
Observed 2010–2015 issue times are ≈15:00 PT D-1 (latest 19:30), all before the cutoff.

## D-006 FishDope narrative excluded (for now)
FishDope daily reports are published ~21:00–22:30 PT on the report date (after
our cutoff for D-1's report), and 2010–2012 reports carry `updated_at` stamps
months later (e.g. a 2012-08-12 report updated 2013-08-26), so the text we have
is not provably what was public at the cutoff. Rule if re-admitted: report for
date R may be used for D only if R ≤ D-2 **and** its last-modified time ≤ the
D-1 21:00 cutoff. Under that rule only ≈mid-2013 onward is usable — too little
overlap with 2010–2015 landing data today. Revisit when more landing years load.

## D-007 Excluded tables
SST / chlorophyll / tides in `conditions_daily` start 2020+; NDBC buoys start 2022;
no overlap with current half-day history (2010-04 → 2015-06). Month-archive
`daily_aggregate` landing rows are excluded (whole-landing totals, and their
species_json concatenates several days — a source parsing bug, not ours to fix).

## D-008 Primary metric: MCC of the daily yes/no call
Classes are imbalanced (≈26% positive), so accuracy rewards always saying "no".
Matthews correlation coefficient is symmetric and imbalance-robust, and applies
to the baselines' hard calls. AUC/Brier/accuracy/precision/recall also reported.

## D-009 "Noticeably better" (Goal 1)
Pooled dev MCC ≥ best baseline MCC + 0.05 **and** the 95% moving-block bootstrap
(14-day blocks, 2000 reps) CI of MCC(model) − MCC(best baseline) lies above 0,
then confirmed on the holdout.

## D-010 Evaluation protocol
Dev folds = test years 2012, 2013, 2014 (2010–2011 are training-only so every fold
has ≥1 inner validation year). Training rows for a fold end ≥2 days before its
first test day. Holdout = all days ≥ 2015-01-01 (incl. 2026 days as they load).
Days are scored only if ≥5 of the previous 7 days had visible half-day reports
(PIT-computable data-completeness filter; removes 19 days, mostly isolated 2019–2026 days).
First 30 days of data are history only.

## D-011 Transform for linear models (debugging finding)
2014 had a bonito explosion: per-trip bonito reached ~400× its 2010–2013 maximum
and the logistic model extrapolated to p≈1e-15 (2014 fold AUC 0.18). Fix:
log1p all `*per_trip*` features and clip standardized inputs to ±4. Applied to all
logistic runs from iteration 1 on.

## D-012 Threshold rule is an experiment dimension
Inner-OOF MCC thresholds were unstable (2012 fold's only inner year, 2011, has a
6.7% base rate → threshold 0.98, zero calls). Fixed thresholds (0.5, 0.4) are run
as alternatives; the rule is part of each experiment's spec.

## D-013 Goal 3 definition
A breakout call = a "yes" on a day where no half-day yellowtail was visible for
D-7..D-1. Precision = hits / breakout calls. Success requires precision ≥ 0.40
with ≥10 calls in the evaluated period (fewer is anecdotal); the Wilson 95% lower
bound is reported alongside. Dev base rate among eligible days: 43/793 = 5.4%.

## D-014 Runs require committed code
`write_run` refuses to save from a dirty `yt/` or `tests/`. The first ten runs
(made before the first commit) are in `archive/iter0_uncommitted_code/` and are
re-run from committed code.

## D-015 Goal 3 breakout window changed to 3 days (user decision, 2026-09-23)
Supersedes the window in D-013. A breakout-eligible day is one with **no
half-day yellowtail visible in D-3..D-1** at the 21:00 D-1 cutoff (`hd_ytdays_3 == 0`).
Because D-1 twilight is not public at 21:00, the window in practice covers D-3 and
D-2 fully and D-1's AM/PM trips. Other D-013 criteria (precision ≥ 0.40, ≥10 calls,
Wilson lo95 reported) unchanged. Dev: 1041 eligible days, 72 positive (6.9%).
Runs logged before this change report breakouts under the 7-day window; they are
marked in LOG.md and all specs are re-run.

## D-016 Baseline B1 = most recent visible day
B1 is now "yellowtail on the most recent day that has any public half-day report"
(`hd_yt_lastday`). In main timing that is D-1 on 1605/1652 dev days (D-2 on 45,
D-3 on 2 when D-1 had no public AM/PM trip). Previously B1 was D-1 only, which
under `--strict` was always "no" (MCC 0, meaningless). The change can only make
the baseline equal or stronger; it differs from the old B1 on 8 dev days.

## D-017 Feature lists are frozen per spec
Specs reference explicit frozen lists (`_ALL_V1`, `_ALL_V2`, ...) rather than the
live `FEATURES`, so adding a feature never silently changes a spec that has run.

## D-018 Goals are worked strictly in order (user instruction, 2026-09-23)
Goal 2 starts only after Goal 1 is met (dev + holdout); Goal 3 only after Goal 2.
`e004_breakout_logreg` was run before this instruction and stays in the log as a
measurement only. Breakout statistics continue to be reported automatically in
every run's metrics, but no spec is tuned for Goal 3 until Goals 1–2 are done.

## D-019 Exploratory sweeps
Wide parameter sweeps (feature set × C × threshold) are run without saving full
run folders, to keep the repo small. Their complete stdout is committed under
`sweeps/` with the script that produced them, so every configuration that was
looked at is visible, not only the ones promoted to named specs. Promoting a
configuration to a spec after seeing its dev score is a form of selection on dev;
the holdout exists to catch that.

## D-020 FishDope reports admitted (user decision, 2026-09-23)
User: reports go live 6–7 pm PT. The data's `published_at` stamps cluster at 9–10 pm,
consistent with **US/Eastern** stamps (21:00 ET = 18:00 PT), so stamps are converted
ET→PT. Reports with no stamp (all of 2010–2012) are assumed public at 19:00 PT on
the report date (the user's upper bound). A report is visible for D only if that
time ≤ 21:00 PT on D-1. Leak guards (rejects listed per build in
`cache/fishdope_rejected_*.csv`; 20 reports at source commit e42bc27):
- title weekday must match the report date's weekday (caught the "2011-02-24" report that is really 2012-02-24 content, per its embedded NWS text);
- no embedded NWS forecast stamp more than 1 day after the report date;
- an edit later than publication delays availability to the edit time, **except** the
  2013-08-26 update shared by 1,429 pre-2013 reports, judged to be a site migration:
  the only later-year references in those reports are regulation dates
  ("closed January 1st 2013") — checked all 20 such passages by hand.
Features: yellowtail mentions (`yellowtail`, `yellows`, `YT`) attributed to regions by
the nearest preceding region keyword: local half-day waters (La Jolla, Point Loma,
Mission Bay, SD Bay, Imperial Beach, Del Mar, PB, OB), Coronados, north county, all.
Crude; no negation handling.

## D-021 Sweep results, iteration 2–3
Best dev MCC 0.640 both with and without FishDope (B1 0.611; target ≥ 0.661).
FishDope does not add measurable skill with these text features. Promoted to
specs e005 (catch history only) and e006 (with FishDope).

## D-022 FishDope: why mention counts failed, sentence-level evidence instead
User asked why FishDope added nothing. Hand review of 12 random "local yellowtail
mention" reports on breakout-eligible days (full output: `sweeps/fd_probe_iter4.txt`):
about half were negations ("No sign of Yellowtail lately", "No Yellowtail … caught
lately"), several were sightings or region misattribution (offshore GPS paddies,
Coronados South Island), and only 3 were private-angler catches in local waters.
Negations and catches were scored identically, so the feature cancelled out
(next-day hit rate 6.6% with a mention vs 7.1% without).
Fix: each sentence containing yellowtail is classified as **neg** (negation word
present), else **catch** (catch verb or "N lb"), else **sight** (seen/puddling/...).
Rule-based, no learned parameters. Result on breakout-eligible dev days: a local catch
in D-3..D-1 → 9.3% vs 6.0%; a local negation on D-1 → 4.6% vs 7.5%. Correct direction,
modest size. Goal 1 sweep best rises 0.640 → 0.655 (target 0.661).

## D-023 Parallel exploration and search accounting (user opted in, 2026-09-23)
Three subagents explore independent directions for Goal 1 at the same time, each in
its own git worktree/branch (`agent/A-*`, `agent/B-*`, `agent/C-*`), never pushing and
never touching the holdout. Each may score at most 60 configurations on the dev
folds and must commit every sweep script + full output under `sweeps/`. The
coordinator reviews, merges selected code into `main`, and re-runs finalists from
`main` so every logged run is reproducible from a main-branch commit.
Search ledger: `sweeps/SEARCH_COUNT.md` counts every configuration scored on dev.
Before this round: 225 (201 in sweeps 1–3, 10 archived iter-0 runs, 14 named-spec runs).
Because the best of many configurations is optimistically biased, the dev bar
(D-009) is necessary but not sufficient: **at most 3 finalists in total** may
ever be scored on the holdout for Goal 1, and Goal 1 is met only if a finalist
also clears the D-009 margin there.

## D-C01 Water temperature and local bait from FishDope text (agent C, 2026-09-23)
No SST/buoy data exists for 2010-2015 in the source, so the only water-temperature signal is what
FishDope reports state. `events.water_temps`: a 50-79 F number with a degree marker (°, degrees, deg,
"F water") in a sentence that mentions water/temp/colour and not air/ATMP/"deg true"; a range a-b
counts as its midpoint. Per report: `wt_all` = median over the whole report, `wt_local` = median over the
local region text (D-020 attribution) after dropping sentences with offshore markers (GPS, bank numbers,
miles, tuna, station tables). `bait_local_*` = non-negated sentences mentioning sardine/squid/anchovy/
mackerel in the local text (includes the SD / Mission Bay bait-barge lines).
PIT: these are columns of the same report rows as D-020 and inherit its `available_at` and leak guards;
read only via the visible prefix; poisoned/truncated in tests/test_pit.py.
Hand check (`sweeps/C_wt_precision_output.txt`, 60 random extractions): value is an observed water
temperature 29/30 (all regions; miss = a hypothetical "once it warms to 61/62") and 30/30 (inshore);
inshore attribution clearly right 16/30, clearly wrong 1/30, not determinable from the sentence 13/30.
Coverage 2010-14 eligible days: wt_all_7 80%, wt_local_7 25%.
`forage_observations` (source='fishdope') is **not** used: every 2009-2015 row maps 1:1 to a
fishdope_reports row (`source_ref` report_id; observed_date == report_date on all 16,917 rows), so it is
PIT-safe via that report's availability, but it was regex-extracted on 2026-09-23 from the same text,
has zone_id NULL for the dev period, and so adds nothing the text does not.

## D-C02 NWS coastal waters forecast, zone PZZ750 (agent C, 2026-09-23)
Added dumps `marine_forecast_products` + `marine_forecasts` (IEM-archived CWFSGX as issued). Zone PZZ750
(San Mateo Pt to Mexican border, 30 nm; the 2005-2019 code). Daytime periods only. `available_at` = the
later of the archive as-issued time (`issue_time_utc`) and the time printed in the product header;
they disagree on 4 of 7,987 2010-14 products (one 2010-11-25 product was archived the next day; one
2011-03-17 archive time is 14 min before its header time). Features for D: the latest product issued
<= D-1 21:00 PT: max wind, gust, seas, offshore-wind flag (E/NE/SE), southerly-wind flag, max southerly
and westerly swell height. The 21:30 PT evening product is therefore never used for the next day.
Small-craft-advisory headlines were not used (validity wording is free text; gust/wind cover it).

## D-C03 Dense centred water temperature (agent C, 2026-09-23)
`wt_c` = mean `wt_all` of the latest <=5 visible reports stating a temperature in D-21..D-1, minus 63 F;
0 when none (`wt_c_local` likewise from `wt_local`). Added after a residual diagnostic on the e007 dev
predictions (`sweeps/C_diag1_output.txt`) showed temperature correlates +0.17 with the residual; that
is selection on dev and is disclosed as such.

## D-C04 Result: environment adds no hard-call skill (agent C, 2026-09-23)
50 configurations (sweeps/C_sweep1..3). Best 0.651 / 0.650 vs e007's 0.655 with the same base features;
every added environmental group lowers AUC or Brier; interactions with `hd_yt_lastday` hurt the 2012
fold (trained on 2010-11 only). Why: warm water raises P(yellowtail) but the cells where B1 is wrong do
not cross the call threshold — B1=yes on cold water is still ~50-56% positive, B1=no on warm water ~20%
(diag1), so flipping calls there does not raise MCC. Nothing promoted to a spec.
Also found: `_ALL_V1`/`_ALL_V2` were built from the live FEATURES list (D-017 breach): e001/e002/e004 were
logged with 41 features but now resolve to 71. Agent C's features are excluded from them; restoring the
original 41 is left to the coordinator.
