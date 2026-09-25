# Season 1 Final Review & Season 2 Strategy

## Season 1 Outcome (Day 214)
- **Final Score**: 0.1538 (Rank 3/7 agents)
- **Total Fish**: 4 YT from 11 trips ($1,960 spent)
- **Frozen**: Day 71 onward—unable to book (budget $40, PTO 0)
- **Gap to Winner (persist)**: 0.1538 vs 0.6632 = **4.3x behind**

## Root Cause Analysis
My strategy was **too conservative**:
- Required 3-day trailing rate > 2.0-3.0 per angler
- This threshold almost NEVER hit in real data
- Strategy never triggered meaningful bookings after initial failures
- Result: sat on hands watching hot days 144-151 pass (184 YT on day 144 alone)

## Persist's Winning Formula
- Tracked 2-3 day signals (not 7-day averages)
- Booked on **ANY positive rate** (not high thresholds)
- Prioritized cheap classes (half-day) first, then premium
- Committed PTO 14 days ahead proactively
- Caught momentum: if yesterday was hot, book today

## Season 1 Data Reality
- Half-days: 752 total trips, only 26 YT (0.03/trip average)—BUT highly variable by date
- 3/4-day: 234 trips, 1,055 YT (4.51/trip)—strong and consistent
- My one success (d036 half-day, 4 YT) proved timing > class type
- My failures (d64, d71 three-quarter & 1.5-day): picked right class, wrong dates

## Season 2 Strategy (Now Submitted)
**Core shift**: Reactive momentum like persist, but with volume bias.

1. **Signals**: 2-3 day trailing YT/angler by class (separate calculation per class)
2. **Threshold**: Book on ANY non-negative signal (no minimum rate)
3. **Priority order**: Cheap half-days first (my persona), then premium classes
4. **Booking**: Tomorrow's offer for the highest-ranked available class
5. **PTO**: Commit 14 days ahead when booking premium trips
6. **Reserve**: Hold only $200 minimum (was $1200—too conservative)
7. **Boats**: Proven boats for 3/4-day (San Diego/Malihini), ctx.pick_boat otherwise

## What Changed
- Removed high threshold (>2.0)—now book on >= 0 signal
- Lowered reserve from $1200 to $200—capital now flows, not stockpiles
- Swapped 7-day to 2-3 day windows—faster reaction to hot dates
- Added priority order—volume first, premium when needed
- PTO commitment now proactive (on any positive momentum)

## Key Metrics to Track Next Season
- Books per month (should be 15-20 vs Season 1's ~11 total)
- Hit rate by class (which dates are actually hot?)
- Reserve usage (did $200 minimum prove too low?)
- Budget depletion curve (should be smoother, not frozen at day 71)

## Known Risks & Fallbacks
- 2-3 day signals can be noisy (one boat catches, others don't)
  → Mitigation: still book—volume catches variance
- No weather/temp data (persist doesn't use it either)
- Can't predict multi-week cold spells
  → Mitigation: stop booking naturally if all classes go negative for 3+ days

## Success Target for Season 2
- **Minimum**: 0.3 score (2x Season 1)
- **Target**: 0.5+ score (approaching persist's 0.66)
- **Path**: ~25 half-day bookings + 5-8 premium trips, spread across year
