# Notes (temp_first)

## Season 1, day 1 (t=730.875, doy 90-ish = spring start; doy looks like calendar day-of-year)
- History: seasons -1 and 0 in trips. Shares = yt/anglers per class-date.
- HD/3/4-day boats: ~0 yellowtail almost all year. Offshore (overnight, day_1_5) is where fish are.
- 15-day doy bins, day_1_5 share: peak doy 255-310 (1.7-4.6/angler both seasons); doy 90-105 spike in S-1 (2.9);
  summer 180-230 ~0.3-0.6 in S0. Overnight: doy 285-300 ~3-4.6, otherwise mostly <0.8.
- Pier temp bins vs share: noisy, no clean monotone relation. Temp alone is weak; bite confirmation matters.
- ONI -0.94 (La Nina, cold) at season start.
- Sandbox forbids getattr. DuckDB: "last" and "share" reserved words.

## Strategy v2 (submitted day 61, unchanged through day 122)
- Fall window doy 250-318: book DAY_1_5 (or OVERNIGHT) at 16:00 if offshore bite(6d) >=0.8 & warm, or >=2, or >=1.2 over 3+ boat-days.
- Outside window: need warm AND bite>=2 and keep $1100 reserve.
- PTO: Fri/Mon doy 262-308 14 days ahead if pier 7d >=63F; fallback Fridays doy 268-300 while pto_left>4.

## History of checks
- Day 32/61/92: cold (57-58F), 0 yt everywhere, forum empty, nobody booking.
- Day 122 (doy ~212): pier warming: 7d mean 60.8F, max 63.9F. Last 14d: three_quarter 85 yt/755 anglers (0.11),
  day_1_5 4/59 (0.07), overnight 0/52, hd_am 3. Still no bookings/rejections by me; forum empty. Rank 6, 0 fish.
  Kept v2 unchanged (summer shares too low to spend on).

- Day 153 (t~883): WARM. Pier 7d 66.0F (max 68.7). Last 14d: three_quarter 611 yt/1399 (0.44), last 5d ~0.55
  (0.9 on t=880); overnight 143/286 (0.5) but thin/erratic; day_1_5 0/85; multi_day 71/97. Forum empty; still 0 fish, rank 6.
- v3 submitted day 153: added THREE_QUARTER (books 21:00 on d-1) for weekend/holiday dates only (no PTO) if
  pier>=63 & 5d 3/4 bite>=0.4 over >=3 boat-days; cost must leave $800. Offshore/PTO logic unchanged.
  Cost of 3/4 unknown - check in results.json.

- Day 153 re-run: the arena MCP server failed to connect, so I could not run queries, submit_strategy or forum_post.
  strategy.py on disk is v3, but I COULD NOT CONFIRM the submission. Next turn, first check that the live strategy is v3
  (look for 3/4 bookings or PTO commits in results.json). If it is not, resubmit strategy.py as is.

## Day 183 (doy ~272), arena MCP DOWN again: no queries, no submit, no forum
- v3 WAS live: 1 x 3/4 trip d154, cost $150, 7 yt/52 anglers + 1 competitor = 0.13. Rank 3 season (score 0.13).
- BUG found: OVERNIGHT booking d182 rejected, "'Josie Lynn' not scheduled for OVERNIGHT on d183; scheduled: Pride".
  pick_boat was called with the departure date, but the schedule is keyed by the FISHING date (d+1).
  Fixed on disk (v3.1): uses o.fishing_dates[0], falls back to scheduled_boats. NOT SUBMITTED. SUBMIT FIRST next turn.
- pto_committed is EMPTY even though targets doy 262-308 should have fired since ~day 158. Something in the PTO block
  probably throws and is swallowed by the try/except (maybe d.doy, is_holiday or the CommitPTO signature). Check with
  arena_eval next turn. The window is closing (targets up to doy 308, so committing is possible until ~day 204).
- Offshore go-signal did fire on d182, so the fall bite is on. Forum still empty.

## Day 214 (doy ~303), arena MCP DOWN a third time: no queries, no submit, no forum
- results: 2 x 3/4 trips (d154 0.13, d210 0/44 = 0). Season score 0.13, rank 3. Budget $1700 and PTO 10 are UNUSED
  (d210 was apparently free?). pto_committed still empty, no rejections. forum_new empty.
- strategy.py on disk had been reset to the live v3 (the v3.1 pick_boat fix was gone), so the harness
  seems to overwrite the file with the live version. Edits on disk do NOT go live without submit_strategy.
- Wrote v4 on disk: pick_boat(fishing_dates[0]) + scheduled_boats fallback; late-season (doy>318 or <90) spend mode:
  offshore at bite>=0.5 with no reserve, 3/4 on free days at >=0.25 with no reserve, PTO Fri/Mon to doy 345 while bite>=0.8.
  NOT SUBMITTED. NEXT TURN: submit_strategy first (if strategy.py was reset again, re-apply these edits).
- The PTO bug is still unexplained (no exception visible). Use arena_eval to test today.plus(14).doy/.is_weekend and CommitPTO.

## Day 245 (doy ~334), arena MCP DOWN a 4th time: no queries, no submit, no forum
- Season score 2.55, rank 2 (B_BIG 7.89 on Friday 1.5-days Aug-Sep). Trips: 3/4 d231 0.57, OVERNIGHT d237->238
  39/40 = 0.95 (offshore works; no pick_boat rejection that time), 3/4 d245 45/49 = 0.90. Bite is HOT late
  (3/4 fleet 1.75/angler, offshore 2.14). Budget $1000, PTO 10 unused, pto_committed STILL empty, no rejections.
- PROBLEM with live v3: budget $1000 < $1100 reserve, so it cannot book any offshore trip outside doy 250-318,
  and TQ_RESERVE $800 allows only one more 3/4 trip. Most of the $1000 will go unspent unless v4 goes live.
- Rewrote v4 on disk (file had been reset to v3 again): late mode (doy>318 or <90) no reserves, offshore at
  bite>=0.8, 3/4 on free days at >=0.3; _boat() uses fishing date + scheduled_boats fallback; PTO window to doy 345,
  signal = pier>=63 OR offshore bite>=0.8; CommitPTO wrapped separately so a constructor error falls back to kwargs.
  SUBMIT FIRST next turn (day ~258). If the file got reset again, re-apply.
- Lesson for season 2: the fall bite runs late (doy 320-335 still hot). Do not hold a $1100 reserve past doy 318.
  Friday-evening 1.5-days in Aug-Sep (B_BIG) paid far better than 3/4 days; get PTO commits working early.

## Check next time (day ~183)
- Did 3/4 trips book/reject? Actual cost? Did PTO commits fire (expect from today doy 248)?
- Is the offshore bite (overnight/1.5-day) picking up in the fall window? If the 3/4 bite stays >=0.5, maybe use PTO weekdays for 3/4 too.

## Old check list (day ~152, doy ~242)
- Verify PTO commits start firing (first commit ~doy 248 for target doy 262). results.json pto_committed.
- If pier >=63 by then, warm path activates. Watch three_quarter bite; if it rises >0.5/angler consider adding it as cheap class.
- Competitor dilution: choose boat with larger anglers count.
