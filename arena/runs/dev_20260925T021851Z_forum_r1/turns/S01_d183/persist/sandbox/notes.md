# Notes (persist, S1 d183)

## Status: rank 1 season (0.6632) and cumulative (0, practice season). Budget_left=$40,
pto_left=1 -> still no bookable action possible for the rest of season 1 (cheapest
offer $80). Nothing to do this turn for season 1 itself; this turn was about
improving strategy.py for when budget/PTO reset (season 2, and season 3+ which
actually counts cumulatively).

## Change made this turn: data-driven boat selection
Previously `_book_if_bookable` used `ctx.pick_boat` (picks the scheduled boat
that ran the class most *frequently* in the last 60 days) with no quality
signal. Queried full-season trips table directly:
- THREE_QUARTER (anglers>100 per boat): San Diego 0.23 yt/angler (516 trips),
  Mission Belle 0.224 (336 trips) vs Malihini only 0.119 (482 trips) - i.e.
  San Diego/Mission Belle are ~2x better than Malihini despite similar trip
  volume, so "most active" != "best". (Small-sample boats like Pacific
  Voyager 0.483/29 trips are noisier, ignore unless sample grows.)
- DAY_1_5 (anglers>50 per boat): huge spread, Penetrator 2.4, Cortez 1.9,
  Ocean Odyssey 1.59 down to Legend 0.76, Endeavor 0.73 - boat choice matters
  a lot here too.
- This matches thrifty's forum post (p00001, season-1 aggregate: San Diego
  585yt/64trips=9.14/trip dominant for 3/4-day vs Malihini 250yt/60trips=4.17).

Fix: added `_best_boat(ctx, offer_cls, fish_day, scheduled)` which pulls
`ctx.observe("trips")`, filters to that offer class's trips-cls set and to
boats currently scheduled, requires >=30 pooled anglers (BOAT_MIN_ANGLERS) to
trust a boat's rate, and picks the max yt/angler among qualifying scheduled
boats. Falls back to `ctx.pick_boat` (or scheduled[0]) when no boat has
enough data yet (e.g. early season). This is recomputed fresh from observed
data every tick, not a hardcoded boat name, so it should be legal (no
season-specific constant) and should adapt if boat quality shifts in a new
season. Submitted and accepted.

## Next turn checklist
1. Once a new season starts (budget/PTO reset to $2000/10), check
   results.json bookings for boat names actually chosen vs what `pick_boat`
   would have chosen - confirm `_best_boat` is actually diverging from the
   old default (e.g. San Diego/Mission Belle over Malihini on THREE_QUARTER)
   and that those bookings show higher yt/angler than the old strategy's
   history at comparable dates. If BOAT_MIN_ANGLERS=30 never gets enough
   trips early in a season for a given class, that's expected (falls back
   to pick_boat) - don't worry until there's real season-to-date volume.
2. Re-check whether OVERNIGHT/DAY_1_5 boat-selection uses fish_day correctly
   (fishing_dates[0], not departure) - this was fixed last turn (d153) and
   `_best_boat` reuses the same `fish_day` passed into `_book_if_bookable`,
   so it should already be consistent, but verify via rejected_actions in
   results.json anyway.
3. Re-derive per-class trailing rates fresh each season - don't assume
   THREE_QUARTER stays the hot class. Historical S1 recap: THREE_QUARTER hot
   ~doy106-136 (rate 0.34-0.66), HD_AM/HD_PM/FULL_DAY near 0 all season,
   OVERNIGHT/DAY_1_5 rates lower/noisier (~0.07-ish when checked, though the
   day_1_5 per-boat table above shows big variance so pooled-class rate may
   understate the best boats - could eventually consider per-boat trailing
   momentum, not just per-class, if per-boat daily samples turn out large
   enough; skipped this turn to keep the change small and testable).
4. Still haven't posted to forum (2 posts/month unused). thrifty already
   posted full aggregate stats (season-1 class + boat rankings) after our
   win - so our boat-quality edge is now semi-public anyway. Still leaning
   against posting further detail ourselves while in the lead; revisit if a
   forum post reveals something we're missing rather than confirming what we
   already found.
5. Consider (not done this turn): PTO_RESERVE=1 may be too aggressive right
   after a season reset when 10 fresh PTO days are available and early
   signal is noisiest - could raise the reserve for the first ~30 days of a
   season and taper down. Left unchanged this turn to isolate the boat-
   selection change; test in isolation next time if there's a clean before/
   after comparison to make.
