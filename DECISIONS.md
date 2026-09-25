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

## D-037 Spatial SST contrast result; data request to the source (user-authorised PRs)
Sweep C9 (6 configs, train 2020+, dev 2021–2023, in-sample threshold): SD-coast SST alone AUC
0.803 / Brier 0.1068 / MCC 0.292; + south-minus-north contrast AUC 0.805 / Brier 0.1074 / best
MCC 0.336 (C=0.03; gain concentrated in the 2021 fold); + count of tiles ≥ 68 °F no better.
Ranking gain is noise; the MCC gain is best-of-6 and one-fold-driven → not adopted.
User authorised requesting new data from the source via PRs on Daily-Fishing-Prediction (Muse
fulfils and closes them). Request 0001 =
https://github.com/camchuckpete-max/Daily-Fishing-Prediction/pull/1 (branch
claude/clever-volta-xta9qm): blended SST 2010–2019, kelp-bed sub-zone SST, currents 2015–2019,
buoy history 2010–2021, CUTI/BEUTI upwelling, pre-2021 chlorophyll, with per-row point-in-time
metadata. Muse's clarifying questions and our answers are in `data_requests/0001-*.md` on that
branch. When the data lands: log the split for the longer SST history before evaluating on it.

## D-038 Streaming dump loader
Source dumps grew past SQLite's maximum query size (`buoy_observations`; `conditions_daily` with
the SST backfill), so `source.open_db` no longer passes a whole dump to `executescript`. It now
accumulates complete statements (statements can span lines because text fields contain newlines),
drops the dump's own BEGIN/COMMIT, and executes ~50 MB batches each in its own transaction.
Verified on the pinned snapshot (source 7121831): landing_counts, conditions_daily,
fishdope_reports and marine_forecasts are row-for-row identical to the previous loader's output.

## D-039 Goal D definition (user, 2026-09-24)
Per-trip label for New Seaforth and Sea Watch half-day fishing trips (AM/PM/unspecified/twilight;
hoop-net/lobster excluded as in D-001); 10,386 trips 2010–2026, 17.6 % with ≥1 yellowtail.
Allowed inputs: the Goal C conditions allowlist (D-031, enforced by `assert_conditions_only`)
plus trip descriptors (boat, trip class). No catch history of any kind and no FishDope-derived data.
Evaluation: walk-forward by year (train on years before the test year only), trips grouped by
date for bootstrap; holdout ≥ 2024-01-01 untouched. Output = calibrated probability bands with
observed hit rate per band on held-out dev years, plus plain-language condition ranges per band
(from the fitted model / a shallow rule tree fitted on training years only).
Tracks: (P) predictive at 21:00 PT D-1 and (E) explanatory using conditions during the trip; E
results are labelled explanatory and never reported as forecast skill.
Data request 0002 (hourly La Jolla predicted tides, CO-OPS 9410230 obs, CDIP 100/201 waves+SST,
Scripps Pier daily SST, trip times, KSAN wind) committed to the request PR branch.

## D-040 Goal D sweep 1 (prototype, source cfae8af, dev only)
Trip table: 10,353 New Seaforth + Sea Watch half-day trips (2010-05 → 2026-09), conditions = the
PIT day-level conditions for the trip date + trip class + boat. Walk-forward by year.
2012–2023: season + trip type AUC 0.660 / Brier 0.143; + moon/tides 0.658; + day forecast 0.655;
+ conditions history (upwelling, swell anomalies) 0.676 / 0.140. SST era (train 2020+, test
2021–2023, base rate 8.9 %): season + trip 0.705; + SD-coast SST 0.715 / 0.078, bands calibrated
(0–5 %: 1.3 % observed of 541 trips; 5–15 %: 10.8 % of 721; 15–35 %: 14.6 % of 494) but no trip
above ~35 % because 2021–2023 were lean years. The 50/75/95 % bands need warm years (2014–15: 30–43 %
of trips) in the SST record → waiting on request 0001's 2010–2019 SST backfill and 0002's hourly
La Jolla data. 16 configurations (Goal D ledger).

