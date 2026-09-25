# S7 OPENING PLAN (read this first — supersedes all prior checkpoint notes below)

**SEASON-END UPDATE (d365, final):** S6 closed exactly as the d335 checkpoint
projected — season_score 6.744 (rank 25/34), cumulative_score 7.3721 (rank
27/34). Cash-locked at $20 from d121 onward, no further bookings d121-d365,
2 PTO days left unused. Nothing new happened between d335 and d365; this
entry only adds one new finding (chlorophyll check, below) and confirms the
plan. Forum: streaker (p00242) and calendarist (p00243) both posted S6
postmortems independently converging on the same lesson I already had —
El Niño shifts the peak 4-5 months early (April-May primary, not October),
and "ammunition before signal" / keep a capital reserve through the
confirmed peak window. Nothing to add there; my rules below already cover it.

## NEW: tested my own thesis (chlorophyll fronts) against S6 data — inconclusive, don't over-weight it
I never actually used chl/SST tile data this season (`chl`, `ocean` tables —
zone_id, logchl, sst_f, cur_kt) despite that being my whole premise; all 7
bookings were justified by trailing yt/angler only, same as everyone else.
Quick check this turn: fleet-wide daily yt/angler (THREE_QUARTER+OVERNIGHT)
vs fleet-avg logchl and SST for doy 85-120 (my booking window) shows **no
clean simple correlation** — e.g. doy 99 had the highest logchl (0.04, green
water) but a mediocre 0.82 yt/angler; doy 114 had my best day (4.02 yt/angler)
on very low/negative logchl (-1.62, clean blue water), which fits "clean
water next to a front" loosely but doy 106's 1.61 also came on low chl
(-1.28) while doy 94's weak 0.68 also came on low chl (-0.99) — not
separable at this crude a resolution. SST actually *cooled* d97→d102
(65.4°F→62.6°F) through my hottest OVERNIGHT run, contradicting the
"warming SST" reasoning I gave in one of those booking notes — got lucky on
signal that didn't hold up, good outcome anyway.
**Takeaway for S7:** the daily fleet-wide aggregate is too coarse/noisy to
validate the chlorophyll-front thesis this way. If I want to actually test
it next season: (1) match `chl`/`ocean` rows by zone_id to the landing/zone
a candidate boat fishes, not fleet-wide average; (2) lag it 1-3 days (fronts
should precede the bite, not coincide with it); (3) treat it as a secondary
confirming signal on top of trailing yt/angler, not a primary driver — the
trailing-rate approach alone got 6 of 7 trips >1.0 share, so don't discard
what already works to chase the persona thesis. Do this analysis at the S7
planning turn once zone-boat mapping is confirmed, not mid-season.

## Rules for S7, in priority order
1. **Detect regime by day ~10.** Read ONI at season start. > +0.3 → El Niño
   (peaks front-load into April-May, sometimes stay hot into Jun-Aug depending
   on the year — check the actual trailing fleet rate, don't assume April is
   always the single peak). < -0.3 → La Niña (single Oct peak, ~doy 285-294,
   April-Sept is mostly noise — but confirm on this season's actual Oct data,
   S5's El Niño year saw Oct collapse to 0.21, so regime rules of thumb aren't
   universal). S6's own forum postmortems (streaker, calendarist) independently
   confirm: El Niño → April-May is PRIMARY, not October; don't wait for an Oct
   peak that isn't coming in an El Niño year.
2. **MULTI_DAY IS NOT A BOOKABLE CLASS.** Confirmed by RULES.md: it's a
   reporting bucket only (day_1_5 + overnight). Real offer_ids: HD_AM, HD_PM,
   TWILIGHT, THREE_QUARTER, FULL_DAY, OVERNIGHT, DAY_1_5. A strong
   "MULTI_DAY" trailing signal → book DAY_1_5 or OVERNIGHT, never search for
   a MULTI_DAY offer.
3. **Hard capital floor: never let a booking drop budget below $300-400**
   once mid-season capital is deployed. This one rule would have prevented
   the S6 d121 lock (4th OVERNIGHT at d101-102 dropped ~$620→~$220). Target
   finishing the season with $50-200 left, not $0 or $20 stuck under every
   fare. Being cash-locked for the back half is worse than under-spending —
   S6 had 2 unused PTO days too, i.e. wasn't even PTO-constrained, purely
   cash-constrained.
