# Notes (persist, S1 d122)

## Big bug found and fixed this turn
Every single TWILIGHT/DAY_1_5/OVERNIGHT booking attempt since d93 (~25 of them) was
REJECTED with "no boat given" or a boat-name mismatch error. Root cause: `ctx.pick_boat`
can return None (or, once, a stale boat name like "Aztec" from its 60-day-history fallback)
when NO boat is actually scheduled for that class/day at all - which is the common case:
querying `schedule` showed hd_twilight/day_1_5/overnight only run on a handful of days out
of any given month, not daily. We were calling `Book` with whatever `pick_boat` returned
without checking `ctx.scheduled_boats(cls, day)` first. Fixed by requiring
`scheduled_boats(...)` to be non-empty before booking, and falling back to
`scheduled_boats[0]` if `pick_boat`'s pick isn't in that list. This was pure waste (no fish
lost, just silently no-opped) but should let real twilight/premium opportunities through now
when they exist.

Also found: the old "hot rate >= 0.3 -> add THREE_QUARTER/FULL_DAY on top of the HD_PM/HD_AM
booking for the same tomorrow-date" bonus branch always failed with "already booked for that
fishing date" (RULES.md: at most one trip per fishing date). Removed - dead code.

## Real signal found: THREE_QUARTER has been hot for 3+ weeks, HD_AM/HD_PM dead
Queried trips by class, doy105-121: three_quarter yt/angler has been *positive nearly every
single day* since ~doy106 (range ~0.02-0.4, e.g. doy109: 24/42=0.57, doy118: 16/44=0.36),
while hd_am and hd_pm have stayed at ~0 the whole time. Old strategy pooled ALL cheap classes
into one rate and then booked in fixed priority order HD_PM > HD_AM > THREE_QUARTER > FULL_DAY
- so it kept booking dead HD_PM trips (rate diluted to near 0 by the zeros) and essentially
never reached THREE_QUARTER despite it being the actually-productive class. This is likely
the main reason season_score (0.0357) is well behind B_PERSIST/thrifty (0.1538 each) at d122.
Fixed: now compute trailing rate PER offer class separately and book whichever bookable class
has the best positive rate. Also confirms the "yesterday tells tomorrow" persona is directionally
right - the momentum signal is real and multi-week, just was being applied to the wrong class.

## PTO gating was too conservative / miscalibrated
Old code assumed peak season starts at doy160 and required a much higher bar (rate>=0.12
with a 5-day reserve) to commit PTO before that. But the real three_quarter bite already
started ~doy106, so PTO commits only happened d107-111 then stalled once pto_left hit the
5-day reserve floor - right as the bite was still going. Replaced the doy-window gate with:
commit weekday PTO 14 days out whenever the best trailing rate (any class) is positive,
keeping only a 1-day reserve. pto_left=5, budget_left=$1040 going into this change.

## Leaderboard context (d122)
B_PERSIST (0.1538) and thrifty (0.1538) lead season score; we're 3rd at 0.0357 (one single
1-yt catch on HD_PM:839, 27 anglers). B_PERSIST's rule is literally "book tomorrow's PM
half-day if yesterday's pooled half-day count > 0" - simpler than us but apparently caught
the same window better, or got luckier on boat draws (no boat-picking bug to lose bookings to).
thrifty pivoted from early-season half-day (claims it failed) to overnight/1.5-day for late
season - worth rechecking their framing once/if overnight or day_1_5 counts turn hot for us too
(currently day_1_5 just ticked to 0.167 at doy120, small sample, watch it).

## Next turn checklist
1. Check results.json: did TWILIGHT/OVERNIGHT/DAY_1_5 bookings actually go through now (no
   more "no boat given" rejections)? Did the per-class rate logic actually book THREE_QUARTER
   instead of HD_PM when three_quarter was hotter?
2. Is three_quarter still hot, or did the bite move/die? Re-run the by-class-by-day query for
   doy122+ and re-derive whichever class is actually producing right now - don't assume
   three_quarter stays king.
3. Watch pto_left - with reserve now only 1, we could burn through the remaining 5 PTO fast if
   the signal stays positive daily. Decide if that's actually correct or if reserve should come
   back up once/if PTO gets low and no huge trip is in sight.
4. Still have 2 forum posts/month unused. Nothing posted this turn (findings are internal
   strategy bugs, not something to tip off competitors to - especially since B_PERSIST/thrifty
   are ahead and could benefit more than us from the "check scheduled_boats before booking"
   lesson). Reconsider once we're not behind.
