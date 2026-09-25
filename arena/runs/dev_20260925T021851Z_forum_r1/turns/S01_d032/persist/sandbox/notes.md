# Notes (persist, S1 d32)

## State at this turn
- Season 1, day 32, 21:00. Budget $2000, PTO 10 — completely untouched, first real strategy submitted this turn (was "books nothing").
- Checked trips table for all of season 1 so far (doy 13-32): yt = 0 on every single row, every class (hd_am/hd_pm/hd_twilight/three_quarter/day_1_5/overnight/multi_day). Total skunk so far. Consistent with cold water: ONI -1.02 (La Niña), PDO -2.4, MEI -1.18 as of latest readings (doy ~9-21). Persona says ignore weather, but this explains why signal is silent.
- Leaderboard: everyone (including me) at 0 fish, season 1 treated as practice anyway. B_PERSIST is already running almost exactly my planned naive strategy ("book tomorrow's PM half day if today's pooled half-day count > 0") — need to differentiate, not just copy.

## Strategy submitted this turn
"yesterday tells tomorrow" — momentum reactive:
- Signal = pooled yt/anglers over trips fished in the last 2 days, classes hd_am/hd_pm/hd_unspecified/hd_twilight/three_quarter.
- If signal > 0: book next bookable offer via ctx.offer() in priority HD_PM > HD_AM > THREE_QUARTER.
- If signal >= 0.3 (hot) and that offer's departure is weekend/holiday: also book a THREE_QUARTER/FULL_DAY offer (no extra PTO cost).
- PTO: at the 21:00 tick only, look at today+14 days; if it's a weekday, doy in [150,300] (peak local season window), and pto_left > 2, CommitPTO it. This drips PTO into the peak window ahead of time so weekday offers there have a chance of being bookable when a bite actually shows up, while keeping a 2-day reserve.

## Untested assumptions to check next turn (results.json / rejected_actions will tell us)
- Exact Offer object field names (id, cls, departure, bookable) and whether ctx.offer(name) is really the right accessor vs needing to scan ctx.offers by departure==tomorrow. If CommitPTO or Book calls show up in rejected_actions_and_errors, read the reason carefully — likely field/attribute mismatch.
- Whether ctx.observe("trips") returns a DataFrame or list-of-dicts — code handles both but hasn't been run against the real sandbox yet.
- Whether duplicate CommitPTO calls for the same date (if logic re-fires) get silently deduped or double-charge PTO — I only fire the PTO logic at hour==21 to cut this risk in half, but same date could still recompute across consecutive days pointing at different target dates, so should be fine; just double check pto_committed count in next results.json isn't running ahead of expectations.
- Once yt counts turn nonzero anywhere, check which class first shows signal (AM vs PM vs twilight) — if PM lags AM by season progression, may want to broaden HALF_DAY_PRIORITY or check within-day recency rather than pooling AM+PM+twilight+3/4 together (right now a single hot AM day would trigger a PM booking too, which might be fine or might be double counting the same bite window).

## Next turn checklist
1. Check results.json for rejected actions from this strategy — fix any attribute errors first.
2. Check if yt counts have gone above 0 anywhere yet (esp. as doy approaches 150+).
3. Compare my season_score vs B_PERSIST / B_SAT once real fish start counting (season 1 may still be practice-only, doesn't count toward cumulative, but good to validate the code path works).
4. Consider forum: nothing posted yet, still have 2 posts/month available. Could share the "still all zeros, cold ONI" observation once useful, or hold back since it doesn't help me competitively to tip others off.
