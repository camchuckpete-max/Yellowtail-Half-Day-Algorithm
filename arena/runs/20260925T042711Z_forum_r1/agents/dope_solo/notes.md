
# dope_solo notes — living doc. Read top section first (current plan), history below.

## SEASON 6 CLOSED — final retro turn. Season 6 is now scored into the cumulative board:
## cumulative_score 8.8401 (0.0958 from S2 + 8.7443 from S6), cumulative_rank 19/34 (up from
## rank31 when only S2 counted). season_score 8.7443 final, season_rank 16/34. Budget $50/PTO 0
## final (below every trip's $80 min fare — season was operationally over since day111). Zero
## rejected actions all season after the early PTO/boat-schedule mistakes. No submit_strategy or
## forum tool exists in this solo variant (checked again this turn via tool search, confirmed
## absent — 7th season running) — strategy.py in this dir is inert, never actually submitted;
## don't spend turns editing it. All steering happens through these notes, read by the nightly self.

**S6 in one line: caught the season's first wave hard (3Q, doy93-111, avg ~1.2-1.7 share/trip,
8.74 total) then went dark for the remaining ~220 days because ALL of the $2000 budget and 9 of 10
PTO days were spent in the first 20 nightly-decision days.** Three more confirmed windows came and
went untouched: 3Q wave2 (doy171-190, ~1.4-3.4 ypa), a day_1_5/overnight spike (doy205-219, ~1.2-1.9
ypa, later shown to be a 1-bucket fake-out), and the strongest print of the whole season, day_1_5's
doy305-315 peak (5.23 ypa) as part of a genuine tranche-4 window (doy280-325) that then collapsed
just as fast. A tranche-disciplined budget would very plausibly have doubled or tripled the 8.74
score by catching 2-3 of these four windows instead of one.

**S7 STARTS HERE — the plan below (originally drafted day-244, refined day-274/305/335) is final
and ready to use verbatim from day 1. Nothing changed by this closing check beyond confirming the
cumulative-scoring mechanics and the no-strategy-tool fact above.**

**Final pull, S6 fish_date_doy 295-340, 10-day buckets, ypa=sum(yt)/sum(anglers), real n:**
| cls | 300 | 310 | 320 | 330 | 340(n=4, ignore) |
|---|---|---|---|---|---|
| day_1_5 | 1.580(15) | **5.233(7)** | 2.466(9) | 0.024(2) | — |
| three_quarter | 1.366(27) | **2.410(11)** | 0.674(21) | 0.023(28) | 0.457(4) |
| overnight | 0.031(17) | 0.308(3) | 0.019(5) | 0.0(3) | — |

**This closes the S6 book: tranche-4 (day_1_5/3Q re-ignition flagged at doy280-305) peaked HARD at
doy310 — day_1_5 hit 5.23 ypa, the single hottest bucket of the ENTIRE season, well above wave-1's
1.1-2.0 or wave-2's 1.4-3.4 — then crashed to near-zero (0.02-0.07) by doy330, a total collapse in
one bucket. 3Q shows the same shape, peak 2.41 at doy310, dead 0.02 by doy330 (n=28, real). Overnight
stayed dead the whole stretch. So the true tranche-4 window was narrow: ~doy295-325, with the peak
concentrated right at doy305-315, not a slow build sustained through day330 as day-305's note
guessed. A budget/PTO-equipped agent needed to be ready to fire in that ~3-week window specifically,
not just "sometime after doy280."**

**S7 TRANCHE PLAN — refined with this final data point, port verbatim into S7 day-1:**
- 4 tranches of ~$500, hard caps by doy: tranche1 doy<120, tranche2 doy120-200, tranche3
  doy200-280, tranche4 doy280-end-of-season. Never let cumulative spend exceed the current
  tranche's ceiling, no matter how hot a signal looks (S6's core mistake: 98% of budget by day111).
- Trigger within an open tranche: 2+ consecutive 10-day buckets at ypa≥~0.7-1.0, n≥20 pooled
  across boats in that class — not a single spike, not raw magnitude alone.
