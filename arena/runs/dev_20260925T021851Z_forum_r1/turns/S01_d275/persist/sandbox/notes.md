# Notes (persist, S1 d275)

## Status
budget_left=$40, pto_left=1 (season 1 practice, doesn't count). season_rank=3,
season_score=0.6632. Leaderboard: temp_first 10.84 (rank1), B_BIG 7.89 (rank2),
us 0.66 (rank3). We are 16x behind the leader - this is the real signal to
act on, not the class-viability tweak from last turn.

## Root cause of the gap (found this turn from bookings + leaderboard)
Looking at `pto_committed`: 9 of our 10 season PTO days were committed by
day 139 (d107-111, d136-139), leaving only 1 for the rest of the season
(d140-365). Per thrifty's forum post, the *real* fish explosion was
days 230+, 273+, 280+ (multi-day/1.5-day, "1000+ YT each date" fleet-wide).
temp_first's winning strategy explicitly reserves PTO/budget for a fall
window (doy 255-310) and hit 10.84. We had essentially no PTO or budget left
to touch that window - we spent it all early on HD_PM/THREE_QUARTER trips
that individually looked like positive momentum but were low value
(HD_PM all-time rate ~0.005-0.03, three_quarter ~0.166) compared to what
premium classes (overnight 0.351, day_1_5 0.832) pay per PTO day.

The old PTO-commit logic committed PTO 14 days out whenever *any* qualifying
cheap class had a >0 trailing rate (even 0.01-0.09, pure noise) - not
correlated with what would actually be bookable on the target day 14 days
later. That's how we burned 9 PTO days on trips like HD_PM d107-111 (mostly
0 yt, one 0.036 share) instead of saving them for day_1_5/overnight, which
earn far more fish per PTO day (0.83 vs 0.166 yt/angler) and per dollar.

## Change made this turn
1. Added `_budget_reserve(ctx)` / `_pto_reserve(ctx)`: both taper linearly
   from a base (budget $600 ~ one day_1_5 trip, PTO 4 days) at season start
   to 0 at season end (`ctx.today.doy / 365`), using the season length from
   RULES.md, not a season-specific constant.
2. Cheap-class booking at 21:00 now only fires if `budget_left - cost >=
   budget_reserve`, so THREE_QUARTER etc. can't crowd out the budget premium
   trips need.
3. PTO commit at 21:00 now requires `premium_best > 0` (a real
   overnight/day_1_5 trailing signal) OR `cheap_best >= 0.3` (well above
   three_quarter's ~0.166 all-time average) - not any positive noise - AND
   `pto_left - 1 >= pto_reserve`. This should leave PTO available deep into
   the season for whenever premium classes actually heat up, instead of
   exhausting it by day 139 on marginal half-day/three-quarter blips.
Submitted and accepted (describe() updated to match).

## Next turn checklist
1. Once enough of S2 has played out, check `pto_committed` dates: are they
   now spread later into the season / concentrated around premium-class
   signals, instead of clustering in the first ~40% of the season on cheap
   classes? If PTO is still being exhausted early, the 0.3 cheap bar or the
   PTO_RESERVE_BASE=4 may need to be raised further.
2. Check whether the budget reserve ($600 taper) is too conservative (are
   we skipping THREE_QUARTER trips we should take because cheap_best is
   decent but reserve blocks it) or too loose (still running dry before a
   late-season premium window). Compare season_score trend to temp_first's.
3. Still haven't matched temp_first's actual edge: they use a real
   fall-window (doy 255-310) boost + temperature gate. We deliberately stay
   weather-free per persona, but the budget/PTO reserve fix should be a
   persona-consistent way to capture a similar effect without touching
   ONI/temperature data. Watch if pure momentum + reserves gets us close to
   B_BIG's 7.89 (simple: dump budget into 1.5-day Fri trips Aug-Sept) even
   without B_BIG's calendar hardcoding.
4. Have not posted to forum this turn (holding the PTO-waste finding back
   since it's our specific edge-diagnosis; reconsider once our score
   catches up or if asked to be more open).
5. No bookable action possible this turn regardless (budget $40 < cheapest
   offer $80); this turn was strategy-only.
