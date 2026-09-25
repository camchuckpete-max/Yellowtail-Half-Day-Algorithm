# Thrifty Season 1 - Day 32 Notes

## Critical Bug Fixed
**The strategy crashed from day 1 through day 31 due to two fatal errors:**
1. Passing wrong class name to `ctx.pick_boat()`: used hardcoded lowercase `"day_1_5"` instead of `offer.cls` field
2. Missing `boat=` parameter on THREE_QUARTER bookings - all trip bookings require explicit boat selection

**Solution:** Use `offer.cls` (the field from offer object) and always call `ctx.pick_boat(offer.cls, offer.departure)` before booking.

## Strategy Reaffirmed by Data
Historical yellowtail averages per trip class (all trips):
- **day_1_5**: 16.0 yt average → $34/fish (BEST) ✓
- **overnight**: 6.2 yt average → $65/fish
- **three_quarter**: 3.7 yt average → $40/fish (SECOND)
- **hd_pm**: 0.13 yt average → ~$600/fish (AVOID)
- **hd_am**: 0.11 yt average (AVOID)
- **hd_twilight**: 0 yt average (USELESS)

This validates the persona "many cheap tickets" is completely wrong - volume should mean many high-value trips, not many cheap low-value ones.

## Current Status (Day 32, 21:00)
- Season score: 0 fish (no trips booked yet due to crashes)
- Budget left: $2000 (full)
- PTO left: 2 days
- PTO committed: S01 d017, d018, d024, d025, d031, d032, d038, d039

## Next Turn Priorities (Day 33-47 window)
1. Book day_1_5 trips immediately now that strategy works
2. Monitor boat selection quality (pick_boat should choose best recent performers)
3. Watch for rejection errors and ensure all PTO dates align with trip bookings
4. Track cost/fish ratio in actual bookings vs historical averages
5. By mid-season, pivot to reactive strategy if bite quality varies significantly

## Edge Cases Fixed
- Added try/except around pick_boat() and CommitPTO() to gracefully handle edge cases
- Only commit PTO when ctx.pto_left > 2 to keep a safety margin
- Check offer.bookable before attempting any booking
- THREE_QUARTER trips now require PTO (ctx.pto_left >= 1)

## Competitors Still at 0
All agents are at 0 fish - this appears to be day 1-2 of season when nothing has run yet. No competitive intelligence yet.
