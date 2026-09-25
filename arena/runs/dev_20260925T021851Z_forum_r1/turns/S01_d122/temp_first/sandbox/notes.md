# Notes (temp_first)

## Season 1 day 1 findings (history = seasons -1, 0; season = calendar year, doy 1 = Jan 1)
- Yellowtail are almost all on long-range boats (overnight, day_1_5, multi_day). Half-day/twilight ~0 yt/angler. 3/4 day is small (0.1-0.8 in spring).
- Fall peak: doy ~266-308 (day_1_5 3-4 yt/angler, overnight 1.6-3.4 in both seasons). Dead from doy 308 to about 84.
- Spring burst in season -1 (doy 84-100: day_1_5 3.9, overnight 3.2), none in season 0. Summer is patchy (0.2-0.6).
- Pier 7-day temp and daily yt/angler: <58F ~0; 60-65F best; 66-68F lower. It's a gate, not a linear signal.

## Strategy v1 (submitted day 1; unchanged on days 32, 61, 92)
- Pier 7d mean must be >=59F; recent 7d long-range yt/angler >=1.0 (0.5 in fall doy 255-310); non-fall spending keeps $1200 reserve.
- Only OVERNIGHT/DAY_1_5 at the 16:00 tick; weekend trips with 0 PTO preferred.
- PTO: commit alternate weekdays (even doy) in doy 270-305, 14 days ahead. That's about 8 days.

## Day 61 check
- No bookings/rejections/errors. Last 21 days: 0 yt in every class. Pier 7d = 58.3F.

## Day 92 check
- No bookings/rejections/errors. Last 31 days: 14 long-range trips, 0 yt. Pier weekly means 55.9-58.0F, cooling. No spring burst this season (same as season 0). Forum still empty. Score 0, rank 6 (everyone is near 0).
- Useful queries: trips(fish_date_t, cls lowercase, yt, anglers); pier(ts_t, wtmp_c). t is in days; floor(t/7) gives week buckets.

## Day 122 check (no change to strategy)
- No bookings/rejections/errors. Pier warming: weekly 56.7 -> 61.5F over the last 5 weeks. First yt: 3/4-day 0.1-0.2/angler, day_1_5 0.17 last week. Long-range still well under 1.0.
- History, overnight+1.5-day yt/angler by 2-week bucket (doy): summer 168-250 is 0.0-0.5 in both seasons. Fall 280-307 is 2.3-3.9. 266 bucket: 0.11 (s-1), 2.3 (s0). Summer is not worth the $1200 reserve, so keep the 1.0 non-fall gate.
- Leaders only have 0.15 fish. Nobody has scored meaningfully. Forum is empty.
- Query tip: trips has fish_date_season and fish_date_doy columns.

## Check next turn (~day 152)
- Summer warming: pier >= 59 and any long-range yt > 1/angler? Strategy should book a weekend overnight.
- Still unverified: CommitPTO arg type and pick_boat day arg. PTO commits start firing around doy 256, so by the day ~240 turn, check for errors.
