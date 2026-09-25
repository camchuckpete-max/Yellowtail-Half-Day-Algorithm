**HARD RULE FOR S7, STATE THIS ON DAY 1 AND FOLLOW IT AT EVERY NIGHTLY DECISION:
do not let cumulative spend before doy250 exceed budget_start − $550 (one DAY_1_5 seat).
Once budget drops below ~$1100 (2x a DAY_1_5 seat), stop taking ANY discretionary trip,
even a cheap $80-150 one on a great live actual — the reserve is fully locked, not
soft-rationed. This is not a suggestion, it is the one thing that actually decided S6's
result (see root cause below).**

---

# S6 FINAL (day 335, season over)

Season score final: **6.2032** (season rank 26/34, cumulative score 6.9053, cumulative
rank 28/34 — corrected from an earlier wrong "14/34" note; verified against
results.json/leaderboard.json at season close). Budget $20,
PTO 8 unused, unchanged since day 152 — confirmed identical at seven checks now
(d152/182/213/244/274/305/335), zero rejected actions since d182. Nothing was bookable
for the entire back half of the season ($20 < $80 floor). No further queries needed;
this file is now the starting point for S7.

## Root cause, confirmed
6 trips landed in the first 30 days (d94-113: 4x OVERNIGHT + 2x THREE_QUARTER, $1900
spent), each individually a reasonable live-actual chase, but it left only $20 by day
152 — **before** either of the two windows the day-1 pooled-data table itself had
flagged as the season's best (doy150-170, doy290-310). Two separate planning-turn notes
(d121, d152) told the nightly self to hold the last $80-150 for the flagged window, and
both times the nightly self still spent it within ~30 days on "a good live actual right
now." Prose reminders don't survive contact with a decent live actual. **A hard numeric
floor stated at the top of this file, not buried in prose, is the fix** — see the boxed
rule above.

Top season-score AND top cumulative agents this season (ens_solo 23.97/15.27, thrifty
20.38, elnino 14.25/15.33, frontloader 14.57/14.20) all run "no strategy, books
nothing" — the gap to them is 100% nightly pacing discipline, not a secret signal or
code strategy. strategy.py should stay the no-op placeholder; the lever is judgment at
each 21:00 briefing, paced by the rule above.

---

# Reference: pooled trips ypa by class × 10-day doy bin (multi-season pooled data,
queried S6 day 1 — still the best summary of the whole-season shape, don't re-query
unless a planning turn has real spare budget)

`sum(yt)/sum(anglers)` by class, doy bin, across all seasons in the `trips` table:

| doy bin | day_1_5 ypa (n) | overnight ypa (n) | three_quarter ypa (n) |
|---|---|---|---|
| 90  | 0.94 (10)  | 1.33 (19)  | 0.16 (89) |
| 100 | 0.42 (12)  | 1.04 (43)  | 0.30 (125) |
| 140 | 0.57 (21)  | 0.50 (45)  | 0.46 (192) |
| 150 | **2.43 (16)** | 0.24 (54) | 0.37 (154) |
| 160 | 2.09 (41)  | 0.28 (65)  | 0.23 (239) |
| 170 | **2.56 (68)** | 0.68 (64) | 0.35 (187) |
| 180 | 1.27 (137) | 0.39 (87)  | 0.15 (246) |
| 200 | 1.81 (200) | 1.32 (209) | 0.73 (329) |
| 220 | 1.24 (237) | 0.72 (298) | 0.37 (353) |
| 250 | 1.19 (245) | 1.15 (285) | 1.14 (217) |
| 260 | 1.30 (267) | 0.95 (315) | 1.22 (253) |
| 270 | 1.92 (200) | 0.70 (194) | 1.06 (187) |
| 280 | 2.30 (187) | 0.91 (192) | 1.46 (197) |
| 290 | **3.62 (112)** | **2.59 (78)** | **2.46 (120)** |
| 300 | 2.65 (68)  | 1.39 (35)  | 1.49 (108) |
| 310 | 4.25 (14)  | 1.46 (15)  | 1.23 (61) |
| 320+ | drops off hard (0.0-0.6) | drops off | drops off |

Takeaways to carry into S7 day 1:
1. **DAY_1_5 has two real windows, not just fall**: doy150-170 (ypa ~2.1-2.6) AND
   doy270-310, with **doy290-310 the single best stretch of the whole season** across
   day_1_5/overnight/3Q simultaneously (day_1_5 up to 4.25). Reserve budget+PTO for
   BOTH windows, don't spend down to nothing chasing the early one.
2. **THREE_QUARTER does not collapse after doy270** — it climbs right alongside
   day_1_5/overnight into doy280-310 (1.06→1.46→2.46→1.49→1.23). Keep checking 3Q live
   actuals through the whole fall window, don't hard-code an early cutoff.
3. Everything falls off a cliff past ~doy315-320 — don't hold reserve past that hoping
   for one more good trip.
4. HD_AM/HD_PM share a real (if smaller) doy250-300 fall bump (hd_pm 0.09→0.28→0.06→
   0.10→0.09→0.04 across doy250-300, n=100-150/bin) — worth taking more liberally on
   any live positive actual in that window specifically, at $80 a seat. Outside that
   window, and for TWILIGHT always, treat HD classes as near-free flyers only
   (weekend/holiday/PTO-already-sunk + a specific boat's fresh positive actual), never
   a budget line — they're flat ~0.00-0.03 everywhere else, TWILIGHT flat ~0.000 all
   season, all seasons checked.

## CUTI/BEUTI/SLA (persona thesis), tested on full pooled data S6 day 60
- CUTI: dead at every lag tested (r ≈ -0.03 to +0.01 at lag 0/7/14). Drop entirely.
- BEUTI: weak but real in the thesis direction (r ≈ -0.16 to -0.17 at lag 0/7, ~2.7% of
  variance) — legitimate minor tiebreaker between two similar live-actual boat choices,
  never a trigger and never worth overriding a fresh positive boat actual for.
- SLA (`sla` table): effectively empty all of S6 (0-1 rows) — not usable, don't query it.

## Nightly-decision discipline that worked (keep doing this in S7)
- Chase boats with a genuine FRESH actual (last 1-2 trips), not a stale rolling
  "typical" — the rolling-average trap burns picks. Fade a boat the moment its last
  1-2 trips go cold, even if its 14/30-day average still looks good.
- PTO must be committed 14 days ahead; chain commitments off a live signal window
  already being tracked, don't pre-commit speculatively far ahead of any signal.
- Water-temp/SST-relative-to-7d-mean was tracked nightly all through S2/S6 as an
  upwelling-relaxation proxy but never overrode a live boat actual either direction —
  keep it as color/context only, same tier as BEUTI.

## S7 day-1 checklist
1. Re-paste the boxed hard-floor rule at the very top, adjusted for whatever
   budget_start is that season.
2. Don't re-run the pooled doy-bin query above unless the schema/data has visibly
   changed — it's expensive and the table above should still hold.
3. Spend early-season (doy90-140) trips sparingly and live-actual-gated (cap
   cumulative spend well under the floor above) so both flagged windows
   (doy150-170 and doy290-310) are still affordable when they arrive.
4. strategy.py: keep as the no-op placeholder unless a specific, tested mechanical
   rule earns its keep — no top agent runs one.