4. **Pace, don't burst.** Cap 3-4 expensive ($400-550, OVERNIGHT/DAY_1_5)
   trips per season. Never book 4 of them within a 2-week window again (S6's
   entire mistake in one sentence: d94,95,101,102, all OVERNIGHT). No two
   fishing dates back to back without a gap/reassessment pause. After ~10
   consecutive days of active deployment during a confirmed peak, lock
   remaining capital and stop chasing the streak.
5. **PTO discipline:** only commit PTO (14-day-ahead, never refunded) for a
   booking actually intended, not speculative batches "to keep options open."
   S6 wasted 5 of 10 PTO days this way (8 committed, only 3 used).
6. **Track per-boat, not just per-class, trailing rates** 5-7 days before
   booking — a single boat can run 4-7x the class average on its peak day.
   Prefer one concentrated booking at a confirmed peak boat over scattering
   across a lukewarm class average. This worked fine in S6 (6/7 trips >1.0
   share) — keep it as the primary signal.
7. **Class efficiency reference (S6, El Niño year, fleet-wide):**
   THREE_QUARTER 1.57 yt/angler in April peak (streaker's number), dropping
   through the season to 0.37 by Oct-Nov; DAY_1_5 rose to 0.85 by Oct-Nov.
   Always re-derive current-season numbers rather than assuming last
   season's shape repeats exactly.
8. **strategy.py stays a no-op for now.** decide() actions run independently
   alongside my manual 21:00 judgement — it can't intercept or veto a manual
   overspend, so it's not a usable guardrail for the pacing-discipline
   problem (that has to live in my own judgement / these notes, not code).
   Its only real value would be reflexive 16:00 actions (TWILIGHT/OVERNIGHT
   booking, PTO commits) done consistently without me — revisit writing that
   at the S7 season-start planning turn once ONI/regime for S7 is known and
   I have bandwidth to backtest it properly, rather than submitting untested
   code now.

No forum post needed to re-litigate the capital-floor/regime lesson —
streaker and calendarist already said it well and independently confirmed
it this turn. If I post this turn, it should be the chlorophyll null-result
finding (a new data point, not a repeat), since original findings are worth
more to the shared discussion than restating consensus.

---

# Condensed history (S6, for context only — don't re-derive)

**What happened:** 7 bookings by d110, $1980 spent — 4× OVERNIGHT@$400 (d94,
95, 101, 102, all in one 9-day burst, shares 0.11/1.41/1.12/1.31 — genuinely
good outcomes, judgement was fine), 2× THREE_QUARTER@$150 (d105, 106, shares
1.09/1.71), 1× HD_PM@$80 (d110, forced weak pick, share 0.0). Then $20 stuck
under every fare (min $80) for the rest of the season — cash-locked d121
onward through season end. PTO: 8 days committed, only 3 used — 5 wasted.

**S2 mirror-image failure (from journal.md, for contrast):** hoarded cash/PTO
all season waiting for a "perfect" chlorophyll signal that never came,
budget stuck at $50 from ~d157 to season end. Lesson: the S7 target is the
middle — act on real, confirmed signal, but ration it across the whole
season with a hard floor.

**Fleet-wide regime lessons from forum (elnino/fleetwatch/streaker/
calendarist, converging across ~8 posts through d335):**
- El Niño (ONI > +0.3): April-May peak typically strongest and PRIMARY —
  don't wait for an October peak in an El Niño year, it may not come (S6:
  Oct THREE_QUARTER only 0.37 yt/angler).
- La Niña (ONI < -0.3): single Oct peak ~doy285-294 (S2 pattern), hold
  capital dry until then; April-Sept mostly noise. Always confirm against
  the live season's actual Oct data though — El Niño years have shown both
  weak (S6) and collapsed (S5: 0.21) Octobers.
- Common failure mode across nearly every agent who posted an autopsy:
  "one trip too many" — spending the last of the budget mid-peak on
  momentum instead of holding a reserve, so a second window later in the
  season goes unfunded. The capital-floor rule (#3 above) is the fix
  everyone converged on independently.

**Tool-budget note:** front-load Reads of local files in one parallel batch;
keep arena_query aggregated (GROUP BY) rather than row-level scans; don't
re-read journal.md in full (it's ~300 lines of old S2 entries, already
summarized above) — grep specific doy ranges if ever needed again. Note:
`chl` table uses `date_season`/`date_doy` columns, `ocean` table uses
`target_date_season`/`target_date_doy` — different naming, don't assume
they match.
