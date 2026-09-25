# S06 CLOSED — final numbers (confirmed via results.json/leaderboard.json)
Budget left $50, PTO left 10/10 (never spent — persona holds). season_score 7.2695, season_rank
20/34. cumulative_score 7.8976 (S02 0.6281 rank16 + S06 7.2695 rank20), cumulative_rank 22/34.
7 bookings, all d94-d122 (THREE_QUARTER x4, OVERNIGHT x2, DAY_1_5 x1): shares 0.571, 1.067, 1.118,
1.10, 2.808, 0.606, 0.0 (skunked last one) = 7.2695 total. Then $50 left, and every class costs
$80+, so structurally locked out for the remaining 243 nights (d123-d365) straight through the
whole rest of the season, including the confirmed big Sept/Oct tail the fleet reported. Zero
rejected actions/errors all season. submit_strategy tool: checked again this turn (ToolSearch) —
still not offered. If it ever appears, hard-code the reserve rule below into strategy.py so a
single night's conviction can't override it.

## What worked
- **Boat/class picking was genuinely good.** Every one of the 7 bookings had the best live ypa
  signal available that night (checked and re-confirmed across 5 planning turns) — this was never
  a signal-reading problem.
- **The Friday-departure OVERNIGHT/DAY_1.5-into-Saturday trick** (fishing date lands on a weekend
  even though departure is Friday evening) is the only way this zero-PTO, weekends-only persona
  reaches the pricier multi-day classes. 3 of 7 bookings used it (d101, d108, d115 fishing dates).
  Keep using it every season — it's not a loophole, it's the persona's only lever into those classes.
- **THREE_QUARTER ($150) was the strongest class fleet-wide in S06's hot window** (April-May,
  El Niño year) — good default when no boat shows an outsized signal.

## What failed — pure pacing, not picking
- Spent $1950 of $2000 in 29 days (d94-d122), rode a real April-May hot streak, then hit a **hard
  cliff**: landing at $50 doesn't mean "fewer trips left," it means **zero** bookable classes for
  the rest of the season (cheapest fare is $80 HD_AM/PM/twilight). This is a cliff, not a taper.
  Same exact failure mode in S02 (practice season) — confirmed twice now.
- No reserve floor was enforced. Nothing stopped trip 7 (d122, THREE_QUARTER, skunked 0.0) from
  dropping budget to $50 with 243 days still to play.
- The whole forum converged independently on the same diagnosis this season-end (frontloader,
  thrifty, biggame, weatherman, dope_reader, overreactor, skeptic, streaker, calendarist, all
  posted d335 postmortems): capital discipline beats signal-chasing; several quantified 5-20 "fish
  left on the table" from breaking early and missing a second peak. thrifty (rank 2, finished with
  cash left) and ens_solo (rank 1) both paced across the season instead of front-loading.
- MULTI_DAY is a fleet-stats aggregate label only — never an actual offer_id/bookable class (per
  RULES.md's trip table, confirmed by multiple agents' errors this season). Only ever use it as a
  leading indicator, act via DAY_1_5/OVERNIGHT/THREE_QUARTER. I never made this mistake but it's
  worth re-confirming at S07 start since it's an easy trap.

## S07 plan — apply from day 1, every night (this is what my nightly self should follow)
1. **Read ONI fresh in the first S07 planning turn (~d1-30).** Don't assume last season's regime
   shape repeats — S02 was La Niña/October-peak, S06 was El Niño/April-May-peak: genuinely opposite
   shapes. ONI > +0.3 → warm → peaks spread April-June (and possibly a second window later in the
   year, per this season's forum reports of a Sept/Oct tail I never reached). ONI < -0.3 → cold →
   peaks concentrate October, hold most of the budget until then. Between → wait for the fleet's
   first sustained (multi-boat, multi-trip) signal before committing.
2. **Default class = THREE_QUARTER ($150)** for weekend day trips unless a boat shows a
   well-supported signal (ypa clearly >2x class average, multiple recent trips, not one outlier).
3. **Concrete reserve floor: never let post-booking budget drop below $300 before the season's
   final quarter (~d280+).** This is the single highest-value fix — sharper than any abstract
   formula, and it's the number the whole fleet converged on independently this season-end.
   $300 ≈ 2x THREE_QUARTER or just under 1x OVERNIGHT — enough to keep reacting to a second peak.
4. **Per-trip cap: never spend more than 20% of *remaining* budget on one trip** before the
   midpoint (~d180). Stops one OVERNIGHT/DAY_1.5 from eating a third of the season's cash.
5. **Target 10-13 trips spread across the whole April-November window, not 6-7 front-loaded into
   the first 30 days.** S06 undershot this by riding one hot streak to near-zero budget by d122.
6. **Don't stop scanning fleet ypa after a hot streak ends** — only stop *spending* because of the
   reserve floor (#3), never because "the peak felt done." S06's own tail (d170-182, 1.3-3.5 ypa
   per journal-era forum reports) and this season's Sept/Oct window were both real and both missed
   purely on cash, not on missed signal.
7. **Keep using the Friday-departure OVERNIGHT/DAY_1.5-into-weekend trick** — it's the main way
   this zero-PTO persona reaches pricier classes at all.
8. **Persona is fixed** (weekends/holidays + Friday-departure trick only, zero PTO) — don't
   relitigate. PTO sitting at 10/10 all season is correct under this persona, not a miss.
9. **Check for submit_strategy at every planning turn** (cheap: glance at the deferred-tools list
   already shown, or one ToolSearch call). If it appears, hard-code rules #3 (reserve floor) + #4
   (20% cap) + #2 (THREE_QUARTER default) directly into strategy.py so they survive even against a
   single night's contrary conviction — this was never available in S02 or S06.

## Note on notes.md housekeeping
Trimmed ~430 lines of repetitive per-planning-turn status re-confirmations (d182/d213/d244/d274/
d305/d335, all restating the same $50-lockout with no new information) down to this single
consolidated version. Nightly journal entries (kept separately in journal.md) already have the
day-by-day detail if ever needed; this file should stay a living plan, not a log.
