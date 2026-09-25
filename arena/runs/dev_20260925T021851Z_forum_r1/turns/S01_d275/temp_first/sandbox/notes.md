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

## Day 153 check -> strategy v2
- No bookings/errors. Pier weekly means 64.5-66.0F. Long-range never reached 1.0 (overnight 0.25-0.52 per 10-day bucket), so v1 never fired.
- This season, 3/4-day boats carry the fish: yt/angler by 10-day bucket from doy 110 to 150 went 0.09, 0.19, 0.28, 0.42, 0.49. That's not like history. Multi_day 0.73 at doy 140.
- Leaders: persist 0.66, thrifty 0.15 (books 3/4-day at $150). Forum empty.
- v2: added a 21:00 3/4-day booking (7d 3/4 rate >= 0.3, no PTO, keep $1200 for fall). Assumes offer cls lowercases to "three_quarter" (unverified!).

## Day 183 check -> strategy v3
- Offer cls "THREE_QUARTER" matched fine. Trips: 3/4 d154 got 7/52 (share 0.132, so share = yt/anglers), 3/4 d155 got 0, overnight d175 got 0. Budget $1300, PTO 10, no errors, rank 4 (persist 0.66).
- Bug: the overnight was booked on the pooled long-range rate of 1.58, which came from hot 1.5-day and multi-day boats. Overnight itself was about 0.01. 10-day buckets, doy 160-180: day_1_5 2.8/1.7/1.6, overnight 0.04/0.01/1.46 (n=2), 3/4 0.05-0.23.
- v3: each class has to clear the gate on its own rate, and offers are ranked by rate per $. The $1200 reserve stays, so summer spending is effectively off (budget 1300). Fall should have money for about 3 trips.
- Forum: thrifty's post (p00001) on 3/4-day volume. San Diego is the best 3/4 boat.

## Day 214 check -> strategy v4 (fall gate 0.5 -> 1.5)
- No new bookings/errors. Budget $1300, PTO 10, score 0.132, rank 4. Thrifty is broke ($40, 0 PTO).
- Season 1 by 10-day bucket, doy 180-210: day_1_5 2.05/2.43/1.27/0.57 (cooling), overnight 0.56/1.05/0.91/0.56, 3/4 0.20-0.27 then 0.07, multi_day 2.4-2.8 (but multi_day is not in the RULES price list; prices: 3/4 $150, overnight $400, 1.5-day $550).
- History fall, 10-day buckets: day_1_5 hot 260/270-300 (2-4.4); overnight hot only 280-290 (0.6-7); 250-270 weak (0-0.5 on overnight). Per $, 1.5-day at 3.5/$550 beats overnight at 2/$400.
- v4: fall gate 1.5 so a weak early-fall week can't spend the money. Remaining $1300 = two 1.5-day trips, or 1.5-day + overnight.

## Day 245 check -> strategy v5 (3/4-day spending turned on)
- No bookings/errors since day 183. Budget $1300, PTO 10, score 0.132, rank 5. The $1200 reserve blocked everything, including 3/4 trips ($1300-150 < 1200).
- Season 1, 10-day buckets doy 210-240: day_1_5 1.18/2.21/2.60/1.59, overnight 0.39/0.73/1.11/1.03, 3/4 0.07/0.37/0.49/1.60 (n=37 at 240!).
- History doy 240-280: s-1 almost dead until about 280. s0 day_1_5 0.51 (250), 1.97 (260), 4.44 (270). Overnight is weak in both.
- Fish per $1000: 3/4 at 1.6 = 10.7, 1.5-day at 2 = 3.6, fall 1.5-day at 4.4 = 8. So hot 3/4 wins.
- v5: 3/4 gate 0.5, reserve $550 until doy 262, then 0. Up to ~5 3/4 trips, plus one 1.5-day.
- Didn't read the forum or leaderboard this turn (short on budget).

## Day 275 check (no change)
- v5 worked well: 8 3/4-day trips from d246 to d273, shares 0.52-2.93 (d273 = 82 yt/27 anglers). Season score 10.84, rank 1. No errors. CommitPTO worked (d270-286 committed).
- Budget is $100, which is less than the cheapest trip ($150), so nothing else can be booked this season. Strategy left as is. Lesson for next season: hot 3/4-day boats in late summer/early fall (doy 240-275) beat everything on fish per $. Spend there early and don't hold a 1.5-day reserve.
- Next season: check whether the budget resets. Reuse the v5 logic, and maybe start the 3/4 gate at 0.4.

## (old) Check next turn (~day 275)
- How many 3/4 trips were booked, and at what share? Were there CommitPTO errors (first fires around doy 256)?
- If 3/4 cools below 0.5 and day_1_5 is 3+, spend what's left on a 1.5-day.

## (old) Check next turn (~day 245)
- Check for CommitPTO errors (the first commit fires around doy 256 for target 270).
- Did day_1_5 pick up by doy 250-260? If the 1.5-day peak starts before 270, consider moving the PTO window earlier (e.g. 262-300).

## (old) Check next turn (~day 214)
- If day_1_5 stays at 1.5 or more all summer, consider dropping the reserve for a 1.5-day trip. Per $, 1.5-day at 1.6 beats fall overnight at 2-3 only if it costs a lot less.
- Check CommitPTO errors near doy 256.

## (old) Check next turn (~day 183)
- Did any 3/4-day bookings happen? If none while the 3/4 rate is > 0.3, the offer cls name is probably different (e.g. "THREE_QUARTER" vs "3/4"). Check rejected actions.
- Consider lowering the overnight summer gate to ~0.5 if overnight stays 0.4-0.5.
- Still unverified: CommitPTO arg type and pick_boat day arg. PTO commits start firing around doy 256, so by the day ~240 turn, check for errors.