- **Tranche 4 refinement (new this turn): the fall peak can be short and violent — S6's whole
  tranche-4 payoff (5.2 ypa day_1_5) landed in one ~10-day bucket (doy305-315) then fully collapsed
  within the next bucket. Don't spread tranche-4 spend evenly across doy280-330 hoping for a
  sustained run — once the 2-bucket confirmation trigger fires inside tranche 4, front-load the
  REMAINING tranche-4 budget fast (within days, not weeks), because the window can close as
  abruptly as it opened.** Give tranche 4 priority/first-look weighting regardless: day_1_5 and/or
  3Q have now peaked hardest right at the season close in S1, S3, S4, and S6 (4 of 6 seasons).
- **Keep 3-4 PTO days uncommitted through doy~250** specifically so a tranche-4 push has weekday
  PTO available — S6's PTO hit 0 by day119 and never recovered, independently blocking tranche 4
  even before budget ran out.
- Carry forward unchanged: hd_am/hd_pm/twilight dead every season (7 for 7) — never book;
  class-pooled trailing ypa (fleet-wide, n≥20) beats single-boat picks; no class is the automatic
  season winner (day_1_5 4/6 times, 3Q 3/6 times, sometimes both in one season like S6).

**S7 day-1 action: open notes with this tranche plan (now finalized with the full-season S6 data,
including the sharp tranche-4 peak/collapse shape) as the primary structural rule, combined with
the 6 cross-season rules in the day-244 entry further below. S6 is fully closed — no more S6 pulls
needed, ever.**

---

## S6 day-305 planning check-in — FINAL S6 turn, resolves the day-274 "does anything re-ignite
## doy250-330" question: YES, strongly. Budget $50/PTO 0 unchanged (still below every trip's $80
## min fare), season_score 8.7443 unchanged, rank 15/34 season-to-date, cumulative 0.0958/rank31.
## Nothing bookable, nothing rejected — pure lesson turn. S6 is done for dope_solo.

**Fresh pull, S6 fish_date_doy 270-305, 10-day buckets, ypa=sum(yt)/sum(anglers), real n:**
| cls | 270 | 280 | 290 | 300 |
|---|---|---|---|---|
| day_1_5 | 0.197(12) | 0.852(33) | 0.962(19) | **1.580(15)** |
| three_quarter | 0.124(29) | 0.056(51) | 0.702(29) | **1.366(27)** |
| overnight | 0.065(38) | 0.030(74) | 0.036(33) | 0.028(19) |

**Verdict: both day_1_5 AND three_quarter staged genuine, accelerating late-season waves in
tranche 4 (doy280-330) — day_1_5 climbed 3 consecutive buckets (0.85→0.96→1.58), 3Q climbed
2 consecutive buckets after one cold one (0.70→1.37), both clearing the 2-bucket/n≥20 confirmation
bar comfortably. This is the strongest confirmed signal of the whole season, on par with the
day-91 3Q wave-1 peak that dope_solo actually caught. Overnight stayed dead the ENTIRE back half
of the season (0.03-0.07 ypa, doy270-305) — don't chase it late, only day_1_5/3Q pay off in the
fall close.**

**Complete S6 season shape: 3Q wave1 (doy93-111, dope_solo caught this, 8.74 score) → 3Q wave2
(doy171-190, ~2 ypa, missed) → day_1_5/overnight 1-bucket spike (doy205-219, correctly passed as
noise) → dead doy220-270 → day_1_5 AND 3Q both reignite hard, tranche 4 (doy280-305+, day_1_5 to
1.58 ypa, 3Q to 1.37 ypa, both still climbing as of doy305, the last day with data). Four distinct
windows this season; dope_solo's front-loaded spend caught only the first.**

**S7 TRANCHE PLAN — FINALIZED, this is the plan to port into S7 day-1 verbatim:**
- 4 tranches of ~$500, hard caps by doy: tranche1 doy<120, tranche2 doy120-200, tranche3
  doy200-280, tranche4 doy280-end-of-season. Never let cumulative spend exceed the current
  tranche's ceiling, no matter how hot a signal looks — this is the direct fix for S6's core
  mistake (spent 98% of the $2000 budget by day111, on just ONE of four confirmed windows).
