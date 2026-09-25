# Notes

## Day 1 findings
- Data covers t=90..730 (season 0 fully + season 1 day 1). Season 0 (t=365-730) is a clean
  full-year reference for doy seasonality.
- Yellowtail (yt) catches are essentially zero doy 1-100 (a few 1-shot blips around doy 85-100),
  start becoming real around doy ~106-144 (sporadic double-digit days), then take off hard from
  doy ~180 onward (season 0 saw sum_yt in the hundreds per day around doy 182-204+, still rising
  at the end of the queried range). So the "dead season" is roughly the first 3 months; peak is
  clearly mid-to-late season.
- Right now (season 1 day 1, doy 1) every recent trip (last several days) shows yt=0 across all
  classes. Correctly nothing to book yet.
- ONI/PDO/MEI recent values (as of ~t=708-719): ONI -0.94, PDO -2.95, MEI -1.14 — all negative,
  cool-ish signal. Persona says ignore ocean covariates unless counts stop making sense; haven't
  needed them yet. Worth a look later if the doy~106+ ramp is delayed or weaker than season-0's,
  since a cold pattern could push the bite later/smaller this year.

## Strategy submitted this turn
- Reactive booking: class is "hot" iff fleet-wide yt summed over last 3 fished days > 0 for that
  trips.cls; mapped back to offer classes (HD_AM/HD_PM/TWILIGHT/THREE_QUARTER/FULL_DAY/OVERNIGHT/
  DAY_1_5). Books any bookable hot offer within budget, boat via ctx.pick_boat.
- PTO problem: commit must happen 14 days ahead, before any real bite signal for that date can
  exist. Solved by pre-committing PTO for the weekday 14-days-out using historical (all seasons
  so far, doy-window ±10) average yt/trip > 0.05 threshold, gated by a small reserve (keep >2 PTO
  days uncommitted). This means PTO spend will start ramping up once "today" is ~14 days before
  doy ~96-106 (i.e. around doy 82-92), well before catches actually confirm - accepted risk of
  wasting a few PTO days pre-season, in exchange for having PTO ready when the reactive booking
  logic actually finds a hot class near the real ramp-up.
- Booking itself never checks calendar/PTO state directly — relies entirely on offer.bookable
  (which the platform sets to False if PTO for that date isn't committed). Did not verify this
  assumption against real ctx behavior yet (no local ctx/API source file available in sandbox) —
  watch first results.json for any "not bookable: PTO" rejections that suggest offer.bookable
  isn't doing what I assumed, or for CommitPTO being rejected/duplicated.

## To check next turn (~day 15)
- results.json: did any CommitPTO / Book actions fire or error? Confirm ctx.offer field names
  (id, cls, departure, fishing_dates, cost, pto_dates, bookable) and Day API (.plus, .is_weekend,
  .is_holiday, .doy) match what I assumed — fix strategy if rejected/crashed silently.
- Check whether hot_offer_classes ever fires as doy approaches ~90-110; check budget/PTO burn
  rate from speculative pre-commits.
- Re-examine whether SEASON_YT_RATE=0.05 / HIST_HALF_WINDOW=10 thresholds are triggering PTO
  commits at a sane pace (not too early/aggressive, not too late for the 106+ ramp).
- Consider tightening "hot" definition to yt-per-angler rather than raw sum if a few big boats
  dominate and create false positives/negatives.