## D-041 Goal D trip-window conditions (requests 0001–0003 deliveries)
New source tables: `coops_tide_predictions` (hourly La Jolla 9410230 predictions 2010–2026),
`shore_station_temps` (CO-OPS 9410230 6-min water/air temp 2010+), `buoy_observations` (only local
stations 46225, 46232, 46254, 46266, LJPC1 are loaded — streaming filter, `FILTERS_VERSION` in the
DB cache key), `upwelling_daily` (CUTI/BEUTI, 14-day publication lag applied), `climate_indices`
(ONI/PDO/NPGO/MEI, each month usable after month end + documented release lag). Module
`yt/hourly.py` builds per trip: `hc_*` predictive features (observations ≤ 21:00 PT D-1, tide
predictions for the trip window, lagged indices) and `ex_*` explanatory features (observed during
the trip window). Trip windows: AM 06:00–11:30, PM 12:30–17:30, twilight 18:00–22:30 PT (New
Seaforth per Muse; Sea Watch UNCONFIRMED, same slots assumed). Guards: `ex_*` rejected in predictive
runs (tested); `hc_*` poisoning/deletion test (post-cutoff observations and unpublished index
values) passes. Sweep D2 (18 configs, dev 2012–2023, source dc526dd): season+trip AUC 0.660 →
+pier water temp 0.744 (Brier 0.143 → 0.130); +buoys 0.716; +climate indices 0.705; +pier+climate
0.751; tide during trip, upwelling, pier wind: no gain; explanatory in-trip conditions: no gain.
Uncalibrated bands overconfident at the top (predicted 0.94 → observed 0.72 on 238 trips).
Note: dc526dd's buoy dump was incomplete for 46254 and LJPC1 (Muse: export-timing artifact; full in
d66d778+). D2 is re-run on bfd3a15.

## D-042 Fixes found by the full PIT suite on the new source
(1) `test_ocean_present_and_lagged` hard-coded satellite SST starting 2020-01-01; the request-0001
backfill starts it 2010-01-01 → assertion relaxed (not a leak). (2) The new kelp-bed sub-zone SST
rows were silently included in tile-comparison features (`sst_offshore_grad`, `sst_warm_frac`,
`sst_tiles_max`, `sst_tiles_ge68`, …) → those now use the 10 `t_*` tiles only. Goal C results
(D-035–D-037) predate the kelp rows and are unaffected; Goal D sweeps do not use these features.
Full PIT suite passes on dc526dd after the fixes.

## D-043 Goal D results on the complete source (bfd3a15): pier water temperature dominates
Full PIT suite passes on bfd3a15 (complete 46254 / LJPC1 buoy data). Sweep D2 re-run (D2b):
unchanged conclusions (season+trip 0.660; +pier water temp 0.743; +pier+climate 0.748; tide, upwelling,
wind, in-trip observations add nothing). Sweep D3: isotonic calibration from inner walk-forward folds
made ranking worse (AUC 0.743 → 0.694 / 0.715) — too few inner years; dropped. Rule tree (depth 3,
leaf ≥ 150, walk-forward): AUC 0.718, held-out bands 0–5 % → 6.6 % observed … 65–85 % → 50 % observed;
its top rule = pier water > 68.4 °F, daytime trip, ONI > 0.1.
Descriptive (pooled dev 2012–2023, NOT held-out): hit rate by pier water °F (24 h before cutoff) —
AM / PM / twilight: <60 3.5/2.3/0 %; 60–62 7.8/9.5/0; 62–64 11/12.5/1.4; 64–66 13/20/0; 66–68 20/21/6;
68–70 28/37/9; 70–72 43/53/17; >72 49/67/3.5 %. Warm end (D4): ≥70 °F daytime by ONI: ≤0 21/38 %,
0–0.5 47/60 %, 0.5–1 34/39 %, >1 69/83 % (AM/PM); warm water in June 4 %, Jul 37 %, Aug 53 %,
Sep 67 %, Oct 60 %; after a 3-day cooling PM 72 % vs warming 51 %. No combination reaches 95 %.
Top cells are dominated by 2015 (≥72 °F PM: 48 of 174 trips, 92 %). 3 + 1 configurations (D3, D4
descriptive) added to the Goal D ledger.