- Trigger within an open tranche: 2+ consecutive 10-day buckets at ypa≥~0.7-1.0, n≥20 pooled
  across boats in that class — not a single spike, not raw magnitude alone (day-244 rule, holds).
- **Give tranche 4 (doy280-330) extra weight/priority now**: day_1_5 and/or 3Q have peaked hardest
  right at the season close in S1, S3, S4, and now confirmed S6 (4 of 6 seasons). If tranche 3
  (doy200-280) shows no 2-bucket confirmation — as happened in S6, dead except one passed-on
  1-bucket spike — bank that tranche's ~$500 forward into tranche 4 rather than force-spending it.
- **PTO must stay reachable into the fall, not just staged 14+ days rolling.** S6's PTO hit 0
  around day119 and never recovered for the remaining 186 days — that's HALF of why tranche 4 was
  unreachable this turn (budget was already the other half, but PTO=0 independently blocks any
  weekday trip even with cash). For S7: reserve at least 3-4 PTO days uncommitted through doy~250
  specifically so a tranche-4 push in Sept-Nov has weekday PTO available, don't let early-season
  enthusiasm burn all 10 days by day120 the way it burned all the budget.
- Carry forward unchanged: HD_AM/HD_PM/TWILIGHT dead every season (7 for 7 now) — never book;
  class-pooled trailing ypa (fleet-wide, n≥20) beats single-boat picks; no class is the automatic
  season winner (day_1_5 4/6 times, 3Q now 3/6 times counting this wave, sometimes both in one
  season like S6).

**S7 day-1 action: open notes with the tranche plan above as the primary structural rule, combined
with the 6 cross-season rules in the day-244 entry below (still all valid). No more S6-specific
data pulls needed — this was the last one.**

---

## S6 day-274 planning check-in — answers day-244's "does anything re-ignite doy250-330" question,
## partially: YES. Budget $50/PTO 0 unchanged (still below every trip's $80 min fare), season_score
## 8.7443 unchanged, rank 15/34 season-to-date, cumulative 0.0958/rank31 (only S2 counted so far).
## Zero rejected actions since day-244 — nothing to act on either way this stretch. Pure lesson turn.

**Fresh pull, S6 fish_date_doy 240-274, 10-day buckets, ypa=sum(yt)/sum(anglers), real n:**
| cls | 240 | 250 | 260 | 270 |
|---|---|---|---|---|
| day_1_5 | 0.131(18) | **0.822(35)** | **0.828(41)** | 0.299(23) |
| overnight | 0.190(60) | 0.226(85) | 0.590(95) | 0.097(89) |
| three_quarter | 0.337(49) | 0.251(76) | 0.968(75) | 0.214(64) |

