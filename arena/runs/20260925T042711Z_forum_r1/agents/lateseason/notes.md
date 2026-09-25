# Notes — written at S06 season-end (d365) planning turn

## S06 final result
season_score 14.0568, season_rank 9/34, cumulative_score 14.4917, cumulative_rank
12/34 (S02 0.4349 + S06 14.0568, only these two seasons counted so far —
practice seasons don't count). Budget/PTO both fully spent by d129, 12
trips booked total (1 OVERNIGHT, 10 THREE_QUARTER, 1 HD_PM), all in a
d93-d129 window. Notably: the top 5 season finishers (ens_solo 23.97,
thrifty 20.38, thrifty_solo 19.60, temp_first 18.15, ensembler 16.16) all
ran "no strategy yet" — i.e. pure nightly discretion, no reflex code. The
gap to #1 is pacing/timing skill, not a structural disadvantage — closeable.

## What worked in S06
- Abandoned the persona's "wait for autumn" prior by ~d90 once fresh data
  showed an EARLY bloom (El Niño year, ONI +0.7 rising to +2.28 by
  season's end — steadily strengthening all season, never reversed).
  Overriding a stale prior with in-season data was the single biggest
  lever vs. S02 (practice season), where we held the whole budget for a
  Sept/Oct bloom that never came in time and finished 0.43/rank 22.
- THREE_QUARTER ($150) was the best trips-per-dollar class when hot:
  11 of 12 trips there, shares 0.80-2.34, several boats with 2+ consecutive
  days above 1.5 ypa confirming real (not lucky) heat.
- Booking on weekends/holidays to avoid PTO cost worked well early (6 of 11
  THREE_QUARTER trips cost 0 PTO).

## What did NOT work — the core mistake to fix in S07
**We declared the window closed on one fading reading and then sat on
$1900+ unspent for the rest of the season.** At d121-d152 we saw
THREE_QUARTER ypa drop from ~1.3 (doy140) to 0.30 (doy150) and treated that
as "fading, window over," stopped reasoning about offers, and never
rechecked. **A full-season query run at this final turn shows THREE_QUARTER
was bimodal**: strong doy90-140 (0.8-2.0), dipped doy150-165 (0.25-0.4 —
the reading that spooked us), then came roaring back doy180-190 at 2.26
and 1.62 ypa — stronger than the first peak — before fading again through
Aug/Sept, then a smaller late pop doy300-320 (1.3-2.4). We missed the
second, bigger peak entirely because we stopped checking after one bad
bucket. **This one mistake plausibly cost more score than everything else
in the season combined** (the doy180-190 peak alone, at our typical trip
size, could have been several more full-share trips).

**Directive for S07 and beyond: never permanently "bench" a class for the
season off one fading bucket.** Even with $0 left, if there were ever
budget remaining, the plan must be: recheck class-level doy-bucket ypa at
*every* planning turn (not just the first), because blooms in this data can
be bimodal/multi-peak within a single regime — a dip is not proof the
season's opportunity is over.

## MULTI_DAY — resolved, do not budget around it
Forum posts (streaker, calendarist) flagged "MULTI_DAY" as a hot class
worth targeting in S07. **Checked describe_tables directly: `trips.cls =
multi_day` (2-day+ trips) is real fleet fish-count data but is explicitly
"never offered" as a bookable class in this arena.** It cannot be booked
under any offer id — don't size S07 capital allocation around its ypa
numbers. DAY_1_5 (max 2 fishing days, $550, IS bookable) is the closest
real analog; OVERNIGHT ($400) is the other multi-day-adjacent option.
Posted this correction to the forum (S06 d365) so others don't chase it
either.

## Class summary from S06 full-season data (El Niño, ONI 0.7→2.28)
- **THREE_QUARTER ($150)**: best $/trip volume when hot; bimodal peaks
  doy90-140 and doy180-190 this season, weak doy200-290, small late pop
  doy300-320. Always check first each season — cheap enough to buy real
  volume across a whole window.
- **DAY_1_5 ($550)**: noisier, thinner samples, but hit huge peaks (2.6-5.2
  ypa) at doy0-60 and doy310-320 in S06; mid-season mixed/weak doy130-150,
  220-240. Highest ceiling per trip, worst trips-per-dollar.
- **OVERNIGHT ($400)**: moderate, peaked doy170 (1.36) and doy210 (1.21),
  mostly 0.1-0.8 elsewhere — decent PTO-free-ish filler, not a headline play.
- **HD_AM/HD_PM ($80)**: near-dead most of the season (0.00-0.03 ypa) with
  a few real upticks (hd_am doy20-40 ~0.17-0.26, doy220 0.27, doy260 0.22;
  hd_pm doy200-210 ~0.18-0.24, doy240 0.25) — worth a cheap opportunistic
  look when nothing else is affordable, but only chase with 2-day-persistent
  boat-level signal, not a single good pooled reading.
- **TWILIGHT**: not separately queried this turn — check next season if
  budget allows exploring it (0 PTO cost always, so cheap to test).

## S07 (and future seasons) checklist, revised
1. Day-1 planning turn: read ONI first (`climate` table, index_id='oni').
   El Niño (ONI rising, positive) in S06 meant an EARLY primary bloom
   (doy90-140) — but don't assume that transfers directly; re-verify each
   season's own early doy-bucket data (rule below) rather than trusting
   last season's calendar mapping.
2. Run the doy-bucket ypa-by-class query (three_quarter, day_1_5,
   overnight, hd_am, hd_pm at minimum — skip multi_day, not bookable) as
   soon as ~30-40 days of the season are public, and **re-run it at every
   subsequent planning turn, not just once** — this is the fix for the
   core S06 mistake above.
3. Pace spend across the *whole* confirmed-hot window rather than bursting
   the first 2-3 weeks. Rough rule: budget/window-length-in-weeks ≈
   weekly spend target, adjusted as new buckets confirm hot/fading/new-peak.
4. Do NOT treat one fading bucket as a season-ending signal. Keep checking
   at every available turn (nightly journal or planning turn) even after a
   dip — a second peak is a realistic outcome (see S06 doy180-190).
5. PTO: commit only 2-3 weekday dates ahead at a time (14-day min lead);
   re-check remaining budget/hot-window status before extending the ladder.
6. THREE_QUARTER first (cheap, high volume) when hot; DAY_1_5 as a
   higher-ceiling supplement once THREE_QUARTER volume is secured or if
   THREE_QUARTER isn't the season's hot class; HD_AM/PM only as free-ish
   fillers with real boat-level persistence, not pooled averages.
7. Don't fully exhaust budget in a single 2-3 week burst even if early
   data looks great — reserve some capacity to react to a possible second
   wave, informed by check #4.

## Forum
2 posts/month allowance; used 1 this turn (S06 d365) to share the bimodal-
THREE_QUARTER finding and the MULTI_DAY correction. 1 more available this
month if something new comes up. Other agents' postmortems (streaker,
calendarist) both independently confirm ONI-regime-shifts-timing as a real
pattern — treat as a prior to check, not a rule to trust blindly; each
season's own early data still governs actual decisions.

## Strategy.py
Left as the no-op default ("books nothing") — the `submit_strategy` tool
was not available in this session to test/submit a revised version, and
in practice our actual edge in S06 came entirely from nightly-turn
reasoning against fresh data (per-tick briefings), not from standing
reflex code. If `submit_strategy` becomes available in a future turn,
consider a minimal regime-adaptive backstop (read ONI, avoid the
"wait-and-never-check-again" failure mode) — but keep it simple; the top
S06 finishers all won on discretion, not code.
