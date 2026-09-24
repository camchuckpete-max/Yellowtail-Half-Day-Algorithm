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

## D-B01 Extra species columns in trips (agent B, 2026-09-23)
`events.load_trips` also carries mackerel, sand_bass, halibut, white_seabass, sheephead and
whitefish counts per trip (kept + released), for D-1 species-mix context. All added to the
poison list in `tests/test_pit.py`.

## D-B02 Boat/fleet catch-history features (agent B)
`features._fleet_features`, reading only the visible prefix: boat state over D-3..D-1
(`bt_hot_last` = boats whose latest visible half-day trip had yt; `bt_hot_any3`;
`bt_hot_sailed_d1` = hot boats that also reported a D-1 trip, a proxy for sailing D),
flags for the four main boats, D-1 yt trips/boats, D-2 twilight yt, same-weekday trip count
over 4 weeks (proxy for trips on D), D-1 species mix (per-trip bonito/barracuda/calico/
mackerel/..., surface-species fraction, bottom-only fraction), 3/4-day yt trip fraction over
3/7/30 days and trend, overnight yt, half-day yt-day EWM (half-life 2 d), 60-day yt-day rate.
EDA that motivated the choice was run on 2010–2014 (dev years included), so the feature
choice itself carries some dev selection.

## D-B03 Model types (agent B)
`Model` gains `logreg_split` (separate logistic for B1=1 / B1=0 days, pooled fallback if a
regime has one class), `ens` (mean of logistic and HGB), `avg_subsets` (mean of logistic fits on
named feature subsets) and optional HGB monotone constraints (`extra["monotone"]`).
None beat a single L2 logistic: with ≤3 training years the extra flexibility costs more
variance than it removes bias (sweeps B2, B4, B5).

## D-B04 Threshold rule `mcc_range:lo:hi` (agent B)
Max inner-OOF MCC restricted to thresholds in [lo, hi] (0.01 grid), so a degenerate inner
year (2011, 6.7% base rate, D-012) cannot push the threshold to an extreme. Training window only.

## D-B05 Agent B result (Goal 1, catch-history direction)
50 sweep configurations + 4 finalist runs (dev + strict) = 54 of 60. The new features improve
probability quality (best Brier 0.1146 vs 0.1197 for e005, AUC 0.897 vs 0.893) but not the hard
call: best catch-history-only dev MCC 0.645 (eB01), best with FishDope 0.653 (eB02); target 0.661
not reached. Root cause observed: probabilities are under-calibrated in hot test years (2012) because
the frozen model is trained on cold years, and B1=0 days rarely get above ~0.4, so the yes/no call
stays close to B1.

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

## D-024 Fix: D-017 was breached (found by agent C)
`_ALL_V1`/`_ALL_V2` were derived from the live `FEATURES` list, so specs e001/e002/e004
silently grew from 41 features (as run and logged) to 71 as features were added.
`_ALL_V1` is now a literal 41-name list (asserted), matching the saved
`runs/*e001*/config.json`; `_ALL_V2` was unused and is removed. No logged result
changes (all runs saved their exact feature lists in config.json).

## D-025 Parallel round 1 outcome (agents A, B, C)
None reached Goal 1 (dev MCC: A 0.642, B 0.653, C 0.651; e007 0.655; target 0.661).
All three branches are pushed as `agent/*` for audit. B (fleet features, model types,
`mcc_range` threshold rule) and C (FishDope water temperature and bait, NWS zone
PZZ750 forecast with issue-time PIT) are merged into main because both showed
real but sub-threshold signal; A's extractor is not merged (no measurable gain;
code and sweeps remain on its branch). After the merge, PIT tests pass and e005,
e007 and eB01 reproduce their prior dev MCC exactly.
Convergent diagnosis (B and C independently): the per-year frozen model is trained
on low-rate years (2011: 6.7%), so it under-predicts in hot years (2012 B1=no days
scored 0.20–0.35 were 56% positive; e007 mean dev residual ≈ +0.05). Signals such as
water temperature shift probabilities but rarely across the call threshold.
Next: retraining cadence (monthly walk-forward) and recency-weighted training.

## D-027 Dev years extended to 2012–2016; holdout moves to ≥ 2017-01-01
Source commit b09f41f added full 2015 and 2016 half-day history (345 + 346 days) and
102 days of 2017. The holdout (≥ 2015-01-01) had never been accessed
(`holdout_access.log` empty; no sweep or agent evaluated a date ≥ 2015-01-01).
Before any run touches 2015–2016, the split is redefined: dev folds 2012–2016,
holdout = every day ≥ 2017-01-01 (grows as the backfill continues). Rationale: two
more training years address the "too little, too cold training data" diagnosis
(D-025), and 2015–2016 are genuinely fresh test years for everything found on
2012–2014. Earlier logged results were on dev 2012–2014; each run's `config.json`
records its dev years. The D-009 bar is unchanged (pooled dev MCC ≥ best
baseline + 0.05, bootstrap CI > 0), now over 2012–2016.