## D-044 Goal D sweep D5: interactions, first honest held-out bands
Walk-forward 2012–2023 (source bfd3a15), 9 configs. Pier °F (centred at 66) + trip type + season:
AUC 0.731; + temp×PM, temp×twilight, temp×season interactions 0.741 (Brier 0.1292, best); + ONI and
temp×ONI 0.762; + 3-day temp change 0.764. Held-out bands of the best-Brier logistic (F+inter,
C=0.1): 0–5 % → 7.4 % observed (1,782 trips); 5–15 % → 11.3 % (2,859); 15–35 % → 20.1 % (1,741);
35–65 % → 42.7 % (888); 65–85 % → 59.3 % (241); 85–100 % → 87.2 % (47). Depth-4 tree AUC 0.707; its
top leaf: pier > 68.4 °F, daytime, late summer–fall, ONI ≥ 0 → 62 % (training). Goal D ledger +9.

## D-045 Glider subsurface temperature and sea-level anomaly (sweep D6)
`subsurface_temp_daily` (Spray gliders 2014+, daily 10-m bins; public 3 days after the described day)
and `sea_level_anomaly` (La Jolla box, 2015+; public 2 days after) added as `hc_glider_*` (5 m, 45 m,
5–45 m stratification, 10-day window) and `hc_sla_lj_*`. PIT poison test extended; full suite passes
(source 657c5a8). D6, same folds 2016–2023 for all models: D5 base AUC 0.754 / Brier 0.1162;
+glider 0.755 (coverage 31 % of trips — transects are intermittent); +SLA 0.750 (coverage 57 % at
657c5a8, backfill later completed); both 0.751. No gain. Goal D ledger +4.
Kelp canopy (`kelp_canopy_quarterly`, kelpwatch API, 1984Q1–2026Q2): no documented publication lag;
per Muse's research releases are batched ~annually → PIT rule: a quarter is usable only from quarter
end + 365 days (Muse's recommended safe bound; +120 d is only a central guess).

## D-046 Kelp canopy and complete SLA (sweeps D7, D7b): not adopted
Source e24c47c (kelp and SLA tables complete). `hc_kelp_{lj,pl}_{last,anom}`: latest quarter visible at
the cutoff (quarter end + 365 d, D-045) and its anomaly vs earlier visible same-quarter values; NULL
(cloud-blocked) quarters skipped. PIT poison test extended; suite passes. D7, folds 2012–2023: D5 base
AUC 0.763 / Brier 0.1292; +kelp 0.723 / 0.1337 — loss concentrated in 2014 (0.841 → 0.714), small
per-fold gains elsewhere. D7b: anomaly only 0.729; La Jolla anomaly only 0.746; +kelp on folds
2016–2023 AUC 0.754 (= base) with Brier 0.1124 vs 0.1162. Reason for rejection: with the one-year lag
the kelp value is effectively constant within a year (14 distinct year-levels in dev), so the model
uses it as a year fingerprint (e.g. high 2014 canopy → 2015, the best yellowtail year); the Brier gain
rests on 8 year-level offsets and does not survive the 2012–2023 folds. SLA re-test on complete data,
folds 2016–2023: 0.750 vs base 0.754 — no gain (confirms D-045). Goal D ledger +5 (D7) +3 (D7b).

## D-047 KSAN METAR hourly weather (sweep D8): no gain, including in-trip wind
`metar_obs` (station SAN, IEM ASOS, 2010+, public at observation time) added: predictive `hc_san_*`
(24 h mean wind speed, onshore (westerly) component, previous afternoon's wind, sea-level pressure and
its 24 h change, relative humidity, visibility; all ≤ D-1 21:00) and explanatory `ex_san_*` (mean and
max wind, onshore component, visibility during the trip window). PIT poison test extended; suite
passes (source e24c47c). D8, folds 2012–2023: base 0.763 / Brier 0.1292; +wind 0.762; +pressure
0.762; +all hc_san 0.760; explanatory +ex_san 0.761; +both 0.759. Descriptive, warm-water (pier
≥ 68 °F) daytime trips: hit rate 42–44 % in every 24 h pressure-change tercile; no monotone in-trip
wind effect (AM 38/36/46 %, PM 46/51 % for the populated terciles). Conclusion: with water
temperature, season and ENSO state known, local weather (wind, pressure, marine layer) carries no
measurable information about a trip's yellowtail outcome. Goal D ledger +6.

## D-048 Chlorophyll at a 1-day lag (owner's decision); sweep D9 inconclusive
Owner, 2026-09-24: "there are still more up to date sources for chlorophyll data, so I think it's fair
to use it, just use the chlorophyll data for the day before." Goal D therefore treats a day's satellite
chlorophyll as visible at 21:00 PT that evening (`hourly.CHL_LAG_DAYS = 1`; Goal C keeps its 21-day
rule, D-034). Caveat recorded: the stored history is the archived VIIRS product, which may be cleaner
than what a live feed shows that evening; a lag-2 sensitivity run is kept alongside.
Features `hc_chl_{sd,nc,bf}_{3d,anom30}`: log chl, 3-day mean ending D-1, and its difference from the
30-day mean, for tiles t_sd_coast, t_north_county, t_43_butterfly. PIT poison test extended; suite passes.
Coverage at e24c47c: 2012-01 → 2014-01 and 2021-04 → now only (backfill running). D9 trains and scores
only on trips with chlorophyll: folds 2013, 2021–2023, 1,344 scored trips, 8 % positive.
Lag 1: season 0.734, season+chl 0.711; D5 base 0.771, +chl (SD coast) 0.775, +chl (3 tiles) 0.769.
Lag 2: base 0.762, +chl (SD) 0.765. Per fold (lag 1, base → +chl SD): 2021 0.709 → 0.740, 2022 0.741 →
0.732, 2023 0.839 → 0.839; the 2013 fold (trained on 2012 alone) swings 0.79–0.96 for the base model
with a one-trip change in the sample, so it carries no information. Descriptive (day trips, dev): no
monotone chlorophyll pattern within pier-temperature bands (<64 °F 4.1/4.8/3.4 %, 64–68 °F
21/22/16 %, ≥68 °F 30/26/28 % for low/mid/high chl). Verdict: no detectable effect, but the test is
weak — it excludes 2014–2020, which holds most warm-water trips. Re-run when the backfill completes.
Goal D ledger +10.
D-048 addendum (Muse, 061622e, ERDDAP metadata): the stored chlorophyll products are *not* fast — SNPP
science quality has a documented 15-day latency (reprocessed), NOAA-20 "near real-time" runs ~15 days
behind. The owner's 1-day rule therefore rests on faster feeds that exist elsewhere (e.g. NASA NRT
L3), not on the products stored here; results with chlorophyll are conditional on that assumption.

