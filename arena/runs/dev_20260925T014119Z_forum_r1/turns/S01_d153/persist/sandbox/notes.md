## Day 153 checkpoint (this turn)
- Rank 1 season and cumulative, season_score 1.38 (up from 0.3376 at day 122). Big wins since
  then: THREE_QUARTER d140 (yt=28/49 anglers, share 0.56) and d141 (yt=11/44, share 0.244) — a real
  fall-ish bite the reactive rule caught within a day of it starting. Also small OVERNIGHT d146-147
  (share 0.0286) and several skunks (HD_AM d112/113/149, HD_PM d126/133) that cost $80 each but the
  strategy correctly keeps chasing since a "hot" class only needs a positive recent sum, not a
  guaranteed hit.
- Budget left is now $60, all trip classes cost >= $80 (half day $80 is cheapest), so **no offer
  can ever be bookable again this season** — the existing `offer.cost > remaining_budget` guard
  already makes decide() a no-op for bookings from here on. Confirmed via RULES.md price table, no
  need to keep re-checking each turn; season score is locked at 1.38 barring any refunded trip
  turning into extra share (won't happen, refunds just return fare, no share). PTO left (2 days)
  is now moot too since nothing is affordable — don't bother committing more.
- Bug found: two rejected OVERNIGHT bookings (d133->d134 fish date, d140->d141 fish date) because
  `ctx.pick_boat` returned "Legend", a boat not actually scheduled for OVERNIGHT those dates
  (confirmed via `arena_query` on `schedule` table: zero rows for OVERNIGHT cls in doy 130-145 —
  the route just wasn't running). pick_boat's "ran that class most in last 60 days" default must
  fall back to stale/cross-window data when nothing is currently scheduled. Harmless this time
  (rejected actions cost nothing) but wasted a would-be booking slot. Fixed by adding a
  `ctx.scheduled_boats(cls, departure)` check before booking: skip (don't book) if the picked boat
  isn't in the current scheduled list. Submitted and accepted this turn. Worth double-checking next
  season whether this actually prevents the rejection pattern, and whether pick_boat's behavior is
  a known quirk worth asking about on forum if it recurs a lot for OVERNIGHT/DAY_1_5 specifically.
- Leaderboard: B_PERSIST still rank 2 at 0.1538 (unchanged, HD_PM copycat, hasn't updated).
  Everyone else (B_SAT, B_TEMP, B_BIG, temp_first, thrifty) still at 0 as of last snapshot —
  temp_first and thrifty are waiting for their doy 250-318 fall window which hasn't arrived yet at
  day 153. Our reactive approach is clearly outperforming by not waiting for a named seasonal
  window and instead just following the last 3 days of fleet catches everywhere, including the
  d140-141 bite that started well before doy 250.
- Did not post to forum this turn — nothing new worth surfacing (still leading by a wide margin,
  no reason to help competitors converge on the reactive approach), and budget is now irrelevant
  for us so no urgency either way. 0/2 posts used this month.

## Day 153 21:00 turn (no-op)
- Confirmed budget $60 < cheapest offer $80 (half day). No bookable offers possible for the rest
  of season 1, no matter what strategy.py says. Did not resubmit — no code change needed, current
  file already handles this fine (offer.cost > remaining_budget guard).
- rejected_actions_and_errors_since_last_turn is empty: the scheduled_boats() pre-check added last
  turn worked, no more OVERNIGHT/DAY_1_5 boat-rejections since. Good, confirms the fix.
- Leaderboard unchanged: persist rank 1 season (1.38) and cumulative; B_PERSIST rank 2 (0.1538,
  still copycat HD_PM, hasn't adapted); everyone else (B_SAT, B_TEMP, B_BIG, temp_first, thrifty)
  still 0. temp_first's fall window (doy 250-318) and thrifty's approach haven't paid off yet as of
  d153 — worth checking at season end whether they catch up once fall actually arrives.
- No new forum posts (forum_new.json empty). Didn't post — nothing new to say, still comfortably
  leading, no upside to helping competitors converge faster. 0/2 posts used this month, same as
  last turn.

## To check next turn (season end / season 2 start)
- Confirm final season_score, cumulative_rank at season end.
- Season 2: reset budget $2000/PTO 10. Re-verify the doy 140-141-style bite recurs (was it a real
  early bite or noise specific to season 1?) and whether the season 0/1 doy~271 fall peak estimate
  (from earlier notes) still holds once season 1's full doy 150-365 data is public.
- Re-check whether the scheduled_boats fix actually eliminates OVERNIGHT/DAY_1_5 boat-rejection
  errors in results.json next turn (look at rejected_actions_and_errors_since_last_turn).
- If B_PERSIST or others start adapting past simple HD_PM-copycat behavior, worth a forum read to
  see if any new strategies are gaining ground before season 2.
