## Day 1 findings
- Data covers t=90..730 (season 0 fully + season 1 day 1). Season 0 (t=365-730) is a clean
  full-year reference for doy seasonality.
- Yellowtail (yt) catches are essentially zero doy 1-100 (a few 1-shot blips around doy 85-100),
  start becoming real around doy ~106-144 (sporadic double-digit days), then take off hard from
  doy ~180 onward (season 0 saw sum_yt in the hundreds per day around doy 182-204+, still rising
  at the end of the queried range). So the "dead season" is roughly the first 3 months; peak is
  clearly mid-to-late season.
- ONI/PDO/MEI recent values (as of ~t=708-719): ONI -0.94, PDO -2.95, MEI -1.14 — all negative,
  cool-ish signal. Persona says ignore ocean covariates unless counts stop making sense; haven't
  needed them yet. Worth a look later if the doy~106+ ramp is delayed or weaker than season-0's.

## Strategy (unchanged since day 1)
- Reactive booking: class is "hot" iff fleet-wide yt summed over last 3 fished days > 0 for that
  trips.cls; mapped to offer classes. Books any bookable hot offer within budget, boat via
  ctx.pick_boat.
- PTO: pre-commits the weekday 14 days out only if historical (all seasons so far, doy-window
  ±10) average yt/trip > 0.05 over >=10 trips, keeping a 2-day PTO reserve. Weekend/holiday/
  twilight need no PTO.

## Day 32 checkpoint (this turn)
- results.json shows zero rejected_actions_and_errors_since_last_turn, and empty
  pto_committed/bookings — code has been running clean since day 1, no crashes, no invalid
  actions. My assumptions about ctx.offer fields and Day API held up.
- Confirmed via arena_query: all trips through doy 32 (season 1) show yt=0 across every class
  (hd_am/hd_pm/hd_twilight/three_quarter/overnight/day_1_5), consistent with day-1 findings —
  correctly no bookings yet.
- Confirmed PTO pre-commit logic correctly has NOT fired: historical rate for doy 46 (=32+14,
  today's PTO_LEAD target) window ±10 is still 0.0 over 111 trips, well below the 0.05 threshold.
  So no PTO wasted yet.
- No forum posts from anyone yet. Leaderboard: everyone at 0 fish (season_score), all still
  building position. Left rank unchanged (6th of 7) — a fully neutral ranking metric at this
  point in the dead season since nobody has caught anything yet. Other strategies visible:
  B_SAT (Sat PM half-day Jul-Oct), B_TEMP/temp_first (water-temp + ONI driven), B_BIG/thrifty
  (1.5-day Friday trips, cost-per-fish framing). None of these have started acting either.
- Decision: did NOT change strategy.py this turn — nothing to react to yet, logic verified sound.
  Did NOT post to forum (nothing new to say, no fish caught by anyone).

## To check next turn (~day 46, when PTO_LEAD target reaches doy ~60, and again toward doy 90-100)
- Watch for the historical PTO-worth-it rate crossing 0.05 as target doy approaches ~96-106 (the
  real ramp start) — first crossing should happen somewhere in the doy 82-96 "today" range, i.e.
  target doy 96-110. If it fires much earlier (false positive from a stray blip trip) or never
  fires by day ~85, revisit HIST_HALF_WINDOW/MIN_HIST_TRIPS/SEASON_YT_RATE thresholds.
- Once real season-1 catches start appearing (doy > ~100), check that _hot_offer_classes actually
  triggers bookings promptly and that boats picked via ctx.pick_boat are being scheduled/booked
  successfully (watch results.json bookings list, not just absence of errors).
- Consider tightening "hot" to yt-per-angler rather than raw sum once real catch data exists, in
  case one big boat's count creates false positives/negatives for the whole class.
- Watch competitor strategies (B_TEMP/temp_first, thrifty) on the leaderboard once fish start
  being caught, to see if pure temp/ONI signals or cost-per-fish targeting are outperforming
  the pure reactive lagging-indicator approach — may be worth blending in a temp/ONI pre-filter
  if reactive-only proves too slow to catch the front edge of the ramp.
