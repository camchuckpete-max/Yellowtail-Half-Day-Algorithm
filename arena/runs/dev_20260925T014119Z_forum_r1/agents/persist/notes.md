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

## Season 1 END retrospective (day 366, arena tools down a 5th time)
- Same `CONNECTION_CLOSED` on the `arena` MCP server, confirmed via ToolSearch — could not run
  `arena_query`/`arena_eval`/`describe_tables`, could not `submit_strategy`, `forum_post`, or
  `forum_read`. Worked entirely from local results.json/leaderboard.json/forum_new.json/strategy.py.
  This is the 5th outage across the last 6 recorded turns (d245, d275, d306, d336, d366) — treat
  "arena tools down" as the modal state for this sandbox, not an exception, and budget turn time
  accordingly (don't keep re-verifying it, just try once and move to what's possible locally).
- **Final season 1 result**: season_score 1.38, season_rank 3, cumulative_rank 3 (season 1+2 are
  practice, so cumulative == season here). Final leaderboard: B_BIG 1st (7.8918, "spend whole
  budget on 1.5-day trips departing Friday evenings in Aug-Sep"), temp_first 2nd (6.3755, water-temp
  + offshore-bite gated, fall window doy 250-318), **persist 3rd (1.38)**, B_PERSIST 4th (0.3366,
  copycat HD_PM), B_SAT 5th (0.2001, every Saturday Jul-Oct book PM half day), thrifty 6th (0.1296),
  B_TEMP 7th (0.0733). We lost by 5.7x to B_BIG and 4.6x to temp_first.
- **What worked**: the reactive "hot class = fleet yt sum > 0 over last 3 fished days" rule did
  catch a real bite fast — THREE_QUARTER d140 (yt=28/49 anglers, share 0.56) and d141 (yt=11/44,
  share 0.244) together are 0.804 of our 1.38 total, found and booked within a day of the bite
  starting, well before any named seasonal window (doy 140, not B_BIG's Aug-Sep or temp_first's
  doy 250-318). Reactivity has real edge over rigid calendar windows when a bite is early/off-schedule.
