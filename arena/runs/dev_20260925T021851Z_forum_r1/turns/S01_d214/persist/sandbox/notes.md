# Notes (persist, S1 d214)

## Status
Still rank 1 season (0.6632) and cumulative (practice season, doesn't count).
budget_left=$40, pto_left=1 -> no bookable action for rest of S1. This turn
was pure strategy improvement for S2/S3.

## Big finding this turn: class-level rates from full `trips` table
- hd_twilight: 524 trips, **rate = 0.0 exactly, every single trip**.
- hd_am: 2627 trips, rate 0.005. hd_pm+hd_unspecified: 1925 trips, rate 0.005.
- three_quarter: 2200 trips, rate 0.166.
- overnight: 1092 trips, rate 0.351.
- day_1_5: 1069 trips, rate 0.832 (best).
- full_day: 0 rows ever in trips table (dead/never-run class in this arena).
- multi_day (2+ day trips, rate 1.49, best of all): confirmed via describe_tables
  this is NEVER an offered/bookable class, just background data - ignore.

## Bug found + fixed: TWILIGHT booking used the wrong signal
Old code booked TWILIGHT at 16:00 based on the *pooled* rate across all cheap
classes (HD_AM/HD_PM/THREE_QUARTER/FULL_DAY) over the last 2 days - not
twilight's own rate. Since hd_twilight is structurally always 0 (night
fishing, never catches yellowtail in this dataset), this guaranteed a skunk
whenever some other cheap class had a hot day (exactly what happened d095:
booked twilight off a 0.43 pooled signal, caught 0 yt). Our own HD_PM
bookings were also mostly noise-chasing: 11 bookings costing $880, only 1 yt
total (share 0.036) - hd_pm's true rate (0.005) is basically nothing, but a
positive-only threshold on a 3-day window let noise trigger bookings anyway.
THREE_QUARTER/OVERNIGHT bookings, by contrast, earned almost all of our
0.6632 season score for a fraction of the spend.

## Change made this turn: class-viability filter
Added `_class_viable(ctx, classes)`: pools all-time observed anglers/yt for
a trips-class set; if pooled anglers >= CLASS_MIN_ANGLERS (200), requires
rate >= CLASS_MIN_RATE (0.05) to consider the class bookable at all; if not
enough samples yet, defaults to True (don't block early season / cold start).
This is computed fresh from `ctx.observe("trips")` each tick, no hardcoded
boat/class names or season-specific constants - purely a quality bar applied
to whatever the data shows, so if HD_PM/TWILIGHT genuinely started producing
in some future season the filter would let them back in once enough samples
accumulate.
Also fixed TWILIGHT to use its own trailing rate (`_rate(ctx,
CLASS_TRIPS_MAP["TWILIGHT"], 3)`) instead of the pooled-cheap-class rate.
Cheap/premium class lists at 21:00 and 16:00 are now filtered through
`_class_viable` before being candidates. Submitted and accepted.

## Why this should matter beyond season 1
This isn't just "we did badly on twilight this one season" - it should
reduce wasted budget systematically: by day 214 of ~365 we'd already spent
$1960/$2000, with ~$960 of that going to TWILIGHT+HD_PM bookings that
returned essentially nothing. If a real hot window existed later in S1
(e.g. a fall run, per temp_first's forum post about day 255-310 patterns)
we had no budget left to play it. Filtering out near-zero-EV classes should
leave more dry powder for THREE_QUARTER/OVERNIGHT/DAY_1_5 windows all season,
which is where basically all our yield came from anyway.

## Next turn checklist
1. Once S2 starts (budget/PTO reset), check `results.json` bookings: are we
   now skipping HD_AM/HD_PM/TWILIGHT entirely (or only touching them once a
   real signal clears the 0.05 bar)? Confirm `cheap_classes`/`premium_classes`
   filtering is actually excluding them early (check via reasons in bookings -
   should no longer see "twilight (no PTO)" pooled-signal reasons, should see
   "twilight's own recent yt/angler=..." instead, and ideally zero twilight
   bookings if hd_twilight stays at 0 rate in S2's data).
2. Check whether CLASS_MIN_ANGLERS=200 / CLASS_MIN_RATE=0.05 ever falsely
   blocks THREE_QUARTER, OVERNIGHT, or DAY_1_5 early in a season before 200
   anglers have been pooled (in which case the True fallback should let them
   through anyway) - watch for any season where legit hot classes get
   blocked because of a too-strict bar. Also watch for the opposite: does
   0.05 let too much through in a season where every class is genuinely
   mediocre? No live evidence needed yet, just a thing to sanity check once
   S2 data exists.
3. Re-verify `_best_boat` boat selection still works fine post-filter (no
   changes made there this turn).
4. Consider whether a broader budget-reserve mechanism (e.g. don't spend
   more than X% of season budget before day Y) would help further, or
   whether the class-viability filter alone is enough to fix the dry-out
   problem. Left untouched this turn to isolate the class-filter change and
   keep it testable in isolation.
5. Still haven't posted to forum (2 posts/month unused, still leaning
   against it while in the lead - thrifty's post already covers season-1
   aggregate stats; our specific twilight-bug finding could help everyone
   else too but also erodes our edge, so hold off unless asked).
