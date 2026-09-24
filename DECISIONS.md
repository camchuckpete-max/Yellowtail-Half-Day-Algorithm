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

## D-029 Predicted tides (user backfilled 2009–2026) and moon check
Source `conditions_daily` rows `noaa_coops_tides` (data_kind `forecast` = NOAA predictions,
identical across zones → one station; daily high/low heights, no times). Predictions are
published a year or more ahead; `available_at` is set conservatively to 30 days before the
date, so D's own predicted tides are visible at the D-1 cutoff. Features: tidal range on D and
D-1, high/low heights, range change. Covered by the poison/truncation test.
Findings (source 8b48084, dev 2012–2016): hit rate is flat across tidal-range quartiles
(B1=0: 11–17%; B1=1: 73–80%); tidal range correlates 0.79 with |cos(moon phase)|
(spring/neap), as expected. Sweep 5 (6 configs incl. 3 controls): adding tides changes dev
MCC by −0.003 to +0.005, AUC unchanged or lower → no effect; not adopted.
Source `astronomical_moon` (2009–2026) matches our computed illumination (corr 1.000,
max abs diff 0.009); no new information.
Note: controls moved slightly vs source 7121831 (B1 0.606 → 0.609; e005 0.624 → 0.623)
because the source backfill re-filled failed 2012–2016 dates. Dev data is still settling.

## D-030 Parallel round 2 outcome (agents D, E, F)
Dev 2012–2016, B1 0.606, target 0.656. Best per agent: D (bait barges) 0.631, E (trip-level
model) 0.632, F (latent state + recalibration) 0.633. All bootstrap CIs are at or near 0;
none survives `--strict` as a meaningful gain; each agent recommends against spending a
holdout scoring. Branches `agent/D-bait-barge`, `agent/E-trip-level`, `agent/F-latent-state`
are pushed for audit; no code merged into main (nothing adopted).
Useful findings kept for later:
- E: a weekly-refit trip-level model is well calibrated across hot and cold years
  (mean predicted vs actual rate per year within 0.02) and matches the best day models on
  probability quality (AUC 0.891, Brier 0.1222). Candidate building block if Goal 1 is ever
  judged on probability quality, and for SST-era models.
- F: ceiling check — even thresholds chosen on dev itself reach only 0.633 (single) and
  0.652–0.658 (one per year). Goal 1 cannot come from the decision layer; it needs
  information that ranks days better.
- D: bait-barge log adds no skill; missing-report indicators are spuriously predictive
  (summer 2014 gap) and are deliberately excluded.
Conclusion: with inputs available for 2010–2016 (catch history, fleet state, FishDope text,
water temperature from text, bait, NWS forecasts, tides, moon) the yes/no call cannot
noticeably beat B1. Next lever: satellite SST/chlorophyll once 2020+ half-day counts load.

## D-031 Goal C: conditions-only model (user decision, 2026-09-24)
Inputs allowed: calendar (day-of-year harmonics, weekend), moon (computed), predicted tides,
NWS coastal forecast (`conditions_daily` nws rows incl. wind/swell direction), NWS zone forecast
(PZZ750, D-C02), and later SST/chlorophyll/currents/buoys. Excluded: everything derived from
`landing_counts` — including trip counts/effort and the fish-count climatology `clim_rate` — and
everything derived from FishDope (reports, text features, water temperature from text, bait
barges, forage). The evaluation-day coverage filter (D-010) still uses report coverage; it
selects which days are scored, it is not a model input, and keeping it makes Goal C numbers
comparable with Goal 1.
New conditions-history features (`cd_*`): per target date the latest forecast visible at the
cutoff, averaged over D-3..D-1 … D-30..D-1: wind, swell, south swell (150–250°), an upwelling
proxy (wind speed × cos(direction − 315°), NW = upwelling-favourable), its 14-day anomaly vs the
same season in prior years' forecasts, and zone-forecast offshore/south wind, south swell and
seas over 3/14 days; plus a second day-of-year harmonic. Past days' forecasts stand in for
observed conditions, which do not exist for 2010–2016 in the source.
Benchmark S0 = season-only logistic on day-of-year harmonics.

## D-032 Goal C, forecast-era results (dev 2012–2016) and the refit-purity rule
Added 30/60/90-day anomalies (upwelling proxy, wind, south swell, total swell) vs a prior-years
day-of-year climatology of the same forecast series. Sweeps C1 (30 configs), C2 one-at-a-time
screen (60), C3 combinations (20). With yearly-frozen models: season-only S0 AUC 0.709,
Brier 0.234, MCC 0.318; best conditions set (S2 + 90-day south-swell anomaly + 30-day
upwelling anomaly + 3-day seas) AUC 0.714, Brier 0.222. No single condition improves ranking
by more than +0.007 AUC; the 90-day south-swell anomaly is the only clear Brier gain (−0.010).
Swell/wind anomalies are systematically offset in every year (all south-swell anomalies < 0,
wind > 0 except 2015), pointing to drift in the NWS forecast series (product/wording changes),
which also explains why several anomaly features hurt out of sample.
**Purity rule:** Goal C's primary numbers use yearly-frozen models (trained only on earlier
years). Monthly refit lifts even S0 to AUC 0.750 because it learns the current year's
yellowtail level from last month's outcomes — catch information entering through training
labels. Monthly-refit Goal C numbers are reported only as a flagged secondary view.

