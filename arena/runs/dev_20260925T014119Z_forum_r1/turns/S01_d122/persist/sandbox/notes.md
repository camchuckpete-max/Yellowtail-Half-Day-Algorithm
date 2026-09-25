## Day 122 checkpoint (this turn)
- Rank 1, season_score 0.3376 (cumulative still 0, seasons 0/1 are practice). Bookings since day 92:
  HD_AM d105 (yt=0), HD_AM d106 (yt=3/37 anglers, share 0.0789), HD_AM d112 (yt=0), HD_AM d113
  (yt=0), THREE_QUARTER d119 (yt=2/34, share 0.0571), THREE_QUARTER d120 (yt=1/20, share 0.0476).
  Matches historical small doy~100-120 bump confirmed present in season 1 too (was open question
  at day 92 checkpoint) — good, season 1 tracking season 0's shape.
- Bug found and fixed this turn: on d111/d112 ticks, multiple classes (HD_AM, HD_PM,
  THREE_QUARTER) were simultaneously "hot" and the old loop tried to book all of them for the same
  fishing date, causing 4 rejected "already booked for that fishing date" actions (harmless, no
  budget/PTO cost, just log noise + arbitrary which class actually got booked via ctx.offers
  iteration order). Fixed: loop now sorts ctx.offers by cost ascending and tracks claimed
  departure dates, booking at most one (the cheapest) hot offer per date. Submitted and accepted.
  describe() had to be trimmed to fit the 200-word cap after adding this.
- Re-verified PEAK_FRACTION gate with fresh data: best window is doy 271 (rate 43.4), target doy
  at this turn (122+14=136) has rate only 1.5 — nowhere near 0.5*43.4=21.7, so PTO correctly still
  not firing. pto_left=2, budget_left=$1300. No rush; PTO_LEAD=14 means the gate should start
  passing once today's doy is roughly 246+ (target doy ~260). Season 1 real data only goes to
  doy 122 so far, so the doy-271 estimate is still purely historical (season 0 + prior seasons);
  worth rechecking once season 1 itself starts showing a rise past doy ~150-200 to confirm the
  same peak location, in case season-1-specific data shifts the estimate before the PTO gate fires.
- Did not post to forum (0 used of 2 available this month) — no new info worth surfacing yet, and
  staying quiet avoids feeding B_PERSIST-style copycats who already mirror our HD_PM idea. Forum
  had zero new posts since last turn (forum_new.json empty); haven't re-read the full forum this
  turn to save budget, but leaderboard.json's strategy blurbs already give the competitive
  picture: B_PERSIST unchanged (0.1538), everyone else still 0. temp_first and thrifty both name
  a doy 250-318 fall window, consistent with our doy 260-290 estimate — three independent
  approaches converging on the same fall bite window is a good cross-check.

## To check next turn (~day 136-150)
- Confirm the dedupe fix actually eliminated the redundant-rejection pattern (check
  rejected_actions_and_errors_since_last_turn — should be empty or much shorter now).
- Watch for season 1's own doy 150-250 trend starting to show up (season 0 had a ~doy 190-210
  bump at rate ~5, well below the doy~271 peak) — if season 1 diverges from season 0's shape here,
  may need to re-scan the peak-window estimate rather than trusting the day-92 scan.
- PTO: still expect no commits until today's doy is roughly 240s (target doy in the 254+ range
  starts clearing the 0.5*best gate, assuming best stays ~43 at doy 271). Recheck the live
  best-rate scan each turn since it's computed fresh from public data and could shift as season 1
  adds real points into that window before we get there.
- Watch B_PERSIST (still 0.1538, purely HD_PM copycat) and temp_first/thrifty (both targeting the
  fall window, still 0 — no signal there yet since it's out of range).
