# Notes (temp_first)

## Season 1 day 1 findings (history = seasons -1, 0; season = calendar year, doy 1 = Jan 1)
- Yellowtail are almost all on long-range boats (overnight, day_1_5, multi_day). Half-day/twilight ~0 yt/angler. 3/4 day is small (0.1-0.8 in spring).
- Fall peak: doy ~266-308 (day_1_5 3-4 yt/angler, overnight 1.6-3.4 in both seasons). Dead from doy 308 to about 84.
- Spring burst in season -1 (doy 84-100: day_1_5 3.9, overnight 3.2), none in season 0. Summer is patchy (0.2-0.6).
- Pier 7-day temp and daily yt/angler: <58F ~0; 60-65F best; 66-68F lower. It's a gate, not a linear signal.

## Strategy v1 (submitted day 1; unchanged on days 32 and 61)
- Pier 7d mean must be >=59F; recent 7d long-range yt/angler >=1.0 (0.5 in fall doy 255-310); non-fall spending keeps $1200 reserve.
- Only OVERNIGHT/DAY_1_5 at the 16:00 tick; weekend trips with 0 PTO preferred.
- PTO: commit alternate weekdays (even doy) in doy 270-305, 14 days ahead. That's about 8 days.

## Day 61 check
- No bookings/rejections/errors. Last 21 days: 0 yt in every class (118 trips including 9 day_1_5 and 3 multi_day). Pier 7d = 58.3F, just under the gate.
- B_PERSIST and thrifty have 0.15 fish each (a lucky half-day share). Forum still empty.

## Check next turn (~day 90)
- Spring burst (doy 80-110)? If long-range yt/angler > 1 and pier >= 59, the strategy should book an overnight on a weekend. Check it did.
- Still unverified: CommitPTO arg type and pick_boat day arg. PTO commits start firing around doy 256, so by the day ~240 turn, check for errors.