## D-033 Splits redefined now that the source covers 2010–2026 (before any look at 2017+)
Source cfae8af has half-day counts for every year 2010–2026 (2019–2025 ≥ 330 days each;
2026: 264 days so far). `holdout_access.log` is empty and no score has ever been computed on a
date ≥ 2017 (agent D read a few 2018–2023 bait text strings, no labels — D-D disclosure).
New split, recorded before any evaluation on 2017+:
- **Dev folds: 2012–2023** (Goal 1 gains seven fresh test years, 2017–2023).
- **Holdout: every day ≥ 2024-01-01** (~950 days incl. 2026; grows as 2026 continues).
- SST-era specs (Goal C track 2) use dev folds 2021–2023 with training starting 2020-01-01,
  since satellite SST starts 2020-01-01 (`Spec.dev_years`, `Spec.train_start`).
The D-009 bar is unchanged. Earlier logged results were on dev 2012–2014 or 2012–2016; each
run's config.json records its dev years.

## D-034 Satellite ocean inputs (Goal C track 2 and available to Goal 1)
Source `conditions_daily`: NOAA Geo-polar Blended SST (2020-01-01+), NOAA-20 VIIRS chlorophyll
(2021-08-26+), altimetry geostrophic currents (2020-01-01+), per model tile. Availability:
data dated t is public at (t + lag − 1 days) 20:00 PT with lag 2 days for SST/currents and 21
days for chlorophyll, so at the D-1 21:00 cutoff SST/currents up to D-2 and chlorophyll up to
D-21 are usable (tested: nothing dated D-1 is ever visible). Caveat: the source's backfilled
history carries NOAA's current (reprocessed) values, not first-published near-real-time values
(`ingest/conditions_snapshot.py` docstring) — mildly optimistic for 2020–2026 back-tests.
GOES-West SST is excluded (patchy 2023-10+). Features `sst_*`, `chl_*`, `cur_*`: SD-coast SST
last value / 7-day mean / 7-day trend / 30-day max, Coronados and 9-Mile SST, offshore minus
coast gradient, share of tiles ≥ 68 °F, max tile SST, log chlorophyll, current speed and
northward component. All are NaN before 2020.

## D-035 Goal C SST track results (train 2020+, dev folds 2021–2023, yearly-frozen)
Sweeps C4 (15 configs), C6 (14), C7 (8); EDA on dev 2020–2023 in `sweeps/C5_sst_eda_output.txt`.
- SD-coast SST (lagged 2 days) has a strong monotone relation with the label on dev days:
  <60 °F 1%, 60–64 °F 9%, 64–68 °F 20–23%, 68–70 °F 27%, 70–72 °F 45%, >72 °F 35%.
  Univariate AUC 0.78; coast warmer than offshore and lower chlorophyll also help (0.61, 0.58
  when flipped); SST trend, currents add nothing.
- Best: **SST alone** (1 feature, logistic) AUC 0.803, Brier 0.1068 vs season-only S0 AUC
  0.762–0.769, Brier 0.1115. Adding season, gradient, chlorophyll, forecasts or boosting does
  not improve ranking with 1–3 training years.
- Yes/no: every model incl. S0 lands at MCC 0.28–0.30 once thresholds are chosen properly
  (S0 0.304 by calling "yes" through summer, recall 0.93). SST's gain is in ranking/probability
  quality, not in the hard call. B1 (uses catch data) is 0.417 on these folds.
- New threshold rule `insample_*` (threshold from the fitted model's own training predictions;
  training data only): needed because the 2021 fold has a single training year and no inner
  walk-forward fold, which previously forced the 0.5 default and zero calls.
Goal 1 re-run on dev 2012–2023 (D-033): B1 0.554; e005 0.581 (CI of gain [+0.009, +0.045]),
e009 0.580, e007 0.578, eB01 0.577 — above B1 over twelve years, still short of the +0.05 bar.

## D-036 Goal C: per-area SST check and spatial features
EDA (dev days 2020–2023, `sweeps/C8_tile_sst_eda_output.txt`): SST (lagged 2 days) in each of the
source's 10 tiles has univariate AUC 0.755–0.778, and 0.655–0.689 within the middle half of the
season-only probability — the tiles move together, so the signal is the regional warm/cold state,
not where warm water sits. Tiles are coarse (t_sd_coast = 183 nm², Del Mar–IB); the source defines
kelp-bed sub-zones (point_loma_kelp, la_jolla, bull_ring) but stores no SST for them; finer SST
needs a source-side ingest change (not possible from this repo; data comes only from the source).
One spatial contrast stood out: south (Coronados + Baja) minus North County SST, AUC 0.312
(i.e. 0.688 flipped: north relatively warm is better). Added features `sst_north_last`,
`sst_south_minus_north`, `sst_tiles_ge68`; tested in sweep C9 (pre-declared, 6 configurations).
User's OneDrive weather archive: not reachable (auth required); dropped at user's request.
