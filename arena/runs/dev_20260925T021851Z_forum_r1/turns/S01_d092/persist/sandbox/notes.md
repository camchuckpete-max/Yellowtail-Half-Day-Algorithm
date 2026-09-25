# Notes (persist, S1 d92)

## What happened since d32 turn
- Zero bookings, zero errors, zero PTO committed, budget/PTO fully untouched through day 92 (60 days, 120 ticks).
- Not a crash: the old strategy's PTO commit logic only fired for target = today+14 in doy[150,300], which requires today>=136 - never reached yet by day 92. So no weekday half-day/three-quarter offer was ever bookable (PTO never committed for near-term dates), and the code correctly no-ops when offer.bookable is False. Working as designed, just designed too narrowly.
- Old strategy also never used TWILIGHT (never costs PTO per RULES.md!) or day_1_5/overnight as booking targets at all - pure gap, not intentional.

## Data through day 92 (season 1)
- Total yt fleet-wide by class: day_1_5=5 (doy7, 2 boats: Dominator 2/25, Voyager 3/18), hd_pm=6 (doy35: 2/28=0.071 rate; doy36: 4/24=0.167 rate). Everything else (hd_am, hd_twilight, hd_unspecified, three_quarter, full_day, overnight, multi_day) = 0 so far.
- doy7 catch was before my strategy started (d32 turn), so unreachable anyway. doy35-36 hd_pm bite was real signal but fell outside my PTO peak window and (presumably) on weekdays, so unbookable.
- thrifty's leaderboard strategy text claims "411 YT total vs 33k on premium trips" - this is NOT consistent with current in-game totals (only 11 fish caught fleet-wide through d92), so treat as their own real-world-fishing-domain assumption/hindsight, not verified in-game fact yet. Worth rechecking once overnight/day_1_5 counts actually turn nonzero.

## Strategy submitted this turn
Same "yesterday tells tomorrow" persona, two fixes:
1. Added TWILIGHT as a booking target (16:00 tick, same cheap-classes rate over last 2 days) - free lever, never costs PTO, should have been there from the start.
2. Added PREMIUM_CLASSES (day_1_5, overnight) signal + booking at 16:00 tick (own 3-day trailing rate).
3. Replaced hard doy150-300-only PTO gate with: commit weekday PTO 14 days out if trailing 3-day rate (cheap+premium pooled) > 0 AND target in doy[160,305]; OR trailing rate >= 0.12 outside that window while keeping a 5-PTO reserve. This lets a hot pre-peak bite (like the doy36 0.167 rate) actually get funded instead of being structurally excluded.
- Kept: HD_PM>HD_AM>THREE_QUARTER>FULL_DAY priority for tomorrow's cheap booking at 21:00, hot-rate (>=0.3) weekend/holiday bonus big-trip add-on.

## Next turn checklist
1. Check results.json bookings/rejected_actions - first real test of whether ctx.offer("TWILIGHT")/("DAY_1_5")/("OVERNIGHT") work as expected (field names, bookable flag) and whether the 16:00 hour branch actually fires (confirm ctx.now.hour convention - is 16:00 tick reported as hour==16 exactly?).
2. Check whether any PTO got committed yet (target doy could now be in range once today>=146 for the 160 boundary, or via the outside-peak hot-rate path if another doy35-36-like bite recurs).
3. Watch for day150+ (today doy 92 -> peak window starts mattering once today>=146). Re-verify PEAK_DOY_START=160/END=305 guess against any new data or forum chatter about when the season actually turns on (others reference "July-October").
4. If overnight/day_1_5 counts turn nonzero, revisit whether thrifty's "premium trips" framing was right and whether cheap-trip priority is leaving value on the table vs. going bigger sooner.
5. Still 2 forum posts/month unused - didn't post this turn (nothing to add competitively; the "still all zeros" observation is stale by day92 given doy35-36 already broke the skunk).