## D-049 Kelp-box satellite SST vs the pier thermometer (sweeps D10, D10b): first new signal
`conditions_daily` source `noaacwBLENDEDsstDaily`, boxes la_jolla / point_loma_kelp (2010 → 2019-09-19
only) and tiles t_sd_coast / t_north_county; same 2-day availability rule as Goal C SST (D-034).
`hc_sat_{lj,pl,sd,nc}_f` = latest visible daily value within 5 days. PIT poison test extended; suite
passes (source ba64933). Pier and kelp-box SST correlate 0.88; the satellite reads warmer than the pier
in Jul–Oct (mean +1.4 to +2.5 °F; pier sensor is below the surface, satellite is the skin/bulk
surface blend). D10, folds 2012–2019, trips with a kelp-box value (4,733): pier model 0.745; satellite
instead of pier 0.744; pier + kelp-box sat 0.751; pier + all four satellite series 0.752;
lj-minus-offshore gap 0.743. D10b: max(pier, kelp-box sat) in place of pier 0.752 (Brier 0.1501 vs
0.1531); pier + gap × temp 0.748.
Descriptive, Jul–Oct day trips, within month and pier band: kelp-box surface > 1.5 °F warmer than the
pier → higher hit rate (pier 66–70 °F: Jul 48 vs 25 %, Aug 47 vs 31 %, Sep 50 vs 35 %, Oct 48 vs 19 %;
pier ≥ 70 °F: Sep 79 vs 68 %, Oct 94 % (31 trips) vs 38 %). By year (Jul–Oct, pier ≥ 66 °F: other /
66–70 & warmer / ≥ 70 & warmer): 2012 26/43/60 %, 2013 13/31/–, 2014 53/73/88 %, 2017 46/80/67 %,
2018 51/45/68 %; flat in 2015, 2016, 2019; no year reverses. Reading: warm surface water over the kelp
beds that the pier sensor does not yet show marks yellowtail water. The effect is real but the model
gain is small because much of it overlaps with season. Adopted as a candidate input; needs kelp-box
SST 2019-10 → now (requested) to be tested on 2020–2023 and used live. Goal D ledger +6 (D10) +4 (D10b).
HF radar (request 0004 item 1): radial history starts 2025-06-05 → too short; dropped.

