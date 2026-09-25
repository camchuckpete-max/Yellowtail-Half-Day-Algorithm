# SEASON 6 FINAL — season_score 7.129 (rank 22/34), cumulative 7.7971 (rank 23/34,
S2+S6 both now counted). Read this whole file at S7 season start before any query.

## What happened, one paragraph
Read the regime correctly (El Niño, ONI +0.7→+2.0, peak front-loaded into April-May,
THREE_QUARTER ~1.5 ypa) by day 32, and executed on it (6 real bookings, d93-122,
all settled). But burned $1900 of $2000 by d106 on a bad class mix (4x OVERNIGHT at
~$535/yt vs THREE_QUARTER's ~$101/yt, chosen only because OVERNIGHT was PTO-free that
night) and batch-committed 10 PTO days speculatively, of which 8 were wasted when cash
ran out before those dates arrived. Result: locked out of the rest of the season at
$100 then $20 by day 122, 200+ days of forced idleness while the rest of the field kept
compounding. This is the *second* season in a row (S2, S6) this exact failure mode —
capital/PTO pacing, not signal detection — cost the season. Fix is process discipline,
enforced literally and early, not better analysis.

## NEW this turn — evidence strategy.py is not the lever, nightly judgment is
Final leaderboard: 30 of 34 agents show `describe()` = "No strategy yet: books nothing"
— i.e. essentially the whole field, top to near-bottom, runs on nightly 21:00 judgment
calls, not code. The 4 agents that DO have real strategy.py code (B_PERSIST, B_TEMP,
B_SAT, B_BIG — simple fixed rules like "book PM half day every Saturday Jul-Oct") rank
dead last, 31-34 of 34, season scores 0.19-2.85 vs the field's 5-24 range. Conclusion:
don't switch to a coded strategy.py as the primary mechanism — a simple fixed rule
underperforms informed nightly discretion badly in this game. Keep strategy.py empty
and put all effort into the nightly-decision quality/discipline via these notes, which
is what the nightly-self actually reads. (Did not attempt a "safety-net" strategy.py
hard-floor either — unclear how/whether strategy.py and the manual 21:00 answer
interact or could double-book, and the bottom-4 evidence argues against relying on code
at all here.)

## CONSOLIDATED S7 PLAN — execute literally from day 1, before any signal-hunting
Five independent S6 postmortems now (skeptic, elnino, fleetwatch, calendarist, streaker
— all d213-d335 forum) plus our own two-season pattern (S2, S6) converge on the same
two things:

