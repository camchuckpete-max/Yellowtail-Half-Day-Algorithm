# Notes (persist, S1 d153)

## Status: rank 1, season score 0.6632 (next best 0.1538). Cumulative still 0 for
everyone - seasons 1-2 are practice, don't count. Budget_left=$40 < cheapest offer
($80), pto_left=1 -> literally no bookable action possible for the rest of season 1
no matter what the strategy says. That's expected/fine, not a bug.

## Fix made this turn: OVERNIGHT/DAY_1_5 boat mismatch bug
`_book_if_bookable` was calling `ctx.scheduled_boats(cls, offer.departure)` /
`pick_boat(cls, offer.departure)`, but OVERNIGHT and DAY_1_5 depart on `d` and
fish on `d+1` - the schedule table is keyed by **fish date**, not departure date.
Verified directly: schedule for cls='overnight' had fish_date_doy=132 -> "Josie
Lynn", fish_date_doy=133 -> "Legend". Our OVERNIGHT:861 (departure d132, fishing
d133) queried scheduled_boats with day=132 (departure), got Josie Lynn back as a
"scheduled" boat and booked it -> rejected: "'Josie Lynn' is not scheduled for
OVERNIGHT on S01 d133; scheduled: Legend". Fixed by using `offer.fishing_dates[0]`
(falls back to `offer.departure` if empty) for both scheduled_boats and pick_boat
calls. For single-day classes fishing_dates[0] == departure so no behavior change
there; this only changes OVERNIGHT/DAY_1_5. Confirm next turn: does results.json
show any more OVERNIGHT/DAY_1_5 rejections, or do they now book+settle cleanly?

## Historical performance recap (for when season 2/3 budget refills)
- THREE_QUARTER was the standout class this season: hot nearly continuously from
  ~doy106 through at least doy136 (per-day rate 0.34-0.66), producing our two
  biggest single-trip shares (0.4286 on d136 with 15yt/34anglers, 0.0833 on d126).
  HD_AM/HD_PM/FULL_DAY stayed near 0 essentially the whole time we tracked them.
  OVERNIGHT/DAY_1_5 rates were low/noisy (~0.07) whenever checked - not worth
  much budget relative to three_quarter, though the boat-lookup bug means our
  premium-class sample was smaller/noisier than it should've been; can't fully
  rule them out yet with a clean signal.
- Since strategy tracks per-class trailing rate and picks the best bookable one
  each tick (no hardcoded "three_quarter is always best" assumption, no season-
  specific dates/constants), this should adapt fine if the hot class differs in
  season 2/3. Don't assume three_quarter repeats - re-derive by-class rates fresh
  each time budget is available again.

## Next turn checklist
1. Did the OVERNIGHT/DAY_1_5 fix eliminate boat-mismatch rejections? Check
   rejected_actions_and_errors_since_last_turn in results.json.
2. If this is a new season (budget/PTO reset to $2000/10), re-run the by-class
   trailing-rate query from scratch early - don't assume three_quarter is still
   the hot class immediately; the early-season signal took until ~doy106 to show
   clearly last time (HD_AM/HD_PM looked dead the whole season, so the "best of"
   logic handled that fine, but consider whether PTO_RESERVE=1 is still right
   once a fresh 10 PTO days are available - could probably afford a bigger
   reserve early and tighten only once a real bite is confirmed, to avoid
   burning PTO on noise before the pattern is clear).
3. Still haven't posted to forum (2 posts/month unused, forum_read shows nothing
   from us or anyone competitive yet as of d153). We're in the lead now, so the
   earlier "don't tip off competitors" logic applies even more strongly - keep
   sitting on it unless there's a clear reason to post (e.g. season 1/2 are
   practice/not scored cumulatively, so competitive info leaked here mostly only
   helps rivals in *this* practice season, which doesn't matter much either way -
   still, default to not posting).
4. Check whether `ctx.offer(cls).fishing_dates` really behaves as assumed (list,
   first element = the day trips/schedule tables key on) once OVERNIGHT/DAY_1_5
   bookings actually go through post-fix - validate against schedule table like
   this turn did, don't just trust the docstring blindly.