## D-050 Kelp-box SST on the full series (sweep D11): signal partly replicates, no model gain
Source 0d1547d (request-branch export; kelp-box SST now 2010 → 2024-01; rows ≥ 2024 unused). PIT suite
passes. Folds 2012–2023, trips with kelp-box SST (7,558 scored): pier model AUC 0.762 / Brier 0.1320;
+ gap 0.762 / 0.1316; max(pier, sat) 0.762 / 0.1318. The D10 gain (0.745 → 0.752 on 2012–2019) does
not carry into 2020–2023 folds (2020 0.641 → 0.625, 2023 0.832 → 0.824 for max).
Out-of-sample descriptive check of D-049, Jul–Oct day trips 2020–2023 (not seen when D-049 was found),
kelp box > 1.5 °F warmer than pier vs not: pier < 66 °F 10.6 vs 6.9 % (329 / 29 trips); 66–70 °F
23.3 vs 12.1 % (236 / 107) — same ~2× ratio as 2012–2019 (48.6 vs 24.1 %); ≥ 70 °F 17.6 vs 30.1 %
(17 / 143) — reversed, too few trips to read. Verdict: at 66–70 °F the "surface warmer than pier" effect
replicates and is kept as a descriptive modifier in the condition table; it is not added to the
predictive model (no out-of-sample gain). Held-out bands of the pier model on these trips (2012–2023):
0–5 % → 5.1 % observed (1,659), 5–15 % → 11.0 % (2,350), 15–35 % → 18.1 % (1,590), 35–65 % → 40.0 %
(1,093), 65–85 % → 46.6 % (322), 85–100 % → 79.3 % (145); the top two bands are over-confident.
Goal D ledger +3.

## D-051 Condition-range table (sweep D12): low end replicates, high end halves out of sample
Deliverable format the owner asked for: a depth-4 tree (min 80 trips per leaf) on pier °F, month, trip
slot, ONI, kelp-minus-pier gap and 3-day pier change, fit on 2012–2019 (4,983 trips, 22.4 % positive) and
scored on 2020–2023 (2,153 trips, 9.9 % positive; never used for fitting). 2020–2023 AUC: depth 3 0.702,
4 0.703, 5 0.712. The tree used only pier temperature, month, slot and ONI (gap and 3-day change unused).
Leaves (2012–2019 rate → 2020–2023 rate, trips):
- pier ≤ 58.1 °F: 0.5 % → 0.0 % (183 / 141)
- pier 58.7–61.7 °F, Feb–Dec: 5.2 % → 3.3 % (637 / 389); 58.1–58.7 °F: 2.9 % → 1.0 %
- twilight, pier 61.7–68.9 °F, Mar–Dec: 2.2 % → 3.9 % (316 / 103)
- AM/PM, pier 61.7–68.9 °F, Mar–Dec: 18.2 % → 11.4 % (2,314 / 1,041)
- AM/PM, pier > 68.9 °F, Mar–Jul, ONI ≤ 0.3: 14.8 % → 13.3 % (88 / 105)
- AM/PM, pier > 68.9 °F, Aug–Dec, ONI ≤ 0.9: 57.9 % → 35.6 % (535 / 149)
- AM/PM, pier > 68.9 °F, Aug–Dec, ONI > 0.9: 77.6 % → 14.3 % (161 / 14)
- AM/PM, pier > 68.9 °F, ≤ Jul, ONI > 0.3: 46.9 % → 10.0 % (211 / 10)
- pier 61.7–68.9 °F, Jan–Feb: 62.9 % (97, almost all winter 2015) → no trips
Reading: the cold / twilight "0–5 %" conditions are stable across both periods. The warm-water cells
fall by about half in 2020–2023 at the same temperature, month and ENSO state, so a year-level factor
not in the environmental data (yellowtail abundance or availability off San Diego in a given year, or
boats' targeting) sets how high the warm-water odds go. The strong-El-Niño cells (≥ 75 %) had almost no
2020–2023 trips and rest mainly on 2014–2015. No cell reaches 95 % in either period. Goal D ledger +3.
