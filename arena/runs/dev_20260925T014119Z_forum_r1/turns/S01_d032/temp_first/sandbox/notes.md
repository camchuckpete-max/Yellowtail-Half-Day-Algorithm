# Notes (temp_first)

## Season 1, day 1 (t=730.875, doy 90-ish = spring start; doy looks like calendar day-of-year)
- History: seasons -1 and 0 in trips. Shares = yt/anglers per class-date.
- HD/3/4-day boats: ~0 yellowtail almost all year. Offshore (overnight, day_1_5) is where fish are.
- 15-day doy bins, day_1_5 share: peak doy 255-310 (1.7-4.6/angler both seasons); doy 90-105 spike in S-1 (2.9);
  summer 180-230 ~0.3-0.6 in S0. Overnight: doy 285-300 ~3-4.6, otherwise mostly <0.8.
- Pier temp bins vs share: noisy, no clean monotone relation (64-66F best for overnight). Temp alone is weak; bite confirmation matters.
- Pier now ~58F, ONI -0.94 (La Nina, cold). Expect cold spring.
- Sandbox forbids getattr.

## Strategy v1 (submitted day 1, unchanged day 32)
- Fall window doy 250-318: book DAY_1_5 (or OVERNIGHT) at 16:00 if offshore bite over last 6 days >=0.8 & pier warm (>=65F or >=63 rising), or bite >=2.
- Outside window: need warm AND bite>=2 and keep $1100 reserve.
- PTO: commit Fri/Mon with doy 262-308 14 days ahead if pier 7d mean >=63F.

## Day 32 (t~762)
- No rejected actions/errors; nobody on board has fish yet. Forum quiet.
- Last 14 days: 0 yt across ALL classes (day_1_5 8 trips/159 anglers, overnight 2). Pier 7d mean 57.9F. Still cold.
- Kept strategy unchanged (nothing to chase).
- DuckDB: "last" is reserved word - don't use as alias.

## Check next time
- Is pier warming toward 63F by summer? If La Nina persists and pier never reaches 63, PTO never commits -> consider fallback PTO commit on doy 270-300 Fridays regardless of temp (history says fall bite anyway).
- Consider summer (doy 180-230) day_1_5 share ~0.5 as a secondary use of budget if fall looks weak.
- Competitor dilution: choose boat with larger anglers count.
