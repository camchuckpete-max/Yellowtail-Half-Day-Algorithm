# Season 1 Final & Season 2 Strategy

## Season 1 Final Outcome (Day 275)
- **Final Score**: 0.1538 (Rank 5/7)
- **Total Fish**: 4 YT from 11 trips ($1,960 spent of $2,000)
- **Budget Frozen**: $40 left, PTO 0
- **Winner (temp_first)**: 10.84 fish (7x better)
- **Root Cause**: Booked during dead zone (d35-71) instead of peak (d250-275)

## Critical Discovery: Water Temperature
Analyzed pier temps + premium trip yields:
- **Dead Zone (d35-71)**: Avg 14.8°C, 146 premium trips, **0 YT total** (all zeros)
- **Peak Season (d250-275)**: Avg 17.6°C, 1004 premium trips, **18,441 YT total** (massive)

This proves temp is the PRIMARY gate, not class or time-of-year intuition.

## Season 2 Strategy Changes
Submitted: "Pier-temp gate + proven classes + momentum"

Key improvements:
1. **Scripps Pier water temperature as primary gate** (7-day rolling mean)
   - Baseline >= 15.5°C (59°F) outside fall
   - Raised to 17°C (62°F) in fall window (d240-310)
   - Blocks booking during dead zones automatically
   
2. **Proven classes secondary gate** (day_1_5, overnight, three_quarter)
   - Same class filtering as Season 1 strategy
   
3. **Reactive momentum tertiary gate** (2-3 day YT/angler)
   - Pick best-performing class when temp gate passes
   - Only book on non-negative signals
   
4. **PTO strategy**
   - Commit 14 days ahead only when temp + momentum both positive
   - Spacing for fall weekends (d240-310)
   - Check pto_left before committing (Season 1 didn't)

5. **Reserve management**
   - $200 minimum (same as before)
   - Should help survive early-season without depletion

## Lessons for Season 2+
- **Temp gate prevents dead zones**: Won't waste budget on cold periods
- **Class gating still important**: But secondary to temp
- **Momentum timing**: Only book when multiple signals align (temp + class + momentum)
- **Early observation**: Watch temp trend first 30 days; only book weekend free-PTO half-days if temp < gate
- **Late season optimization**: When d240+ arrives, be ready to deploy capital aggressively (was our failure)

## Data Tables Available (Unused in Season 1)
- `pier`: Scripps Pier water temp (used now)
- `ocean`: SST by zone, currents, chl
- `fishdope`: Daily YT reports (yt_local, yt_coronado, yt_north, catch/sight/neg counts)
- `forecasts`: Wind, swell predictions
- `buoy`, `metar`: NOAA data
- `climate`: ONI, PDO, NPGO indices
- `upwelling`: CUTI, BEUTI

Future seasons: consider fishdope text signals, upwelling indices, or buoy SST as secondary confirmation.

## Final Season 1 Metrics
- Cost per fish caught: $490 (4 fish / $1,960)
- Trips per fish: 2.75 (11 trips / 4 fish)
- Best trip: d036 (4 YT, PM half-day, pure luck during dead zone)
- Dead zone waste: ~$1,600 (8 trips in d35-71, all zero)

Season 2 goal: reach 1-2 fish minimum by deploying capital only when temp gate passes.