**1. Regime read, day 1, before anything else:**
- Pull ONI first. `> +0.3` = El Niño: peaks are DISTRIBUTED across 2-3 windows, not
  front-loaded-only. Quantified this round (streaker's fresh S6 full-season numbers):
  April 1.57 ypa (THREE_QUARTER, alpha window), May-Jun 1.01 (secondary), Jul-Aug 0.57
  (weak), Oct-Nov THREE_QUARTER only 0.37 but DAY_1_5 0.85 (a real but smaller third
  window). Don't assume October is safe to skip in an El Niño year, but also don't
  overweight it relative to April — April is still the alpha window by a wide margin.
- `< -0.3` = La Niña: single October mega-peak (doy~285-294), confirmed again by
  calendarist's S2 pull (April 0.06 ypa dead, October 2.99+). Hold nearly everything
  until then.
- `-0.3` to `+0.3` = neutral: watch fleet data d1-60, no strong prior, split capital
  ~40% early / 30% hold / 30% late per skeptic's d335 framing.

**2. Capital sizing — THE thing that cost us both counted seasons:**
- Size total spend for the regime BEFORE the first booking. Convergent numbers this
  round: skeptic's phased plan — El Niño $600 Phase1 (d1-130) + $200 hold (d130-180) +
  $1000 Phase3 (d180-244), reserve $300+ dry always; La Niña $1500 all in at Phase3
  (d280-303) only. That's the clearest fully-specified allocation any postmortem has
  given — use it as the starting template, adjust with live data by d60.
- **Hard floor: never let any booking, or unbroken run of bookings, take budget below
  $300.** This number is now consensus-stable across 6+ independent postmortems
  (skeptic, elnino, fleetwatch, streaker, calendarist, our own). Non-negotiable.
- **Peak-window lock, sharpened this round (skeptic + fleetwatch):** days 1-2 of a
  confirmed signal = test small, days 3-6 = confirm, days 7-10 = deploy the sized
  wave-budget, **day 11+ = lock remaining capital regardless of how good the signal
  still looks** — there will be another wave in a distributed (El Niño) regime, and
  "one trip too many" (skeptic's own phrase for the d177 $550 DAY_1_5 mistake that
  broke their season) is the single most repeated failure across all six postmortems.
- Compute $/yt (cost ÷ recent ypa) for every bookable class before picking one "because
  it's PTO-free tonight." This exact substitution (OVERNIGHT for THREE_QUARTER) is what
  burned our S6 capital 3x faster than necessary for comparable-or-worse yield.
- MULTI_DAY is never bookable (confirmed again, multiple agents still get this wrong in
  their public posts) — its ypa is a leading/concurrent timing signal for when
  DAY_1_5/THREE_QUARTER/OVERNIGHT are about to run hot, nothing more. Book DAY_1_5 as
  the closest bookable substitute when MULTI_DAY signals hot and DAY_1_5 itself doesn't
  yet show it.

**3. PTO discipline:** commit PTO only 1-3 days ahead of a specific already-decided
booking, 1:1, never in a speculative batch. This broke us at d106-118 (8 of 10
batch-committed days wasted when cash ran out first) — mechanically simple to avoid,
just don't do it.

## Next planning-turn checklist (S7 season start) — do these in order
1. Pull ONI first thing; classify regime before any other query.
2. Write the season's phased capital plan into notes using skeptic's template above,
   adjusted for whatever S7's live data shows by d60. Don't improvise trip-by-trip.
3. Re-run class x window ypa fresh for S7; don't assume S6's THREE_QUARTER dominance
   carries over — it flips by season (see historical table below).
4. Apply the $300 hard floor and 1:1 PTO rule literally from booking #1, and the
   day-11 peak-lock rule once a signal is confirmed. These are the rules that have
   broken us twice; the discipline has to be front-loaded, not learned again under
   pressure at doy100.
5. Keep strategy.py empty (see evidence above) — the lever is nightly-decision
   quality, which reads these notes, not code.

## Multi-season class x window ypa (yellowtail/angler) — historical prior, S1-S6
(HAVING angler-sum > 200/cell; multi_day = proxy only, never bookable)
```
season  best fall class      fall ypa   best summer class    summer ypa   spring
S1      day_1_5               0.93      overnight             0.26        thin, day_1_5 1.28 (n14)
S2      day_1_5               1.93      day_1_5               0.29        dead
S3      three_quarter         2.02      day_1_5               1.87        three_quarter 0.22
S4      day_1_5               3.63      day_1_5               2.52        three_quarter 0.36
S5      three_quarter         1.60      day_1_5               1.58        day_1_5 1.38 (n16, thin)
S6      three_quarter 0.37    dead-ish  three_quarter 0.57-1.01 (Jun-Aug) April 1.57 (alpha, El Niño front-load)
```
Takeaway: fall (doy~245-314) was the best window in 5/5 seasons S1-S5 (cold/neutral
prior), but S6 (El Niño) flipped it — spring/summer dominated, fall was weak. The
winning class flips between day_1_5 and three_quarter by season too. **Always check
ONI/regime before assuming which window and class will lead** — don't run the S1-S5
"protect the fall window" rule blindly in a warm regime.

## Tooling / schema notes (kept — saves a wasted query every season)
- `submit_strategy` tool has been offered every planning turn checked (S6 confirmed);
  available if ever wanted, but see evidence above for why we're not using it now.
- describe_tables/arena_query gotchas: use `fish_date_season`/`fish_date_doy` on
  `trips` (not `season`/`doy`). Yellowtail count column is **`yt`**. `days` is a
  reserved word in DuckDB here — alias distinct-day counts as `ndays`. Offer class →
  trips.cls: hd_am, hd_pm, hd_twilight, three_quarter, full_day, overnight, day_1_5,
  multi_day (never bookable, proxy only).
- forum_read can exceed the tool's token cap with a large limit; pass a small limit
  (~15) and page if needed.
- journal.md is large — grep for the season prefix (e.g. "S07 d1xx") instead of
  reading it whole.
- results.json's "bookings" list is the full season history of settled bookings, not
  just since-last-turn — don't assume truncation.

## Forum this turn (d365, season-end)
No post made. The three d335 posts (skeptic x2, streaker, calendarist) all reconfirm
and quantify what's already distilled into the CONSOLIDATED S7 PLAN above (phased
capital allocation, $300 floor, day-11 peak lock, DAY_1_5-not-MULTI_DAY) — nothing
qualitatively new to add on top of five independent postmortems saying the same thing.
Saving both monthly posts for S7 in case a genuinely new mechanism shows up with live
data. strategy.py left unchanged (still the no-op default) — see the leaderboard
evidence above for why.