**Verdict: day_1_5 gave a genuine 2-consecutive-bucket wave at doy250-269 (0.82/0.83 ypa, n=35/41 —
clears the day-244 rule's "2+ consecutive buckets, n≥20" bar with real depth), then faded back to
0.30 by doy270. This is a real, moderate re-ignition — not as strong as the season's earlier peaks
(1.2-2.0+ ypa) but a legitimate confirmed wave by the trigger rule, arriving right in the
doy250-280 tranche-3 window the day-244 plan earmarked. Overnight and three_quarter each threw a
single hot bucket at doy260 (0.59 and 0.97) sandwiched between cold buckets on both sides — by the
same rule these are NOT confirmed waves, just noise/single-boat spikes, consistent with 6 seasons
of this exact failure mode (see day-213 entry). Operationally irrelevant for S6 dope_solo (budget
already below min fare since day111) but a clean, real-money-would-have-mattered data point for
S7's tranche plan: tranche 3 (doy200-280) would have had a genuine, moderate target here.**

**Nothing new to change in the S7 plan below — this pull is confirmation, not revision.** One
addition: note that a confirmed 2-bucket wave's peak ypa (~0.82-0.83 here) can be well below a
prior wave's peak (1.4-3.4 for 3Q wave 2, 1.0-1.7 for wave 1) and still be worth fishing on a fresh
tranche — don't require the new wave to match the old wave's ypa magnitude, just require it to
clear the 2-bucket/n≥20 confirmation bar and be affordable within that window's tranche.

**Next check (S6 season-end, ~doy330): with S6 basically decided for dope_solo, this is the last
useful data pull before S7 day-1 — confirm doy280-330 (does day_1_5's doy250-269 wave return, or
does something else take over, matching S1/S2's late-season day_1_5 pattern) and then port the
full plan below into S7 day-1 verbatim, refreshed with whatever doy280-330 shows.**

---

## S6 day-244 planning check-in — RESOLVES the day-213 "is day_1_5/overnight's doy210 uptick real"
## question: NO, it was a one-bucket spike that crashed immediately. Budget $50/PTO 0 still,
## nothing bookable (season_score 8.7443 unchanged since day111, rank 15/34 season-to-date,
## cumulative 0.0958/rank31 — still only S2 counted toward cumulative). Pure lesson turn.

**Fresh pull, S6 fish_date_doy 180-244, 10-day buckets, ypa=sum(yt)/sum(anglers), real n:**
| cls | 180 | 190 | 200 | 210 | 220 | 230 | 240 |
|---|---|---|---|---|---|---|---|
| three_quarter | 2.013(31) | 1.621(46) | 0.534(67) | 0.300(73) | 0.279(93) | 0.022(70) | 0.335(87) |
| day_1_5 | 0.578(13) | 0.997(30) | 0.950(35) | **1.908(47)** | 0.078(56) | 0.080(42) | 0.144(35) |
| overnight | 0.778(21) | 0.576(39) | 0.349(69) | **1.207(70)** | 0.093(92) | 0.083(103) | 0.203(102) |

**Verdict: the day-213 note's "day_1_5/overnight just broke out at doy210" read was WRONG in
hindsight — it was a single 10-day bucket spike (real n=47/70, not noise) that collapsed
immediately the very next bucket and has stayed near-dead (0.08-0.20 ypa) for 30+ days since
(doy220-240). Three_quarter, which the day-213 note called "faded hard," also stayed dead/flat
through doy220-240 (0.02-0.33). So as of doy244, ALL THREE classes are simultaneously cold —
this looks like S6 rolling into a genuine late-season dead patch across the board, not a
rotation into a new winning class. Full season picture: 3Q wave1 (doy93-111, where dope_solo
fished) → 3Q wave2 (doy171-190, ~2 ypa, missed, budget already gone) → brief day_1_5/overnight
spike (doy205-219 roughly, ~1.2-1.9 ypa, also missed) → dead since doy220. Three separate windows
worth fishing this season, dope_solo caught only the first.**

**THE KEY NEW LESSON FOR S7 (refines, doesn't replace, the day-182/day-213 budget-pacing rule):
a single hot 10-day bucket is NOT enough to call a "breakout" or "class rotation" — wait for at
least 2 consecutive hot buckets (as the original day-91 rule said for the initial 3Q call) before
treating it as a real wave worth committing meaningful budget to, even when n is large. The day-213
note broke its own rule by calling day_1_5/overnight's doy210 print a confirmed breakout off ONE
bucket. This doesn't change the top-line S7 rule (never fully spend down budget early — three
separate windows now confirmed missed in S6 alone) but sharpens the trigger: 2+ consecutive
10-day buckets clearing ~1.0+ ypa on n≥20, not one.**

**S7 budget-tranche rule, now finalized with S6's full picture:**
- Split $2000 into roughly 4 tranches of ~$500, released one at a time as the calendar advances
  (e.g. don't let >~$500-600 be spent before doy~120, another ~$500 released doy120-200, another
  doy200-280, final ~$400-500 reserve for doy280-330). This would have let S6's dope_solo catch
  wave 1 (doy93-111, tranche 1) AND wave 2 (doy171-190, tranche 2) AND the day_1_5/overnight spike
  (doy205-219, tranche 3), instead of blowing tranche 1+2+3+4 all by day111.
- Within each open tranche, still use the trailing-ypa trigger (2+ consecutive hot buckets, n≥20)
  from the day-91 rule — the tranche cap prevents over-committing to any single window, the ypa
  trigger prevents wasting a tranche on noise.
- A tranche that goes unused by its window's end just rolls forward — don't force a spend.

**Next check (S6 season-end, ~doy330): confirm whether anything re-ignites doy250-330 (S1/S2
pattern) or S6 stays dead the rest of the way. Either way, nothing operationally different for S6
itself (budget <$80 min fare, PTO 0) — this is 100% S7-prep. At S7 day-1, write the 4-tranche plan
above into the live plan, combined with the still-valid pieces: class-pooled trailing ypa over
single-boat picks, PTO staged rolling 14+ days ahead, HD_AM/HD_PM/TWILIGHT confirmed dead 7
seasons running, don't anchor on any one class as automatic season winner (S3/S4/S6-wave1 rewarded
day_1_5/3Q early, S5/S6-wave2 rewarded 3Q mid-season, S6's doy210 spike rewarded day_1_5/overnight
briefly — the class that pays varies, only the tranche discipline should be fixed).**

---

## S6 day-213 planning check-in (superseded above — the "day_1_5/overnight breakout" call here
## was premature, see day-244 entry). Kept short for history: flagged doy210 day_1_5 1.908/overnight
## 1.207 (n=47/70) as a possible new wave replacing 3Q's faded wave-2; day-244 pull shows it
## collapsed to 0.08-0.20 by doy220 and stayed there through doy240 — was a 1-bucket spike, not a
## wave. Lesson: require 2+ consecutive hot buckets before calling a rotation, not just large-n.

## S6 day-182 planning check-in — identified 3Q's wave 2 (doy171-190, ~1.4-3.4 ypa, real fleet-wide
## signal) which dope_solo's budget (exhausted by doy111) could not catch. This is real and
## confirmed by day-244's pull (2.0/1.6 ypa at doy180/190 buckets) — unlike the day-213 call, this
## one held up. Full reasoning in git history of this file if ever needed; condensed into the
## day-244 entry's season-shape summary above.

## S6 day-152 planning check-in — checked doy110-152, saw 3Q declining (2.489→0.297) and day_1_5/
## overnight never breaking out; concluded "single-wave front-loaded season, no missed second wave."
## This was WRONG (day-182 pull found wave 2 starting doy171, just past this check-in's data
## window) — cautionary tale, kept for the lesson: always pull through the most recent available
## day, not just through the last checked bucket, when verifying a "no re-ignition" conclusion.

## S6 day-121 planning check-in — season effectively over for dope_solo: budget $1950/2000 spent
## by day111 (3x OVERNIGHT + 5x THREE_QUARTER, all in doy93-111), $50 left, below every trip's min
## price ($80). Flagged the core mistake: spent 98% of budget in the first 20 nightly-decision days
## of a ~230-day window. This is the root cause the day-244 tranche rule above is designed to fix.

**Trip results, all settled/ran (for reference, unchanged since day-121):**
OVERNIGHT x3 (d094/095/101): shares 0.111, 1.409, 1.118. THREE_QUARTER x5 (d106/108/109/110/111):
shares 1.706, 1.403, 0.308, 0.957, 1.733. Total season_score 8.7443, rank 15/34 season-to-date.

---

## S6 day-91 planning check-in — NIGHTLY DECISIONS START. Confirmed 3Q sustained 1.1-2.0 ypa
## doy60-91 (n=8-32/bucket), day_1_5 pulled back to 0.67-1.27, overnight n too small to trust yet,
## HD_AM/HD_PM still dead. Told nightly-self to trust the pre-confirmed 3Q signal immediately, stage
## PTO rolling 14+ days ahead, watch day_1_5 for re-acceleration, keep $600-800 reserve for a fall
## day_1_5 breakout. **What actually happened: nightly-self correctly fished 3Q hot (avg share
## ~1.2-1.7/trip) but blew through the ENTIRE budget by doy111 instead of holding the reserve — the
## day-91 rule said "keep $600-800 in reserve" but had no hard per-window cap, so it didn't bind.
## The day-244 tranche rule (hard $ cap per calendar window, not just a soft reserve target) is the
## fix for this specific failure.**

## S6 day-60 / day-32 pre-season checks (condensed): winter doy0-60 ypa was unusually hot for
## day_1_5 (1.5-3+) and 3Q (0.5-3), ONI climbing to 0.7-0.8 (El Niño territory) — correctly
## predicted an early-breaking season, which is what happened (3Q wave 1 at doy93-111 right as
## nightly decisions opened). This part of the read was good; the failure was pacing the spend
## once the signal confirmed, not spotting the signal.

---

## SEASON 6 DAY-1 PLAN (original, written before any S6 nightly data) — still the source for the
## cross-season "season shape varies" finding below; operational rules superseded by day-244 above.

**Cross-season class-pooled ypa by 20-day doy bucket, S1-S5, full year — season shape is NOT
consistent year to year:**
| season | what won the fall, when |
|---|---|
| S1 | day_1_5, modest, late (doy280-335) |
| S2 | day_1_5, huge (4.3-5.0 ypa doy270-289), but dope_solo missed it (spent too early, cautionary tale — 12 cheap probes, $1900, for 0.096 score) |
| S3 | day_1_5 early (doy160, 2.8 ypa) through fall peak (4.4-4.6, doy290-310); 3Q also strong doy280-290 |
| S4 | day_1_5 early (doy160, 4.25 ypa) and dominant all the way to doy280-310 (4.2-5.9) |
| S5 | day_1_5 built early then COLLAPSED doy220+; THREE_QUARTER took over the fall instead (1.3-3.5 ypa doy280-330) |
| S6 | 3Q wave1 doy93-111 (dope_solo caught this) → 3Q wave2 doy171-190 (missed) → day_1_5/overnight 1-bucket spike doy210 (missed) → dead doy220-244 |

**Rules that held up across all 6 seasons, keep for S7:**
1. HD_AM/HD_PM/TWILIGHT confirmed dead every season — never book.
2. Class-pooled trailing ypa (fleet-wide, n≥20+) beats single-boat/single-day picks — proven
   repeatedly, including within dope_solo's own S6 trip selection (San Diego/Mission Belle
   alternation by trailing ypa worked, avg 1.2-1.7 share/3Q trip).
