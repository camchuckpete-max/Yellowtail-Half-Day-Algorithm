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

## Day 183 21:00 turn (no-op)
- No change since day 153: budget still $60, cheapest offer still $80, so no booking can ever
  happen again this season. `rejected_actions_and_errors_since_last_turn` is empty, no new
  bookings, no new forum posts (forum_new.json empty). Leaderboard identical to day 153 snapshot:
  persist rank 1 season (1.38) and cumulative; B_PERSIST rank 2 (0.1841, up slightly from 0.1538 —
  copycat HD_PM still picking up occasional small shares); temp_first and thrifty tied rank 3/4 at
  0.1296 each (temp_first's fall window doy 250-318 still hasn't arrived by d183); B_SAT rank 5
  (0.0282); B_TEMP and B_BIG still 0.
- Did not resubmit strategy.py (no code change needed) and did not post to forum (nothing new,
  still leading by a wide margin, no upside to helping competitors converge). 0/2 posts used.
- Nothing left to do this season except confirm final score at season end.

## Day 214 21:00 turn (no-op)
- Same as day 153/183: budget $60 < cheapest offer $80, no booking possible for rest of season 1.
  `rejected_actions_and_errors_since_last_turn` empty, no new bookings since d149 (HD_AM skunk).
  Leaderboard: persist still rank 1 season+cumulative at 1.38; B_PERSIST rank 2 now 0.2348 (up from
  0.1841 at d183, copycat HD_PM keeps picking up small shares slowly); temp_first and thrifty still
  tied rank 3/4 at 0.1296 (temp_first's fall window doy 250-318 hasn't shown results yet even though
  we're now inside it at d214 — worth checking again at season end whether it ever pays off); B_SAT
  rank 5 (0.0431, up slightly); B_TEMP and B_BIG still 0.
- Did not touch strategy.py (no code change possible/needed) or forum (nothing new, 0/2 posts used).
- Lead margin over B_PERSIST (1.38 vs 0.2348) is now large enough that season 1 rank 1 is very
  likely locked in barring some huge late fall bite for others we can't participate in anyway.

## Day 245 21:00 turn — arena tools unavailable, important leaderboard shift
- The `arena` MCP server failed to connect this turn (CONNECTION_CLOSED) — `arena_query`,
  `arena_eval`, `describe_tables`, `submit_strategy`, `forum_post`, `forum_read`, `write_notes` were
  all missing from the toolset. Could not query data, resubmit strategy, or post. Only did what's
  possible with local files (Read/Edit on RULES.md, persona.md, notes.md, strategy.py, results.json,
  leaderboard.json, forum_new.json). **Retry data queries and a possible strategy revision next
  turn** — this is a real gap, not a "nothing to do" turn.
- No booking action was possible anyway: budget_left is still $60, cheapest offer is $80 (half day),
  confirmed again via results.json. rejected_actions_and_errors_since_last_turn is empty.
- **Leaderboard has changed significantly since day 214 and needs attention**: it now shows
  B_BIG at rank 1 with season_fish 7.8918 ("spend the whole budget on 1.5-day trips departing Friday
  evenings in August-September") and temp_first at rank 2 with 2.5469 (water-temp + offshore-bite
  gated strategy, fall window doy 250-318, 1.5-day/overnight when warm water + strong bite). persist
  is now rank 3 at 1.38 — down from believing we were rank 1 in earlier notes (that belief was based
  on a stale/partial leaderboard snapshot; re-verify what leaderboard actually showed at day 214 vs
  now, may have been misread). cumulative_fish is 0 for every agent (season 1 is a practice season,
  doesn't count per RULES.md), so this doesn't cost us anything real, but it's a big signal:
  **a simple "commit the full budget to the highest-value trip class in its known-best seasonal
  window" (B_BIG) or "gate high-value trips on a real environmental signal, not just a 3-day fleet
  reaction" (temp_first) both beat our reactive-3-day-lookback approach by 2-6x.**
- Hypothesis for why we underperformed: our reactive strategy spent budget early and often on cheap
  $80 half-day trips (many skunks: HD_AM d105/112/113/149 all 0 share, HD_PM d126/133 all 0 share),
  burning budget that could have gone to fewer, better-timed, higher-total-yellowtail trips (1.5-day,
  overnight, full-day) where the boat's total catch is what matters, not just "did the class see any
  fish in the last 3 days." Our one big win (THREE_QUARTER d140, share 0.56) shows a real bite can
  pay off huge, but we also caught a bad OVERNIGHT (d146-147, share 0.0286, yt=1/34 anglers) reactively
  rather than because of any actual signal the trip would be good.
- **Next turn priorities (once arena tools reconnect)**:
  1. Re-run arena_query on `trips`/`schedule` to check whether DAY_1_5/full-day/overnight classes have
     structurally better yt-per-angler than half-day/three-quarter classes, and whether there's a
     reliable Aug-Sep Friday 1.5-day seasonal pattern like B_BIG claims (read their forum posts too,
     if any explain the reasoning — forum_read was unavailable this turn).
  2. Consider redesigning strategy.py to bias budget toward fewer, larger, higher-expected-value
     trips (1.5-day/overnight/full-day) in their strongest historical windows, closer to temp_first's
     or B_BIG's approach, rather than spreading $80 half-day bets across every "hot" 3-day window.
  3. This season (S01) can't be changed further regardless (budget stuck at $60, below the $80 floor)
     — any revision is for season 2 onward. Don't burn a turn just confirming that fact again; assume
     it unless results.json shows a budget increase (season rollover).
  4. Double check leaderboard's cumulative_fish=0 pattern — confirm seasons 1 and 2 are both practice
     per RULES.md, so the real test starts season 3; don't overreact to a single practice-season loss,
     but do treat the strategy gap as real and worth closing before the counted seasons.

## Day 275 21:00 turn — arena tools unavailable again (2nd time, same as day 245)
- Same `CONNECTION_CLOSED` failure on the `arena` MCP server as day 245: `arena_query`,
  `arena_eval`, `describe_tables`, `submit_strategy`, `forum_post`, `forum_read`, `write_notes` all
  missing from the toolset again. Confirmed via ToolSearch (no matching deferred tool, explicit
  note that the server failed to connect). This looks like a recurring/persistent issue for this
  sandbox, not a one-off — worth treating "arena tools may be down" as the default expectation for
  a while, and always trying ToolSearch/a direct call early each turn rather than assuming it's
  fixed.
- Worked from local files only (Read on RULES.md/persona.md/notes.md/strategy.py/results.json/
  leaderboard.json/forum_new.json). No new bookings possible anyway: budget_left $60, pto_left 0,
  cheapest offer $80, `rejected_actions_and_errors_since_last_turn` empty. No new forum posts
  (forum_new.json empty).
- Leaderboard unchanged from day 245 snapshot: B_BIG rank 1 (season_fish 7.8918, all-budget-on-
  Fri-1.5-day-Aug-Sep), temp_first rank 2 (6.3755, water-temp + offshore-bite gated), persist rank 3
  (1.38, unchanged — no bookings since d149), B_PERSIST rank 4 (0.3366), thrifty rank 5 (0.1296),
  B_TEMP rank 6 (0.0733), B_SAT rank 7 (0.0598). cumulative_fish still 0 for everyone (season 1
  practice, per RULES.md). Did NOT resubmit strategy.py — with `arena_eval`/`arena_query` down I
  have no way to test a rewrite against past ticks before submitting, and a bad submission risks
  outright rejection ("crash on past ticks") with no way to debug it this turn. Deferred the
  redesign (biasing toward fewer/larger 1.5-day/overnight/full-day trips in strong seasonal windows,
  per day-245 plan) until tools are back and I can validate first.
- **Next turn**: first thing, retry arena tools (ToolSearch or direct call). If back: (1) query
  trips/schedule for DAY_1_5 vs half-day yt-per-angler by month, check the Aug-Sep-Friday claim
  B_BIG's strategy string implies; (2) read forum for any B_BIG/temp_first posts explaining
  reasoning; (3) draft + arena_eval-test a strategy.py rewrite that spends a smaller number of
  larger trips in the best window(s) rather than reactive $80 half-day bets everywhere, before
  submitting; (4) this season (S01) still can't book anything ($60 < $80 floor) so any rewrite only
  matters for season 2 onward — don't burn time re-confirming that, just check budget_left in
  results.json.

## Day 306 21:00 turn — arena tools down a 3rd time (d245, d275, d306)
- Same `CONNECTION_CLOSED` on the `arena` MCP server, confirmed via ToolSearch (explicit "failed to
  connect" note, not just missing). No `arena_query`/`arena_eval`/`describe_tables`/
  `submit_strategy`/`forum_post`/`forum_read`/`write_notes`. This is now 3 of the last 4 recorded
  turns (d245, d275, d306) with the connector down — worth assuming it may still be down at season
  end / season 2 start too, and trying early each turn regardless.
- Local files (results.json/leaderboard.json/forum_new.json) show **no change since day 275**:
  budget_left $60, pto_left 0, season_score 1.38, season_rank 3, cumulative_rank 3,
  rejected_actions_and_errors_since_last_turn empty, forum_new.json empty (0/2 posts used, nothing
  to post anyway). Leaderboard identical: B_BIG 1 (7.8918), temp_first 2 (6.3755), persist 3 (1.38),
  B_PERSIST 4 (0.3366), B_SAT 5 (0.2001), thrifty 6 (0.1296), B_TEMP 7 (0.0733). cumulative_fish
  still 0 for everyone (season 1 practice).
- No action taken: budget $60 is below the $80 floor (cheapest offer, half day) so no booking is
  possible regardless of strategy.py content, and no code change was submitted since arena tools
  (needed to validate against past ticks before submitting) are unavailable. strategy.py is
  unchanged from the day-153 version (reactive 3-day-lookback + seasonality-gated PTO).
- **Season 1 is nearly over (day 306/365) and did not change further** — this is fine since it's a
  practice season (cumulative_fish doesn't count) but the strategy gap vs B_BIG/temp_first (5-6x
  their season score) is real and unaddressed for two turns running now due to tool outages.

## Day 336 21:00 turn — arena tools down a 4th time (d245, d275, d306, d336)
- Same `CONNECTION_CLOSED` on the `arena` MCP server, confirmed via ToolSearch (explicit "failed to
  connect", not just missing). That's 4 of the last 5 recorded turns with the connector down —
  treat "arena tools may be down" as close to the default state near season end, still worth trying
  each turn but don't expect it.
- Local files show **no change since day 306**: budget_left $60, pto_left 0, season_score 1.38,
  season_rank 3, cumulative_rank 3 (cumulative_fish 0 for all, season 1 is practice per RULES.md).
  rejected_actions_and_errors_since_last_turn empty. forum_new.json empty (0/2 posts used, nothing
  to post anyway with tools down). Leaderboard unchanged: B_BIG 1 (7.8918, all-budget-on-Fri-1.5-day-
  Aug-Sep), temp_first 2 (6.3755, water-temp+offshore-bite gated), persist 3 (1.38), B_PERSIST 4
  (0.3366), B_SAT 5 (0.2001), thrifty 6 (0.1296), B_TEMP 7 (0.0733).
- No action taken: budget $60 < $80 floor (cheapest offer), so no booking possible regardless of
  strategy.py; no code change submitted (tools down, can't validate against past ticks before
  submitting — a crash on past ticks gets a submission rejected outright, so don't risk a blind
  rewrite this close to season end for a season that can't book anything more anyway).
- **Season 1 ends at day 365, only ~29 days left and nothing can change our score (1.38, rank 3)
  regardless of strategy.py content.** The day-245 redesign plan (bias budget toward fewer, larger
  1.5-day/overnight/full-day trips in strong seasonal windows, like B_BIG/temp_first) is still
  unexecuted after 4 turns of tool outages — this is now purely a season-2 prep task, not urgent for
  season 1. Don't keep re-deferring it once tools are back though; do it at season-end or season-2-
  start turn, whichever comes first with tools available.

## To check next turn (season end / season 2 start)
- **Top priority**: retry arena tools first thing. If back, actually execute the day-245 plan that's
  been deferred 3 turns now: (1) arena_query trips/schedule for DAY_1_5/full-day/overnight vs
  half-day yt-per-angler by month, check B_BIG's Aug-Sep-Friday 1.5-day claim; (2) forum_read for
  B_BIG/temp_first reasoning; (3) draft + arena_eval-test a rewrite biasing budget toward fewer,
  larger trips in strong seasonal windows (more like temp_first's water-temp+bite gating or B_BIG's
  committed seasonal window) instead of reactive $80 half-day spam; (4) submit only after testing,
  since a crash on past ticks gets the submission rejected outright.
- Confirm final season_score, cumulative_rank at season end.
- Season 2: reset budget $2000/PTO 10. Re-verify the doy 140-141-style bite recurs (was it a real
  early bite or noise specific to season 1?) and whether the season 0/1 doy~271 fall peak estimate
  (from earlier notes) still holds once season 1's full doy 150-365 data is public.
- Re-check whether the scheduled_boats fix actually eliminates OVERNIGHT/DAY_1_5 boat-rejection
  errors in results.json next turn (look at rejected_actions_and_errors_since_last_turn).
- If B_PERSIST or others start adapting past simple HD_PM-copycat behavior, worth a forum read to
  see if any new strategies are gaining ground before season 2.
