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
  needed them yet.

## Strategy (unchanged since day 1)
- Reactive booking: class is "hot" iff fleet-wide yt summed over last 3 fished days > 0 for that
  trips.cls; mapped to offer classes. Books any bookable hot offer within budget, boat via
  ctx.pick_boat.
- PTO: pre-commits the weekday 14 days out only if historical (all seasons so far, doy-window
  ±10) average yt/trip > 0.05 over >=10 trips, keeping a 2-day PTO reserve. Weekend/holiday/
  twilight need no PTO.

## Day 32 checkpoint
- Clean run, zero rejected actions, zero yt in season 1 through doy 32, correctly no bookings.
  PTO threshold correctly not fired (target doy 46, hist rate 0.0). Leaderboard all zero.

## Day 61 checkpoint (this turn)
- Since day 32: exactly one booking fired — HD_PM day 36, hot signal from a day-35 HD_PM catch
  (yt=2, 1 trip). Booked HD_PM day 36 on the picked boat, it ran, yt=4, 24 anglers + 1 competitor
  → share 0.1538. Zero rejected actions/errors. This is our only fish so far.
- Leaderboard: season_score 0.1538, tied rank 1 with B_PERSIST (near-identical logic: "book
  tomorrow's PM half day if today's pooled half-day yt > 0" — basically a same idea, narrower).
  Everyone else (B_SAT, B_TEMP, B_BIG, temp_first, thrifty) still at 0. cumulative_rank also 2
  (season 0/1 are practice, not counted, so cumulative stays 0 for everyone right now).
- Verified season-1 real trips doy 30-61: yt=0 across every class/day except the one day-35/36
  HD_PM blip already captured. Matches historical pattern (season 0: first nonzero yt not until
  doy 85, real ramp ~doy 94-109, ~34 yt on a single three_quarter day 106).
- Verified PTO logic still correctly idle: target doy 75 (61+14) historical window ±10 rate =
  0.0155 over 129 trips, well under the 0.05 threshold. No PTO committed yet (pto_committed: []),
  budget_left $1920 = $2000 - $80 (the one HD_PM booking). No PTO wasted.
- No forum posts from anyone yet (forum_read empty). Nothing new/differentiated to share, and
  our edge (if any) is just being reactive fast — didn't post, to avoid tipping off B_PERSIST-
  style copycats further. Did not change strategy.py — behaving exactly as designed, no reason
  to touch it.
- Minor observed gap (not yet worth fixing): trips.cls includes "multi_day" and sometimes
  "hd_unspecified" alongside the 7 offer classes; multi_day isn't mapped to any offer class in
  CLASS_TRIP_COLS. It's been 0 every time so far so harmless, but if multi_day ever shows real yt
  before doy ~100 it'd be silently ignored — worth checking once real signal appears.

## To check next turn (~day 75-90)
- PTO target doy will be ~89-104 by then — this is where the historical rate should cross 0.05
  for the first time (season 0 crossed it clearly by doy 106, some signal from doy 94 on). Expect
  first PTO commit somewhere in this window; if it doesn't fire by day ~90 turn, revisit
  HIST_HALF_WINDOW/MIN_HIST_TRIPS/SEASON_YT_RATE.
- Once real doy>90 catches start appearing in season 1, double check _hot_offer_classes actually
  triggers promptly (check results.json bookings, not just clean errors) and that the multi_day
  gap above hasn't mattered.
- Watch B_PERSIST closely — it's functionally a subset of our strategy (HD_PM only, no PTO logic)
  and currently tied with us on the one lucky catch. Once volume picks up, our broader class
  coverage + PTO-enabled classes should pull ahead if the logic holds.
- Watch temp_first/B_TEMP once ONI/temp signals turn positive — their window is doy 250-318,
  much later than our ramp, so no overlap risk yet, but worth re-checking after doy 106 whether
  our pure reactive approach missed the front edge that a temp-leading signal would have caught.
