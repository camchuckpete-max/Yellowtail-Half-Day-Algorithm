# Notes (temp_first)

## Season 1 day 1 findings (history = seasons -1, 0; season = calendar year, doy 1 = Jan 1)
- Yellowtail are almost all on long-range boats (overnight, day_1_5, multi_day). Half-day/twilight ~0 yt/angler. 3/4 day is small (0.1-0.8 in spring).
- Fall peak: doy ~266-308 (day_1_5 3-4 yt/angler, overnight 1.6-3.4 in both seasons). Dead from doy 308 to about 84.
- Spring burst in season -1 (doy 84-100: day_1_5 3.9, overnight 3.2), none in season 0. Summer is patchy (0.2-0.6).
- Pier 7-day temp and daily yt/angler: <58F ~0; 60-65F best (~0.35-0.4); 66-68F LOWER (0.09-0.2). So "warmer is better" only holds up to about 60F; it's a gate, not a linear signal. (Confounded by season.)
- Now: pier ~57.8F, ONI -0.94 (La Niña, cooling).

## Strategy v1 (submitted day 1)
- Pier 7d mean must be >=59F; recent 7d long-range yt/angler >=1.0 (0.5 in fall doy 255-310); non-fall spending keeps $1200 reserve.
- Only OVERNIGHT/DAY_1_5 at the 16:00 tick; weekend trips with 0 PTO preferred.
- PTO: commit alternate weekdays (even doy) in doy 270-305, 14 days ahead. That's about 8 days.

## Check next turn
- Were any actions rejected (boat pick day arg: departure vs fishing date? CommitPTO arg type)?
- Does the offers pto_dates/bookable behave the way I assumed?
- Did the spring burst start (doy 80-110)? If pier climbs and counts spike, loosen the reserve.
- Competitor dilution: see if others pile onto the same boats (pick_boat default).
