
# Notes (persist) — Season 1 retrospective, written at season end (d366)

## Final S1 result
season_score=0.6632, rank 3/7. Leaderboard: temp_first 10.84 (1st), B_BIG 7.89
(2nd), us 0.66 (3rd), B_PERSIST 0.34, B_SAT 0.20, thrifty 0.15, B_TEMP 0.07.
We beat all the naive baselines but lost badly to temp_first and B_BIG.

## What actually happened (traced from results.json bookings)
17 bookings total, ALL between d95 and d136. Spent $1960 of $2000 and 9 of 10
PTO days by d139. Zero bookings for the remaining ~230 days of the season
(d136-365) — not because the strategy stopped trying, but because budget hit
$40 (below the $80 cheapest fare) and PTO was down to 1. The season was
effectively over for us by day ~136, regardless of what happened later in the
data (fleet-wide "fish explosion" reportedly hit d230+/d273+/d280+ per other
agents' strategy descriptions — we had nothing left to spend when it came).

Breakdown of the $1960: 1 twilight ($80, 0 yt), 11x HD_PM ($880, ~all 0 yt,
one 0.036 share) — this was the strategy chasing 2-3 day trailing "momentum"
on a class that turned out to be structurally weak (all-time HD_PM rate
~0.005-0.03) before the all-time viability filter had enough cumulative
samples (200 anglers) to exclude it. Then 4x THREE_QUARTER ($600, decent:
0.08+0.06+0.056+0.43 shares) and 1x OVERNIGHT ($400 on a weak 0.07 trailing
signal, 0 yt) — a single premium trip taken on a barely-positive rate, using
$400 of the $2000 budget for nothing.

## Root causes identified (in priority order)
1. **No real floor stopping total resource exhaustion before a real signal
   appeared.** The old budget/PTO reserve tapered *linearly* with days left
   and was too small (BUDGET_RESERVE_BASE=600, PTO_RESERVE_BASE=4) — by
   d136 (~63% of season left) the reserve had already decayed to ~$375 /
   ~2.5 PTO, not enough to stop the bleed from 15 cheap/exploratory bookings.
   We ran the tank dry with roughly two-thirds of the season still ahead.
2. **PTO was being spent on cheap-class signals at all** (the old
   `cheap_best >= 0.3` OR-branch). Premium classes pay far more fish per PTO
   day (overnight ~0.35, day_1_5 ~0.83 vs three_quarter ~0.17 per prior
   analysis), so any PTO spent on a cheap-class signal was likely negative
   EV relative to holding it for a premium opportunity that might come later.
3. **Any positive trailing rate (even 0.01-0.07) was enough to trigger a full
   premium booking** ($400-550) or a PTO commit. That's noise, not signal,
   especially given premium classes run on small angler counts per boat, so
   a single higher-than-usual boat can swing the 3-day rate a lot.
4. Never tested weather/temperature/ONI (per persona, intentionally) — the
   winner, temp_first, gates on Scripps Pier temp >=59F plus a fall-window
   (doy 255-310) boost. We deliberately stayed pure-momentum; the fix this
   turn tries to capture a similar "protect resources for the real window"
   effect through reserve discipline instead of a calendar/weather gate,
   which fits the persona better but is a real bet — worth checking if it's
   enough or if temp_first's approach is just structurally superior.

## Change made this turn (submitted, accepted)
1. Removed the cheap-class PTO-commit path entirely — PTO 14 days out is now
   committed ONLY when a premium (overnight/1.5-day) trailing rate is real
   (>= MIN_PREMIUM_RATE = 0.15), never on cheap-class noise.
2. Raised that same 0.15 bar for premium *booking* too (16:00), replacing
   the old "any positive rate" trigger — so a single weak boat doesn't burn
   $400-550 on noise.
3. Added MIN_SAMPLE_ANGLERS=15: if a trailing window's rate is built from
   fewer than 15 angler-counts, treat it as 0 (unproven), rather than let a
   tiny sample swing a big decision.
4. Lowered CLASS_MIN_ANGLERS from 200 to 150 (excludes a proven-bad class
   like HD_PM slightly sooner, cutting exploration losses).
5. Raised BUDGET_RESERVE_BASE 600->900 and PTO_RESERVE_BASE 4->7, and
   changed the taper from linear (`frac_left`) to `frac_left ** 0.5`
   (sqrt) — this keeps the reserve much higher for most of the season and
   only lets it shrink fast near the very end, instead of leaking away
   proportionally to time from day 1.
6. describe() updated to match; submission accepted without errors.

## Next turn checklist (for whoever/whatever reads this next, likely me)
1. Once S2 has played out a while, check bookings/pto_committed timing: are
   we now still holding budget/PTO past day ~150-200, instead of exhausting
   by day 136 like S1? If we're still going broke early, the reserve base
   or the sqrt exponent needs to go up further (try frac_left**0.3 for an
   even flatter early curve, or raise BUDGET_RESERVE_BASE toward 1200).
2. Check whether MIN_PREMIUM_RATE=0.15 is too strict (never fires, season
   ends with huge unused budget/PTO and score near 0) or still too loose
   (fires on noise again). Tune against how S1's actual premium rates
   looked once more data is visible via arena_query on the trips table.
3. Compare season_score trend against temp_first and B_BIG's cumulative
   score — if reserve discipline alone still leaves us far behind, that's
   evidence the persona's no-weather constraint is a real handicap, worth
   flagging honestly in a forum post or to whoever reviews personas.
4. Did not post to forum this turn (budget-conscious; the retrospective/fix
   is captured here privately). Consider posting once S2 data shows whether
   the reserve fix worked, so the finding (linear taper was the real S1
   killer, not the momentum logic itself) is useful to others too.
5. No bookable action was taken this turn (season-end, strategy-only turn;
   budget was $40, below the cheapest $80 fare, and this was the mandated
   retrospective turn anyway).
