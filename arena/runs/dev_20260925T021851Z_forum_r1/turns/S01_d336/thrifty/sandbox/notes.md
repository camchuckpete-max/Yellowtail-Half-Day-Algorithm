# Season 2 Post-Season-1 Analysis

## Season 1 Final Outcome
- **Score**: 0.1538 (Rank 6/7)
- **Budget spent**: $1,960 of $2,000 (only $40 left at day 336)
- **Total catch**: 4 YT from 11 trips
- **Cost per fish**: $490/YT (horrible economics)

## Root Cause: Strategy Submitted Too Late
I correctly identified the seasonal window pattern (d1-71 dead zone vs d240-310 peak) in post-season analysis, but **submitted the improved strategy after already wasting $1,960 in dead zone bookings**.

The season 1 sequence:
1. Days 35-71: Made 11 bookings (8 half-day + 3 premium), spent $1,960, caught 4 YT (all from d36)
2. This depleted budget from $2,000 → $40
3. When the seasonal-window strategy eventually ran (around d100-150), budget was already gone
4. Strategy correctly avoided d72-310, but had no capital to deploy in fall peak (d240-310)

## Season 2 Fix: Deploy Correct Strategy from Day 1

### Changes to strategy.py:
1. **Absolute gate**: `if doy < 72: return actions` - refuse all d1-71 bookings at first decision point
2. **Reserve discipline**: Hold $600 until d240, then drop to $200
3. **Momentum thresholds**: Tighter in peak season (d240+: 0.2) than early (d72-239: 0.1)
4. **Lookback windows**: 3-day early, 7-day in peak (peak season has more data, can use longer window)
5. **Class preference**: All three (day_1_5, overnight, three_quarter) enabled from d72

### PTO strategy:
- Commit starting d226 (14 days before d240 peak opens)
- Only commit for future days in d240-310 window
- Never waste PTO in dead zone

## Competitive Landscape (Season 1 Final Leaderboard)
| Rank | Agent | Fish | Strategy |
|------|-------|------|----------|
| 1 | temp_first | 10.84 | Warm water gate (59°F Scripps Pier) + overnight/day_1_5 focus |
| 2 | B_BIG | 7.89 | Friday evening trips in Aug-Sept peak |
| 3 | persist | 0.66 | Reactive momentum, weekend PTO discipline |
| 4 | B_PERSIST | 0.34 | Book half-day if daily pooled count > 0 |
| 5 | B_SAT | 0.20 | Every Saturday July-Oct half-days |
| 6 | **thrifty** | **0.15** | *My strategy - failed by deploying too late* |
| 7 | B_TEMP | 0.07 | Temperature gate (68°F) + half-days |

**Winner's insight**: temp_first dominates by using **Scripps Pier temperature (59°F gate) + proven classes (overnight/day_1_5)**. Water temp is a more continuous signal than day-of-year. Could combine both: `if scripps_temp < 59: return; if doy >= 240: be aggressive`.

## Data Available But Unused
- Pier: Scripps water temp (hourly, more granular than doy alone)
- Fishdope: Daily YT reports (local, coronado, north)
- Ocean: SST, currents, chlorophyll
- Climate: ONI, PDO (seasonal indices)

Could enhance season 2 by adding Scripps water temp as a tertiary gate after seasonal + momentum.

## Season 2 Goals
- **Minimum**: 1 fish (beat B_SAT, match persist level by deploying in peak only)
- **Target**: 3-5 fish (approach persist strategy, beat B_BIG's first-year naive focus)
- **Stretch**: 7-10 fish (approach temp_first by adding water temp signal)

## Action for Season 2 Day 1
1. Verify strategy.py loads without errors
2. Monitor d72-107 window for early signal (d72-107 had 0.183 YT/angler - weak but > 0)
3. At d226, start committing PTO for d240+ fall trips
4. At d240, book aggressively on best momentum class
5. Target 3-5 bookings total (vs 11 wasteful ones in s1)
6. Reserve 1-2 premium slots ($550-1000) for late-season peak (d270-306)

## Hypothesis for Season 3
If water temperature (Scripps Pier 59°F gate) + seasonal windows (d240-310 peak) + momentum (3/7-day) are combined, could reach 5-7 fish. temp_first's dominance suggests temp signal is stronger than doy alone.