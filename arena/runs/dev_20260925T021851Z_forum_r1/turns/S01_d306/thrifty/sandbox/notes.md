# Season 1 Final Analysis & Season 2+ Strategy

## Season 1 Outcome
- **Final Score**: 0.1538 (Rank 6/7)
- **Total Fish**: 4 YT from 11 trips ($1,960 spent, $40 left)
- **Winner (temp_first)**: 10.84 fish
- **Gap**: 7x behind winner

## Critical Discovery: Seasonal Windows Trump Everything

### Data Pattern (Season 1 actual catches):
| Period | Days | Avg Temp | YT/Angler | Total YT | Status |
|--------|------|----------|-----------|----------|--------|
| Dead zone | d1-71 | 58.4°F | 0.001 | 10 YT | WORTHLESS |
| Early warmup | d72-107 | 58.9°F | 0.183 | 2,474 YT | **180x better** (temp barely changed!) |
| Mid-season | d150-185 | 65.4°F | 0.146 | 6,464 YT | Good |
| Fall early | d240-275 | 63.9°F | 0.748 | 40,982 YT | Excellent |
| Fall peak | d275-306 | 64.4°F | 1.584 | 38,648 YT | **Peak of season** |

**Key insight**: Day d72 shows catches jump 180x over d35-70 at nearly identical temperature (58.9°F vs 58.6°F). This proves **day-of-year seasonal timing > temperature absolute values**.

### Why I Lost
My d35-71 bookings yielded 0 YT. The peak d240-306 period yielded 1.584 YT/angler and I missed it entirely. I booked nothing in the fall.

## Season 2 Strategy Changes

### Primary Gate: Seasonal Windows (not temperature)
- **Avoid d1-71**: Dead zone, 0.001 YT/angler - no bookings
- **Consider d72-107**: Early warmup, 0.183 YT/angler - cheap second chances
- **Target d240-310**: Fall peak, 0.75-1.6 YT/angler - deploy capital here
- Decision rule: `if doy < 72: don't book; if doy >= 240: book aggressively`

### Reserve Strategy
- **d1-239**: Hold $600 minimum (don't waste in dead/weak zones)
- **d240-365**: Drop to $200 minimum (deploy aggressively in peak)
- **Rationale**: Early season is almost worthless; save for proven peak

### Secondary Gate: Proven Classes (unchanged)
- Classes: day_1_5, overnight, three_quarter
- Signal: Recent 3-day YT/angler per class
- Book best-performing class with positive momentum

### PTO Strategy
- Commit 14 days ahead ONLY for fall window (d240-310)
- On d226, start committing weekday PTO for d240+ trips
- Early season (d1-239): avoid PTO except free weekend trips

### Boat Selection (unchanged)
- 3/4-day: prefer San Diego/Malihini (historically best for this class)
- Others: pick_boat (scheduled boat with best recent rate)

## Lessons for Future Seasons
1. **Seasonal timing is primary**: Calendar day matters more than weather indices
2. **Capital conservation**: Spending $1,960 to get 4 YT (4 fish, $490/fish) is worse than getting zero fish and saving for the real season
3. **Peaks are predictable**: Fall (d240-310) consistently shows 100x better catch than spring (d35-71)
4. **Early bookings were pure cost**: Every trip d35-71 was a sunk $80-550 that could have gone to one fall trip
5. **Reserve management is critical**: Don't let budget depletion trap you in early season

## Data Available But Unused in Season 1
- Pier: Scripps water temp (hourly, has predictive power but secondary to doy)
- Fishdope: Daily fish reports (yt_local, yt_coronado, yt_north)
- Ocean: SST, currents, chlorophyll by zone
- Upwelling: CUTI/BEUTI indices (may correlate with doy peaks)
- Climate: ONI, PDO indices (seasonal climate state)

Future investigation: do ONI/PDO correlate with peak d240-310? Does CUTI/BEUTI confirm upwelling during fall?

## Next Season Goals
- **Minimum**: 1 fish (1.0 score, beat all half-day volume strategies)
- **Target**: 3-5 fish (beat persist at 0.66, aim for B_PERSIST level)
- **Stretch**: 7-10 fish (beat B_BIG at 7.89, compete for top)

### Key Actions for Day 1
1. Do NOT book anything d1-71
2. Watch d72-107 period for early signal; book cheap half-days if signal strong
3. Commit PTO on d226 for d240+ trips
4. On d240, book aggressively: three_quarter, overnight, day_1_5 in rotation
5. Target 3-5 premium trips in fall window (cost $1,200-2,000)

## Season 1 Trip Breakdown (Post-Mortem)
- d035 PM: $80, 0 YT (within dead zone)
- d036 PM: $80, 4 YT (lucky outlier, only fish before d240)
- d043 PM: $80, 0 YT (within dead zone)
- d049 PM: $80, 0 YT (within dead zone)
- d050 PM: $80, 0 YT (within dead zone)
- d056 PM: $80, 0 YT (within dead zone)
- d057 PM: $80, 0 YT (within dead zone)
- d062-63 DAY_1_5: $550, 0 YT (premium wasted in dead zone)
- d064 THREE_QUARTER: $150, 0 YT (premium wasted in dead zone)
- d069-70 DAY_1_5: $550, 0 YT (premium wasted in dead zone)
- d071 THREE_QUARTER: $150, 0 YT (premium wasted in dead zone)

**Total cost for 0 YT (d35-71)**: $1,930. Opportunity cost to fall peak: ~$1,930 × 1.5 YT/angler ÷ (11 anglers/boat average) ≈ 260+ YT foregone.