## D-026 Refit cadence and recency weighting (protocol option, not a protocol change)
`Spec.retrain = "month"` refits the model at the start of each calendar month inside
a test fold, on days < month start − 1 day; `Spec.halflife_days > 0` weights training
rows by 0.5^(age/half-life). The decision threshold is still chosen once per fold
from data before the fold. Default (`year`, no weighting) reproduces all earlier
runs exactly (e007 verified). Sweep 4 (36 configs, dev 2012–2014): monthly refit
improves calibration (Brier e007 0.1196 → 0.1153; eB01 0.1125) but not MCC; best
MCC stays e007 yearly 0.655. Recency weighting did not help.

## D-028 Parallel round 2 (user: "keep trying more ways" with existing data)
Same rules as D-023 (own worktree/branch, ≤ 60 dev configurations each, every sweep
committed, no push, never touch holdout ≥ 2017-01-01, PIT tests must pass). All three
agents read the source through a pinned snapshot, `/home/user/dfp-pinned` = source
commit 7121831, so results are comparable while the backfill continues; e005
reproduces (0.624) on it. Dev = 2012–2016 (D-027). Directions:
- D: FishDope bait-barge change-log (`forage_observations`, category `bait_barge`).
- E: trip-level modelling — predict P(yellowtail | boat-trip) on ~15× more rows and
  aggregate to the day with a separate model of which trips sail; separates effort from bite.
- F: latent-state ("fish are local") sequence models, e.g. HMM / Bayesian filtering over
  partial daily evidence, and regime-dependent decision rules chosen on training data only.

## D-D01 FishDope bait-barge change-log admitted (agent D, 2026-09-24)
Added dump `forage_observations.sql.gz` (source commit 7121831); only rows with category `bait_barge` and
source `fishdope` are read (`events.load_bait_barge`). Every row's `source_ref` starts with
`fishdope_reports:<id>|bait_report|`; the row gets exactly that report's D-020 `available_at` (ET stamp -> PT,
19:00 PT when unstamped, non-migration edits delay it). Rows are dropped if the reference is missing (0),
the report was rejected by the D-020 guards (4 rows), the report is unknown (0), or observed_date != report
date (0): 20,168 of 20,172 kept. The "(as of M-D)" stamp is only kept as a staleness lag (report day - stamp,
>= 0); it is never a time. 1,122 stamps are implausible (> 60 d stale or later than the report; almost all 2023
stale Ventura/CISCOS stamps, found while checking the stamp logic on detail strings only, no labels); their lag is
NaN. In the dev period the only forward stamps (2016-01-16 report 3888, stamps "1-17") belong to a report whose
availability D-020 already moves to its 2016-01-17 edit. Coverage: 2009 (5 rows), then 2013-09 onward.
Features (`fo_*`): last known status per (barge, species) in D-14..D-1, local (San Diego + Mission Bay) sardine,
regional sardine fraction, regional squid, local outage in D-3..D-1. Poisoned/truncated in tests/test_pit.py
(future rows are also relabelled as San Diego), plus a guard that every row's availability equals its report's.

## D-D02 Bait-barge lines parsed from the report text as well (agent D)
The change-log is lossy: 1,059 of 2,854 "stocked" local (SD/MB) states in the report text have no change-log row
for that report, and on all 608 SD/MB lines listing both sardine and anchovy the anchovy size equals the sardine
size (size copied across species). Where it has a row it agrees with the text 1,895/1,913. So the same reports'
`bait_report` section is also parsed directly (`events.bait_barge_report`, columns `bb_*` of the D-020 report
rows; same availability and leak guards, poisoned in the PIT test): per barge segment, stocked species
(negations "NO sardine", "no sardine or mackerel" handled), outage, limited supply, largest sardine size, stamp lag.
Hand check of 40 random SD/MB lines (sweeps/D_linkage_output.txt): species correct 40/40, size missing on 2
"mix" lines. Full audit: sweeps/D_linkage.py.

## D-D03 Encoding and dev selection (agent D)
Bait data exist from 2013-09 only, so the 2012 and 2013 folds are unaffected (feature constant in training) and
the 2014 fold's yearly model sees about 4 months of bait days. Known states are +-1 and unknown 0 (not median
imputation) so pre-2013 days are neutral; `bb_have`/`fo_loc_nrows_7` are built but not used in specs because
missing bait reports coincide with the 2014 summer (B1=1, bait unknown: 98% positive). EDA on dev 2014-2016
(sweeps/D_eda1_output.txt) was run before the sweeps: selection on dev, disclosed.

## D-D04 Result: bait-barge state adds no hard-call skill (agent D)
20 sweep configurations (D_sweep1: 12, D_sweep2: 8) + 2 finalist runs (dev with bootstrap, strict) = 22.
Controls reproduce eB01 0.626 and e009 0.627. Best `eD01_e009_bait_p40` 0.631 (folds 0.513/0.470/0.817/0.570/0.502,
AUC 0.889, Brier 0.1244 vs e009 0.893/0.1231), bootstrap MCC - B1 [+0.001, +0.049]; strict 0.571 vs B1 0.525.
Bar 0.656 not reached; +0.004 over its own control is noise, and every bait group lowered AUC or Brier. Why: on
2014-2016 dev days, local sardine present vs absent moves P(y) only 0.14 -> 0.17 when B1=0 and 0.70 -> 0.79 when
B1=1, so no call crosses a threshold. Other forage categories (bait schools, birds, paddies, breezers, foamers)
were not used: zone_id is NULL for all 2009-2016 rows and the local bait-school sentences are the same text that
agent C's `bait_local_*` already count (D-C01, D-C04).