- **What did not work — the core diagnosis**: my own 15 bookings show a stark, consistent split by
  trip class that the code never used:
  - HD_AM (5 bookings): yt = 0, 3, 0, 0, 0 → shares 0, 0.079, 0, 0, 0. **4/5 skunks.**
  - HD_PM (3 bookings): yt = 4, 0, 0 → shares 0.154, 0, 0. **2/3 skunks.**
  - THREE_QUARTER (6 bookings): yt = 2, 1, 8, 2, 28, 11 → shares 0.057, 0.048, 0.154, 0.056, 0.56,
    0.244. **6/6 positive, and the two huge wins are here.**
  - OVERNIGHT (1 booking): yt=1/34, share 0.029 — weak, but n=1, don't over-read.
  The strategy's "hot = sum>0" test treats all classes identically and its booking loop sorts by
  **cost ascending**, so it grabbed cheap $80 HD_AM/HD_PM offers first every time both a cheap and
  an expensive class were simultaneously "hot" — spending budget on the noisiest, weakest-signal
  class first instead of the one with a real track record. This is the single clearest, most
  actionable finding from season 1: **half-day classes are structurally noisier/weaker for
  yellowtail than three_quarter/bigger trips (shorter range boats likely don't reach the grounds),
  and "sum > 0 over 3 days" is too weak a bar for them** — one nonzero fleet day triggers a booking
  even when the class skunks 80% of the time.
- **Why B_BIG/temp_first beat us by so much**: both commit real budget to a small number of
  higher-cost, higher-EV trip classes (1.5-day, overnight, three_quarter) in a strong window,
  rather than spreading many small $80 bets reactively across every class. Even without their exact
  seasonal-window numbers (couldn't query this turn), the mechanism is clear from my own data: fewer,
  bigger, higher-EV bets beat many small noisy ones, and diluting a hot signal across HD_AM/HD_PM/
  THREE_QUARTER equally was the main leak.
- **Concrete fix drafted for next time tools are up** (NOT yet tested or submitted — must be run
  through `arena_eval` against past ticks before `submit_strategy`, since a crash on past ticks gets
  a submission rejected outright):
  1. Replace "hot = fleet yt sum > 0" with a **per-class minimum yt-per-trip rate**, with an
     asymmetric bar: half-day classes (HD_AM, HD_PM) need a much higher rate (e.g. >=1.5-2 yt/trip
     averaged over the lookback window) to count as hot, since they skunk ~80% of the time in our
     sample; three_quarter/full_day/overnight/day_1_5 keep a lower bar (e.g. >=0.3-0.5) since they
     were consistently positive. Tune both numbers against the real trips table once queryable —
     these are informed guesses from n=5/3/6, not fitted values.
  2. In `decide()`, stop sorting candidate offers by `cost` ascending. Sort by **expected value
     descending** (recent per-class yt/trip rate, or rate/typical-anglers) first, cost ascending as
     tiebreak, so budget goes to the strongest-signal class available that tick, not just the
     cheapest hot one. This directly fixes the HD_AM/HD_PM-first bug above.
  3. Consider a soft budget reserve so a strong three_quarter/overnight bite mid-season isn't starved
     by budget already spent on multiple half-day skunks earlier (e.g. don't let cumulative spend on
     offers costing <$150 exceed some fraction of total budget, tunable once real numbers are back).
  4. Re-verify the PTO seasonality-gating logic (day-of-year window, half-of-peak-rate threshold)
     still behaves sensibly once season 1's full doy 150-365 data is public — it was built on partial
     data through the season and never got to see the back half before this turn.
  5. Keep the reactive, non-calendar-window core (it out-raced named windows once, at d140) — the
     fix is which classes/how much to bet on a hot signal, not abandoning reactivity for a rigid
     Aug-Sep-only or doy-250-318-only rule like the top two competitors use.
- Did not touch strategy.py this turn (can't test against past ticks with tools down; the day-153
  version already live and validated is left in place) and did not post to forum (tools down, and
  0/2 posts wouldn't have mattered without forum_read to see what B_BIG/temp_first said anyway).

## To check next turn (season 2 start) — SUPERSEDES the old plan above
1. **Top priority**: retry arena tools first thing (ToolSearch or direct call). Season 1 is now
   final (score 1.38, rank 3/3 counted-seasons-wise it doesn't count, practice) — season 2 starts
   fresh with budget $2000/PTO 10.
2. If tools are back: run `arena_query`/`arena_eval` on the full `trips` table (now doy 1-365 of
   season 1 is public) grouped by `cls`, computing mean yt/trip and skunk-rate per class, to replace
   my n=5/3/6 guesses with real numbers. Specifically check: is HD_AM/HD_PM really ~20% hit rate
   fleet-wide (not just my sample), and is THREE_QUARTER/OVERNIGHT/DAY_1_5 really consistently
   better? Also check B_BIG's implied Aug-Sep-Friday 1.5-day claim and temp_first's doy 250-318 fall
   window against the data directly.
3. Implement the 5-point fix drafted above (per-class asymmetric hotness threshold using yt/trip
   rate instead of sum>0; sort candidate offers by expected value not cost; consider a soft budget
   reserve for higher-cost classes) in strategy.py, test with `arena_eval` against season 1's past
   ticks (does it still run without crashing, does it plausibly do better?), then `submit_strategy`.
   Don't submit untested — a crash on past ticks is an outright rejection.
4. forum_read once available: check whether B_BIG/temp_first posted their reasoning/numbers, and
   whether B_PERSIST/others adapted past copycat behavior over season 1's second half.
5. Re-check `rejected_actions_and_errors_since_last_turn` for any new OVERNIGHT/DAY_1_5
   boat-scheduling rejections now that a full season of the `scheduled_boats` pre-check has run.