3. PTO must be staged rolling ~14+ days ahead continuously, not just when a signal fires (S2's
   journal — 280+ consecutive "nothing bookable, no PTO staged" nights — is the cautionary tale;
   S6 avoided this, only 1 rejected action all season).
4. Don't assume any one class is the automatic season/fall winner — it's varied every season
   (day_1_5 4/6 times, 3Q 2/6 times, and even within S6 the "winning" class rotated 2-3 times).
5. A single hot bucket is not a confirmed wave — require 2+ consecutive 10-day buckets at
   elevated ypa (n≥20+) before committing real budget (new for day-244, see above).
6. **The single biggest lever left unaddressed until day-244: hard per-calendar-window budget
   caps (tranches), not just a soft "keep some reserve" instinct** — S6 proves the soft version
   doesn't bind under real-time pressure from a hot confirmed signal.

## Open items carried forward
- Leaderboard as of day244: dope_solo season_score 8.7443, rank 15/34 (mid-pack, big improvement
  over S2's 0.0958/rank31). Top season performers this tick: ens_solo 23.97, thrifty 20.38,
  thrifty_solo 19.60 — all "no strategy yet" (plain nightly decisions, no custom strategy.py),
  same as dope_solo, confirming again the gap is nightly-decision quality/pacing, not tooling.
  Cumulative leaders (ens_solo 15.27, elnino 15.33, frontloader 14.20) show consistent
  season-over-season scoring matters more than any single big season.
- No forum/submit_strategy access confirmed for this solo variant across 6 seasons — stop
  re-checking unless the toolset visibly changes.
- S7 day-1 planning turn: write the full plan starting from the day-244 tranche rule + the 6
  cross-season rules above. That should be the primary structural fix; everything else
  (trailing-ypa trigger, PTO staging, boat selection) already works.
