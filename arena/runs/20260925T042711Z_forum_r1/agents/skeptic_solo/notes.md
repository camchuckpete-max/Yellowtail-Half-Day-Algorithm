# S6 season-end retrospective (consolidated — replaces the 5 prior near-duplicate planning-turn
entries; their content is folded in below, redundancy removed)

## Final S6 result
budget_left=$20, pto_left=5, season_score **6.744** (season_rank 24/34), cumulative_score
**7.5721** (cumulative_rank 25/34). Season is now finalized: `results.json.seasons` shows S6
`counted: true`. `rejected_actions_and_errors_since_last_turn` empty all season — every booking
attempt that was tried, succeeded; nothing was lost to mechanical errors.

## What actually happened (7 bookings, all d093–d107, nothing after)
4x OVERNIGHT (d093–101, $1600) + 2x THREE_QUARTER (d105–106, $300) + 1x HD_PM (d107, $80) = $1980
of $2000 spent in 15 days, all before the fall-run window (doy265–300) was even visible. Shares on
those trips were mostly *good* (0.11, 1.41, 1.12, 1.31, 1.09, 1.71, 0.0 — HD_PM was a real bust,
n=1 boat read) — the picks themselves weren't the failure. The failure was **pacing**: no budget
left ($20 < $80 cheapest class) for the remaining ~230 days of nightly turns, including the entire
fall run. This is a pure-arithmetic lockout, not a bad-read problem — don't re-diagnose it as one.

## Root cause, one sentence
Individually-reasonable trips booked back-to-back with no cap on trailing spend burned 80% of a
full-season budget in 9 days, before the part of the season (fall run) historically most worth
saving budget for was even in view.

## S7 game plan — hard gates, not judgment calls
1. **Trailing-10-day spend gate**: before booking, if money committed in the last 10 calendar days
   (including the trip about to be booked) would exceed **$600**, don't book. This alone stops the
   d093-101 pattern that caused everything.
2. **Pre-doy250 floor**: if `budget_left < $600` before day-of-year 250, stop booking new trips
   entirely — preserve capacity for the fall window.
3. **Earmark PTO-committed costs immediately.** The moment PTO is committed for a date (14+ days
   out, per rules), treat that trip's fare as already spent against budget, so a spree in the
   intervening days can't strand a commitment (this happened to the d112/d113 PTO in S6 — committed,
   then unaffordable by the time it mattered).
4. **share/$ computed live is the decision metric** — not a hardcoded class-by-season rule. Don't
   assume "fall = book DAY_1_5." See table below: it only wins 2 of 5 seasons.
5. **HD_AM/HD_PM needs 2+ boat-days of recent history** before trusting a positive pooled read —
   the S6 d107 HD_PM booking on a 0.024/angler n=1 read produced 0 yt.
6. **strategy.py is very likely inert in this harness** — `submit_strategy` was checked and absent
   at every single S6 planning turn (d213, d244, d274, d305, d335, season-end). Stop re-checking
   this every turn (it's a wasted query once established); check once at S7 season start, and if
   still absent, treat all pacing discipline above as manual judgment required at every 21:00
   nightly call — that's the step that failed in S6, not the fish-picking.
7. Avoid the mirror-image failure too (this agent's own S2: passive/cash-hoarding, rank 12 despite
   a mid-season lead). Target: spend steadily enough to stay in the game, never past gate #1.

## Reference: fall-run (doy265–300) share/$ by class and season (S1–S5 pooled)
share = SUM(yellowtail)/SUM(anglers); $/share computed from class fixed price.

| season | day_1_5 share | overnight share | three_quarter share | day_1_5 $/share | 3/4 $/share |
|---|---|---|---|---|---|
| S1 | 1.954 | 0.600 | 0.239 | 0.00355/$ | 0.00159/$ |
| S2 | 3.433 | 1.374 | 0.195 | 0.00624/$ | 0.00130/$ |
| S3 | 2.340 | 2.126 | 2.509 | 0.00425/$ | **0.01673/$** |
| S4 | 3.976 | 1.099 | 1.034 | **0.00723/$** | 0.00689/$ |
| S5 | 0.176 | 0.104 | 2.166 | 0.00032/$ | **0.01444/$** |

DAY_1_5 wins fall share/$ in only S2 and S4. In S3 and S5, THREE_QUARTER beats it 3–40x per
dollar; S5's entire "fall run" for day_1_5/overnight fails to materialize while three_quarter
alone stays strong. **Don't hardcode a class for the fall window — pull live 7–14 day pooled
share/$ for whatever's actually scheduled/bookable that night, every night.**

## Schema gotcha (cost a wasted query once — don't repeat)
`schedule.cls` values are **lowercase** (`day_1_5`, `three_quarter`, `overnight`, `hd_am`, `hd_pm`,
`hd_twilight`, `hd_unspecified`). A query filtered on `'DAY_1_5'` silently returns 0 rows.

## Open question, not worth resolving
Every agent's `strategy` field in `leaderboard.json` reads "No strategy yet: books nothing." except
the four fixed baseline bots (B_PERSIST/B_TEMP/B_SAT/B_BIG), which show real strategy text. Top
season scorers (ens_solo 23.97, thrifty 20.38, thrifty_solo 19.60) all show the placeholder too —
either the field just isn't populated for non-baseline agents in this view, or top agents also
book purely via nightly manual calls with no submitted strategy.py. Doesn't change what to do
next season (nightly discipline either way), so not worth spending a query on.
