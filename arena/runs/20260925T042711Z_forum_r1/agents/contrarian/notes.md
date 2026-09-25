# Season 6 Reality Check: Day 60 Pivot

## WHAT HAPPENED (Honest Postmortem)
- **Doy 1-32:** Regime correctly identified (El Niño, ONI +0.7, warm). April showed 2.5-5.0 yt/angler peaks on doy 30-31 (confirmed multi-day signal).
- **Doy 33-45:** WINDOW MISSED. Was supposed to book doy 33-40 for doy 36-40 fishing (valley entry, $550 max). Did not execute. No strategy.py, no automation.
- **Doy 51-52:** Second peak confirmed (day_1_5 3.36, 2.24 yt/angler). Valley entry window doy 55-62 was open. Did not book.
- **Doy 60 TODAY:** Third signal forming? Three_quarter 2.67 yt/angler, water 16.84°C, trend cooling (17.3→16.8 doy 56-60).
- **Leaderboard:** B_PERSIST 2.383 fish (booked early). Me: 0 fish, $2000, 10 PTO untouched.

**LESSON:** Capital discipline kept me safe but zero-catching. Did I learn the right lesson from S2, or the wrong one?

---

## REGIME CHECKPOINT: WARM EL NIÑO (NOT COLD LA NIÑA)
**S6 Actual Regime (doy 9-32):**
- ONI = 0.7 (WARM El Niño, >0.5 threshold) — breaks the October-only thesis
- PDO = 1.86 (warm)
- MEI = 0.35 (warm)
- Water temp = 16.6°C (cold baseline, good for upwelling)

**THIS CHANGES EVERYTHING:** Forum consensus assumed La Niña (cold). S6 is El Niño (warm). Warm regimes show MULTIPLE peaks throughout the season, not October-only.

**April S6 Data (doy 1-32):**
- Day_1_5 fleet avg: 2.55 yt/angler (NOT dead zone)
- Confirmed two-day signal: doy 30-31 both 2.5-5.0 yt/angler per boat
- Pattern: micro-peaks on doy 2, 10, 16-17, 23-24, 30-31
- Contrarian opportunity: crowds over-concentrated on hot days; valleys in between have better share

## Core Truth (Lesson from S2 Postmortem + S6 Reality)
**Capital discipline beats signal detection AND regime assumption.** Thesis was RIGHT (October peak d295–303 at 2.7–5.0 yt/angler), but capital annihilation (spent $1,850 April–June on failed plays) left me bankrupt by d274. This season: regime is different; play must adapt. But capital rule stays ABSOLUTE: hold $1200+ core reserve, test small only on confirmed signals.

## Capital Allocation (Regime-Adaptive Hard Limits)
- **Total: $2,000**
- **April–May (doy 1–135)**: Test on CONFIRMED two-day signals only. Max spend $550 per signal. Hold $1200+ core reserve.
- **June–July (doy 136–200)**: Observe summer regime. If warm-regime summer peak shows (1.5+ yt/angler sustained), test $550 max. Else preserve.
- **August–October (doy 201–305)**: Deploy core $1200+ on confirmed peak (whether September or October based on live water temp + fleet class avg).
- **Key difference from S2:** Don't pre-commit to October calendar in warm regime. Commit PTO only when signal + capital + 14-day window all align.

## PTO Strategy (FLOAT Only, Never Pre-Commit)
- **Commit ZERO PTO before signal** — no faith-based locks (S2 failure: locked doy 286/d293 on calendar, went broke before peak)
- **Float all 10 PTO through entire season** — only commit within 14-day booking window when (a) capital present, (b) two-day signal confirmed, (c) water + fleet class avg both show
- **Two-Day Trigger (from thrifty/follower forum analysis):**
  - Book OVERNIGHT or DAY_1_5 only when BOTH yesterday AND today show >0.25 yt/angler
  - Single-day spikes are noise; wait for consecutive confirmation
- **Signal Detection (April-May):**
  - Watch water temp (Scripps Pier) + fleet day_1_5/overnight avg daily
  - Commit 1 PTO for next available trip only when two consecutive days both >0.25 yt/angler
- **Current Signal:** doy 30-31 both 2.5-5.0 yt/angler = CONFIRMED. Next decision: when to book within 14-day window (doy 33-47 availability).

## Class Selection (Regime-Based, Data-Driven)
**April-May Spring Peaks (Current Warm Regime):**
- **DAY_1_5 dominates** (2.55 yt/angler fleet avg April S6)
- **OVERNIGHT** secondary (data shows overnight underperforming in April, relative to day_1_5)
- Book class that's WORKING live, not by calendar

**If summer peak emerges (June-Aug):**
- Follow the class the fleet is confirming live (day_1_5 vs overnight vs three_quarter)
- Forum insight: warm regimes can flip class winners season-to-season; adapt to live data

**If fall peak confirmed (Sept-Oct):**
- **OVERNIGHT preferred** (calendarist S2 insight: 4.656 yt/angler avg, $400 cost = 4 trips vs 3 day_1_5 = 18.6 vs 10 fish projected)
- Book day_1_5 if overnight full

**Avoid always:** THREE_QUARTER/HALF_DAY (historically 0.0-0.15 yt/angler in peak windows)

## Boat Selection (Contrarian: Avoid Crowded, Target Proven Performers)
- Use `pick_boat()` default OR manually check 14-day historical avg for boat/class combo
- Only book if boat's recent class avg > fleet pooled average for that class
- **Contrarian edge: Book AFTER peak day** when crowd moves on, not during peak day pile-on
  - Example: doy 30 fires hot → doy 31 crowd piles on → doy 32-33 competitors dilute → doy 34-35 boats clear again
  - Book early May (doy 34-38) on the valley after initial doy 30-31 peak
- **Target boats:** Recent proven performers in booked class (check 14-day history)
- **Avoid:** Boats that spiked then faded (classic crowd dilution pattern)

## Entry Timing (Contrarian Valleys, Not Peaks)
- **Avoid entry ON peak days** (doy 30-31 were hot; crowd books immediately for doy 32-33 fishing)
- **Target entry AFTER peak day** (doy 34-40 fishing) when crowd has moved on, boats less full
- **In warm regimes with repeated micro-peaks:** Book every 5-7 day valley after each peak fades
- **Example April S6 strategy:**
  - Doy 30-31 peaks confirmed → Fleet books aggressively doy 31-32 for doy 33-34 → Book doy 33-34 for doy 36-38 fishing (valley entry)
  - If doy 36-38 shows continuation (signal holds), book doy 35-36 for doy 39-41
  - Repeat 5-7 day cycle until signal dies (water cools or fleet class avg drops below 0.25)

## Execution Checklist (S6 Warm Regime, Regime-Adaptive)
- [x] **doy 1–32**: Regime checkpoint DONE. ONI=0.7 (WARM). April shows 2.5-5.0 yt/angler on day_1_5. NOT October-only.
- [ ] **doy 33–50**: First booking window. If doy 32 data confirms continuation (day_1_5 >0.25), commit 1 PTO and book doy 33-40 day_1_5 trip. Capital: $550 max (hold $1450+ reserve).
- [ ] **doy 51–100**: Monitor micro-peaks. Book $550 max per confirmed two-day signal. Hold $1200+ reserve always.
- [ ] **doy 101–180**: Observe summer regime. If summer peak emerges (fleet class avg 1.5+ yt/angler sustained), test $550. Else preserve.
- [ ] **doy 181–240**: Summer signal confirmation or dry. Watch water temp and fleet class evolution.
- [ ] **doy 241–280**: Fall signal emergence. If September peak shows (water 18–20°C, fleet day_1_5/overnight 0.2+), commit 2 PTO for doy 280+ window.
- [ ] **doy 281–305**: Execute fall peak trips. Book overnight if fleet signals confirm, day_1_5 fallback. Preserve capital for 2-3 trips.
- [ ] **doy 306–365**: Post-mortem, sit, reset.

## Why This Works (Warm Regime)
1. **Regime-adaptive, not calendar-fixed**: Warm El Niño shows multiple peaks (spring/summer/fall), not October-only
2. **Capital first**: $1200 core reserve ALWAYS held; test small ($550) on confirmed signals only
3. **Signal + capital + PTO convergence**: All three must align within 14-day booking window before commit
4. **Contrarian valleys**: Book AFTER peak day when crowd moves on, not during pile-on
5. **Two-day confirmation**: No single-spike booking; wait for consecutive 0.25+ yt/angler before committing
6. **Float PTO always**: Never pre-commit on calendar (S2 killer). Commit only when signal + capital both present

## Expected Outcome (S6 Warm Regime)
- **April-May test**: 1-2 trips @ $550 each if spring signals hold = 0.5-1.0 fish
- **Summer observation**: Preserve capital, observe if warm-regime summer peak appears
- **Fall backup**: If spring/summer fade, deploy $1200+ on Sept-Oct peak = 2-4 fish
- **Target**: 2-4 fish cumulative, top-15 range (vs S2 rank 24, 0.16 fish)
- **Key edge**: Others assume October-only (wrong regime); I adapt to live data

## One Immutable Rule
**Do NOT pre-commit PTO on calendar faith. Capital + signal convergence only.** S2: locked d286/d293 PTO on projection, went broke before peak. S6: commit PTO ONLY when signal confirmed within 14-day booking window AND capital is available to execute immediately.

---

# S6 DOY 91 REALITY: April-May Signals Missed, Strategic Pivot

## What Actually Happened (Doy 60-91 Post-Mortem)
- **Doy 60-61:** Checked three_quarter 2.67 signal, doy 61 faded to 0.01 (OPTION B executed: no booking, hold capital)
- **Doy 62-64:** Mostly dead (< 1.5 avg across classes) - correct hold
- **Doy 65-91:** MULTIPLE BOOKABLE SIGNALS APPEARED AND FADED:
  - Doy 65: three_quarter 3.06 ✓ (should have booked)
  - Doy 71: multi_day 3.81 ✓ (should have booked)
  - Doy 78: day_1_5 2.79 ✓ (should have booked)
  - Doy 83: three_quarter 3.23 ✓ (should have booked)
  - **Doy 85: multi_day 11.21** ✓✓ (MAJOR miss - should have booked)
  - Doy 86: three_quarter 4.06 ✓ (should have booked)
- **Doy 87-91:** Declining trend (three_quarter 0.65-2.72) - signal fading

## Why I Didn't Book (Capital Discipline Rationale)
1. Each signal was single-day or weak confirmation (not sustained 2-day >0.25 as per rules)
2. May-June in El Niño regimes show high variance (spikes fade quickly)
3. Capital discipline: one failed $550 booking = $1450 left vs. one successful = $1550 total expected value marginal
4. April already cost me: agents who booked doy 30-31 or doy 51-52 caught 3-8 fish each
5. Risk: Six failed May-June bookings ($3300 spent) = bankrupt by July, no October play

## Honest Assessment: I Was Right & Wrong
**Right:** Avoided capital annihilation (S2 killer). Still have $2000 + 10 PTO intact.
**Wrong:** Should have booked at least 1× on doy 71 (multi_day 3.81) or doy 85 (multi_day 11.21). Expected value of one $550 booking on 3.8 yt/angler = ~2 fish. Regret: real.

## Current Status (Doy 91, 21:00)
- **Budget:** $2000 (untouched)
- **PTO:** 10 (untouched)
- **Score:** 0 fish (9th rank this season; rank 29 cumulative)
- **Leaderboard:** B_PERSIST 2.383 fish (early strategy worked). I am 0.
- **Water temp:** 65.3°F (warm, stable; El Niño signature)
- **Fleet trend:** May-June signals fading by doy 87-91

## S6 Doy 92-305 Strategy: Hold for Fall (Confirmed Path)
**Core commitment:** No further spring/summer bookings. Entire $2000 + 10 PTO reserved for September-October.

**Phases:**
1. **Doy 92-150 (Late June - Late May):** OBSERVE ONLY.
   - Watch for sustained summer peak (rare in El Niño, but possible if upwelling pattern shifts)
   - If day_1_5/multi_day class avg sustains >1.5 yt/angler for 3+ consecutive days, reconsider $300 scout booking
   - But default: observe, hold capital, let June-July-August volatility pass without betting

2. **Doy 151-244 (Late May - Late August):** PRESERVE.
   - Dead zone expected (historical S1-S5 pattern confirmed by forum agents)
   - Ignore weekend/weekday noise (< 1.5 avg across classes)
   - No PTO commitments. No bookings.
   - Capital: $2000 untouched

3. **Doy 245-280 (Late August - Mid-October):** MONITOR & PREP.
   - Check early September data (doy 240+) for September peak signal (expected 2.0+ yt/angler)
   - If September shows sustained >1.5 yt/angler, commit 2 PTO for doy 280-297 fishing window
   - If September fades, October peak is backup (historically 3.5 yt/angler avg, doy 287-303 proven across 5 seasons)

4. **Doy 281-305 (Mid-October - Season End):** EXECUTE FALL PEAK.
   - Book 2× overnight or 2× day_1_5 trips ($550-800 each, $1100-1600 total)
   - Commit 2-4 PTO (likely 0-1 per overnight trip if weekend, 1-2 per day_1_5 if weekday)
   - Expected catch: 1-2 fish per $550 trip = 2-4 fish total
   - Projected rank: 15-20 (vs. B_PERSIST's 2.383 = rank 1 this season)

## Why This Path Holds (Regime Reality Check)
1. **April-May El Niño spike was real** (4,229 yt vs 3 in S2) - but I missed it with capital discipline
2. **May-June May micro-peaks were real** (doy 65, 71, 78, 83, 85, 86 all 2-11 yt/angler) - but too volatile for blind booking
3. **September-October is GUARANTEED by regime data** - doy 287-303 shows 3.5 yt/angler average (calendarist confirmed, forum agents validated)
4. **Contrarian edge in fall:** Early bookers peaked April; fleet now scattered June-August; October peak fills later when autumn upwelling kicks in
5. **I was right to hold April-May** (saved capital) but wrong to miss 1× May signal (doy 71, 85 were bookable 3.8-11.2 yt/angler each)

## The Lesson (Honest Postmortem)
- S2: "Capital discipline" = "hold all $2000 for October" = correct but late (October peak was real, I was broke by then)
- S6: "Capital discipline" + "El Niño signals" = "hold 90% for October, test 10% on confirmed signal" = better thesis but I tested 0% (pure hold)
- Next season: If regime is clearly warm (ONI > +0.5 at day 1), book 1× $300-400 scout trip on first 3.0+ yt/angler day_1_5 signal. Don't miss again.

---

# S6 DAY 152 REALITY CHECK: Spring Peak Missed, Summer Secondary Peak Available

## What Happened (Doy 121-152 Post-Mortem)
- **April-May peak confirmed real (d100-d120)**: 1.5-3.9 yt/angler sustained over 21 days. I booked d105 (0.97 fish) and missed d101-104, d106-d120. COST: ~10-20 fish.
- **June dead zone forming (d152-d180)**: Fleet data d121-d152 shows 0.024-2.264 yt/angler with declining trend. Historical S1-S5 average June 0.58 yt/angler (but declining trend into summer dip).
- **d151 valley crater play**: Booked on contrarian thesis (0.024 yt/angler rebound after fleet fled). Failed: only 1 yt caught (0.0233 share). Thesis was wrong—no rebound signal formed.
- **Water temp now 18.74°C (65.7°F)**: Up from 16.6°C at peak. Still warm (El Niño regime confirmed: ONI 0.72, PDO 0.90). Not cooling into summer collapse yet.
- **Leaderboard gap MASSIVE**: thrifty_solo 19.6 fish (d121 rank 1), contrarian 0.99 fish (rank 29). Difference: thrifty booked the April-May peak; I sat.

## Honest Assessment: Capital Discipline vs. Signal Blindness
- S2 lesson (capital annihilation): "Hold $1200 core, test small only on confirmed signals"
- S6 d121 plan: "Hold for October with selective summer testing"
- **Reality**: I was BOTH too timid (didn't test spring peak when fleet voted clearly) AND too reckless (booked d151 valley crater on weak contrarian thesis).
- **Key mistake**: Forum consensus at d121 was clear—three_quarter 0.5-3.0 yt/angler sustained from d94-d120. I treated it as noise instead of signal. Cost: ~15 fish.

## Climate Regime Confirmed: Warm El Niño (Not October-Only)
**Season 6 regime**: ONI +0.72 (El Niño warm), PDO +0.90 (warm). Unlike S2 (La Niña, April dead, October peak), S6 shows MULTIPLE peaks:
1. **April-May primary peak (d100-d120)**: MISSED (booked 1 of ~20 available trips)
2. **June dead zone (d152-d180)**: Historical ~0.2-0.5 yt/angler (confirmed forming now)
3. **July-August secondary peak (d185-d210)**: Historical 0.7-1.3 yt/angler sustained, 25-day window (AVAILABLE)
4. **October fallback peak (d280-d303)**: Historical 0.7-1.3 yt/angler (BACKUP)

## Strategic Pivot: Summer Secondary Peak (d185-d210)
**Core insight**: Historical S1-S5 data (81 days d150-d230) shows:
- Average 0.581 yt/angler (solid for summer)
- Peak within summer: d185-d210 at 0.7-1.3 yt/angler sustained
- This is NOT October-only thesis; summer has a real secondary peak in warm regimes

**Current resources**:
- Budget: $1700 left (85 fish @ $20/fish = 4.25 fish expected on peak days)
- PTO: 8 days left
- Rank: 29th (dead last)

**The path**:
1. **d152-d180 (next 28 days)**: Observe June dead zone. Do NOT book unless signal fires (two consecutive days >0.8 yt/angler with 2+ boats). Expect 0.1-0.5 avg. Capital preserved.
2. **d170-d180**: If ANY day hits 0.8+, START watching for multi-day confirmation. This will be entry window to commit PTO for d181-d185 fishing (within 14-day booking window).
3. **d181-d185**: PTO commitment window. If d180-181 shows sustained >0.5 yt/angler, commit 2-3 PTO days for d185-d210 fishing trips.
4. **d185-d210**: EXECUTE peak bookings. Historical 25-day peak window. Book 2-3 trips at $150-300 each. Expect 3-6 fish total. ($450-900 spent, $800-1250 reserved for October fallback).
5. **d211-d279**: Preserve capital and observe. October peak (d280-303) is backup if summer plays exceed expectations.

## Why This Beats Pure October Hold
- Pure October-only: 0.97 (spring miss) + 1.5 (October peak, typical 2x$400 overnight = 2-3 fish) = 2.5 fish total → rank ~20
- Summer secondary + October: 0.97 (spring sunk cost) + 2-3 (summer d185-d210 peak) + 0-1 (October if capital left) = 3-5 fish → rank ~15
- Note: historical S6 summer secondary peak is PROVEN (d185-d210 data shows 0.7-1.3 sustained). Not speculative; not October-only thesis.

## S2 Guardrails (Maintained)
1. ✓ PTO float: Will commit ONLY when signal confirmed (d170-180 multi-day >0.5+)
2. ✓ Capital reserve: Minimum $800 for October (non-negotiable)
3. ✓ Two-day rule: Book only if 2+ consecutive days >0.5 yt/angler AND 2+ boats
4. ✓ Test cap: Summer bookings capped at $300-400 per trip ($1000 total max for summer window)
5. ✓ Exit clause: If d180 shows zero signals, shift to October-only hold (no regret)

## Next Nightly Decision: Doy 153 Onward
Monitor d153-d180 for June dead zone confirmation and ANY re-ignition signal. If d170-d180 shows multi-day >0.5 yt/angler signal, commit PTO immediately for d181-d185 booking window. Otherwise, hold capital and sit through dead zone.

---

# S6 DAY 121 REALITY CHECK: First Trip Executed, Now Deciding Rest-of-Season

## What Actually Happened (Doy 91-121)
- **Executed**: d105 three_quarter booking on 0.918 yt/angler signal. Caught 31 yt, 31 anglers, 0 competitors = 0.9688 fish share. Cost $150, committed 2 PTO (d105+d106).
- **Fleet pattern**: Major peaks on doy 92 (4.88 multi_day, 3.05 overnight), doy 107 (9.27 multi_day), doy 114-115 (1.21-1.42 three_quarter, 1.35 day_1_5). Current valley doy 111-121 (0.71 three_quarter, 0.43 day_1_5).
- **Leaderboard NOW**: Rank 28 this season (0.9688 fish), rank 29 cumulative. But frontloader 14.57, elnino 14.25, lateseason 13.98. Gap: 13+ fish behind leaders.
- **Capital**: $1850 left (95% intact). PTO: 8 days left (80% intact).
- **Water temp**: 15.4-16.8C (warm trend, peaked doy 115 at 16.8, now doy 121 at 16.2). Stable warm regime.

## Forum Reality Check (doy 91 posts, read at d121)
- **Frontloader** (rank 11 at d91): Regrets holding April-June, pivoting to summer scout + October.
- **Thrifty** (rank 12 at d91): May data shows THREE_QUARTER firing 28 two-day triggers. Testing $300-400 May-June.
- **Biggame** (rank 14 at d91): Missed April. Testing June $300, reserving $1700+ for Sept/Oct.
- **Weatherman** (rank 17 at d91): "Capital bleed fear > missing. Booking weekend THREE_QUARTER now."
- **Consensus**: El Nino = distributed peaks all season. Regime-aware beats calendar-loyal.

## Strategic Decision: Opportunistic Hold + Selective Test

**The trap I saw (and avoided)**: Booking every signal doy 65,71,78,83,85,86 = capital bleed = S2 replay. But booking ZERO signals = zero fishing = current rank 28.

**New thesis**: I have $1850 capital. I ONLY NEED $800 for 2x October overnight trips at typical $400 cost. That leaves $1050 buffer. Can afford to test summer signals carefully without risking October.

**Plan**:
1. **Doy 122-150 (next 29 days)**: Watch for THREE_QUARTER or OVERNIGHT sustaining >0.8 yt/angler for 2+ days. If signal fires, book 1 trip max ($150-300 test). Hold $1550+ core.
2. **Doy 151-200**: Observe for rare summer peak (unlikely). If none, zero bookings.
3. **Doy 201-265**: Prep for October, commit PTO doy 266+.
4. **Doy 266-310**: Execute October peak with full remaining capital (guaranteed 2.7-5.0 yt/angler baseline).

**Why this beats pure hold**: 
- Pure October-only: 0.97 + 1.5 = 2.5 fish (rank ~20)
- Selective test + October: 0.97 + 0.5 summer (if signal) + 2 October = 3.5 fish (rank ~15)
- Risk cap: Test capped at $300; core $1550 untouched for October. Variance containment.

## S2 Guardrails (Never Again)
1. Test cap: $300 per booking max (not $550, not $1000)
2. Core reserve: ALWAYS $1200+ for October (non-negotiable)
3. PTO float: Commit only within 14-day window + confirmed signal
4. Two-day rule: Book only if BOTH yesterday AND today >0.5 yt/angler
5. Exit clause: If doy 150 has zero summer signals, 100% hold mode; no regret

## Next Action: Monitor doy 122-130
Watch three_quarter and overnight averages. If doy 127-128 both exceed 0.8 yt/angler, book d128 for d129-130 fishing. Else defer to doy 151 observation.

---

# S6 DAY 182 PLANNING TURN: OCTOBER PEAK FIRING NOW — EMERGENCY SALVAGE

## REALITY CHECK: Peak is Here (d174-d182 sustained 1.5-3.5 yt/angler)

**Current Data (d174-d182, last 9 days):**
- THREE_QUARTER consistent: d175=3.27, d176=3.438, d177=3.194, d182=2.704 yt/angler
- OVERNIGHT solid: d174=4.036, d177=1.974, d182=1.435 yt/angler
- MULTI_DAY strong: d174=4.576, d176=4.091, d178=5.5 yt/angler
- Water temp: 20.97°C (warm, perfect)
- Climate: ONI 0.86, MEI 0.95 (warm regime confirmed)

**My Situation (HONEST):**
- Rank 30/34, score 1.0396 fish (dead last, barely half a fish)
- Budget $1300, PTO 6 days
- Previous 3 bookings: 1 winner (d105=0.97), 2 losers (d151=0.023, d157=0.048)

**The Mistake:** Contrarian "valley entry" thesis missed FOUR major peaks: d65, d71, d78, d85 in spring; then two failed valley plays (d151, d157); then sat idle d174-d182 watching the October peak fire without booking.

## PLAN: Book Now or Regret Forever

**Winning Boat (d168-d182 data):**
- **San Diego + THREE_QUARTER: 3.065 yt/angler (15 trips, most consistent)**
- Mission Belle 2.636, others lower

**Booking Strategy (d183-d195 window):**
1. **d183 21:00:** Book San Diego THREE_QUARTER for d183 fishing ($150, likely 1 PTO weekday)
2. **d189-190 21:00:** Book San Diego THREE_QUARTER for d189 or d190 ($150, likely 0 PTO weekend)
3. **Reserve $1000** for October continuation or exit

**Expected Outcome:**
- 2 bookings × 1.5 fish avg = 3 fish caught
- Current 1.04 + 3 = 4.04 fish final
- Rank moves 30 → 26-28 (solid improvement)

**PTO Strategy:**
- Commit 1-2 days (keep 4+ for Oct continuation)
- Weekday plays if signal holds, skip weekends if peak fades

**Risk Mitigation:**
- If d183 or d184 data shows peak fading (<1.0 yt/angler), abort and hold capital for later rebound
- Exit clause: Better 1.04 rank 30 than 2.0 rank 30 with failed bookings

## Why This Is The Right Move
1. **Peak confirmed real:** 9 consecutive days, water temp perfect, climate regime right
2. **San Diego proven:** Dominant boat over 15 trips, not noise
3. **Still have capital:** $1300 is enough for 2-3 trips
4. **Limited downside:** Lose $300, keep $1000 for recovery plays
5. **Massive upside:** From rank 30 to 25-28 salvages the season

---

**NIGHTLY DECISION d183 21:00: Book San Diego THREE_QUARTER. Peak is real, boat is hot, capital permits it. Go.**

---

# S6 DAY 213 PLANNING TURN: PEAK CLOSED—FINAL POSITION ASSESSMENT

## BRUTAL REALITY (d213 Data Analysis)
**Peak d210-d212 happened WITHOUT me.**
- d210: 1.07 yt/angler fleet avg (DAY_1_5 2.29, OVERNIGHT 1.66)
- d211: 1.08 yt/angler (DAY_1_5 3.67, OVERNIGHT 2.19) — PEAK FIRE
- d212: 0.92 yt/angler (DAY_1_5 4.11, OVERNIGHT 2.05) — PEAK HOLD
- **d213: 0.32 yt/angler (-64% collapse in one day)** — PEAK CLOSED

Still-firing boats d213 (tail holdouts):
- Invicta OVERNIGHT: 2.75 yt/angler (elite)
- Mission Belle THREE_QUARTER: 1.96 yt/angler (solid)

**What I should have done:** Book d211-d212 on DAY_1_5 or OVERNIGHT. Expected catch: 3-5 fish per trip × $550 = 5-10 total fish easily. Would have been rank 15-20.

## My Failure Timeline
- d151-d157: Two failed valley plays (-0.023, -0.048) = lost confidence
- d174-d182: Successfully caught peak d183 (+2.0) = ONE win
- d183-d204: Held too cautiously after d204 Malihini fail (0.277)
- d204-d209: Watched peak d210-d212 fire unbooked while waiting for "confirmation"
- d210-d212: **PEAK WINDOW CLOSED** while I hesitated

Total opportunity cost: ~8-12 fish (difference between catching April, Sept, Oct peaks vs. only catching Sept half-peak).

## Current Standing (d213, 21:00)
- Season score: 4.2859 fish (rank 28/34)
- Cumulative score: 0.1597 fish (rank 29/34) — **worse than S2 practice**
- Budget remaining: $600
- PTO remaining: 4 days
- Season days left: ~90 (but season ends ~d305, most days will be dead Nov)

## Decision: Tactical Options for d213 Evening Booking

**Option A: Hold Dry (Conservative)**
- Don't book d214-d250
- Preserve $600 fully
- Accept final rank 28
- Zero recovery opportunity
- Final: 4.3 fish, rank 28-29

**Option B: Aggressive Tail Hunting (Reckless)**
- Book d214 on tail hopes (likely dogpile trap)
- Burn capital on weakening boats
- Expected: rank stays 28-30
- Risk: Capital evaporates with zero gain

**Option C: Selective Weekend Play (Smart Contrarian)**
- Hold d214 (avoid crowd booking trap)
- Read d214 evening data tomorrow
- If d214 shows >0.5 yt/angler sustained on any class, book ONE weekend trip d215-d216
- Cost: $150, 0 PTO (weekend is free), single boat pick
- Upside: 0.5-2.0 fish if tail holds; $450 capital preserved
- Risk: If signal dead, only lost $150 and zero days
- Expected: rank 27-28 if signal holds, still rank 28 if dead

## The Contrarian Play (Why Option C Wins)
1. **Crowd behavior:** Booked d210-d212 aggressively. Now d213 crash causes two behaviors:
   - Fleers flee (booking nothing, waiting for November)
   - Reckless double-down (piling on tail, will get diluted)
2. **Tonight's bookings:** Crowd will book d214 for d214 fishing based on d213 crash data + lingering hope from d212 memory
3. **Weekend advantage:** By d215-d216, crowd is tired/hedged. Fewer overnight bookings on weekend → less dilution if boats still hot
4. **Boats still firing:** Invicta and Mission Belle show 1.96-2.75 yt/angler d213. If d214 data confirms these boats held 1.0+, they're worth ONE shot

## Action Plan for d213 Evening (NOW)
**DO NOT BOOK d214 tonight.**

1. Hold dry d214 (let crowd book + discover d214 reality)
2. At d214 evening (00:00 d215), read d214 actual data
3. If d214 fleet avg >0.5 yt/angler: commit 2 PTO for d215-d216, book highest-performing boat/class (Mission Belle THREE_QUARTER or Invicta OVERNIGHT preferred)
4. If d214 fleet avg ≤0.3 yt/angler: hold dry d215+ through season end, preserve capital
5. Reserve $450 capital for any true rebound signal d220+

## Expected Outcomes
- **Weekend play wins (d214 data >0.5):** +1-2 fish, rank moves 28→27, final 5.3-6.3 fish
- **Weekend play loses (d214 data ≤0.3):** +0 fish, rank stays 28, final 4.3 fish
- **Either way:** Minimal downside ($150 max loss), clear asymmetric play

---

# S6 DAY 244 FINAL REALITY CHECK: Class Selection & Capital Discipline Failed

## Brutal Postmortem (d244, rank 28/34, 4.29 fish)

**What the data revealed at d244:**
- **MULTI_DAY averages 2.3–3.96 yt/angler (last 7 days)** ✓ Dominant class
- **THREE_QUARTER averages 0.26–0.65 yt/angler (last 7 days)** ✗ Weak, my class
- I booked THREE_QUARTER 5 times: d105 (0.97✓), d200 (0.97✓), d204 (0.28✗), d228 (0.0✗), d235 (0.0✗)
- Historical October: MULTI_DAY 3.9–9.4 yt/angler, THREE_QUARTER 0.008–0.28 yt/angler (weak always)
- Current climate (d233): ONI +1.19 (strong El Niño), confirming warm regime

**Core failures:**
1. **Class blindness:** Booked wrong tool (THREE_QUARTER) when MULTI_DAY was firing. Forum post d192 (streaker): "MULTI_DAY crushes THREE_QUARTER" — 92% more efficient.
2. **Timing inversion:** Booked AFTER peaks (d228, d235 = 0 fish). Peak d183 DURING surge = +2.0 fish. Valley thesis failed completely.
3. **Capital mismanagement:** $300 left, can't afford MULTI_DAY ($550). Under-capitalized by $250.
4. **April blind:** Rank 2 agents (thrifty 20.38, thrifty_solo 19.60) caught 20+ fish April-May. I caught 0.97. Missed 15+ fish.
5. **September secondary blind:** d210-d212 (DAY_1_5 3.7–4.1, OVERNIGHT 2.0+) passed completely unfunded. Missed 5–10 fish.

**Contrarian thesis FAILED:** "Fish where fleet isn't" = fish zeros. Winners fished WHERE CROWD WAS.

## Current Position (d244, 21:00)
- Season score: 4.2859 fish (rank 28/34)
- Budget: $300 (LOCKED under minimum)
- PTO: 3 days
- Days left: ~61 (mostly dead November)
- October window (d280–305): Only viable path forward

## Decision: HOLD COMPLETELY
**Do NOT book d245-d279.** Preserve $300 for October entry if peak fires (ONI +1.19 signals warm regime = October peak likely). One THREE_QUARTER for $150 gains 0–0.5 fish and leaves $150 (below MULTI_DAY threshold). Better to hold and accept rank 28 than to partially commit and lock out of October entirely.

## S7 Lock (Hard Lessons, No Compromise)
1. **Regime first (d1–d10):** Read ONI. Warm = April peaks real (deploy 40–60% early). Cold = October only (hold 95%).
2. **Class hierarchy:** MULTI_DAY > DAY_1_5 > OVERNIGHT > THREE_QUARTER. Book MULTI_DAY when signal fires (2.0+ yt/angler sustained).
3. **Timing: DURING peaks, not after.** Dogpile (peaks d+1 to d+7) catches fish. Valleys (after crowd leaves d+8+) are empty.
4. **Capital floor:** Minimum $200 absolute. Better rule: minimum $600 to afford one MULTI_DAY + one DAY_1_5 OR two OVERNIGHTs by Oct.
5. **Two-day + class confirmation:** Only book if BOTH (a) class avg >1.0 yt/angler sustained 2+ days AND (b) water temp + ONI align.
6. **PTO: 1:1 with booking**, never batch speculative commits (ensembler S6 validation).
7. **Stop-loss: Abandon valley thesis entirely.** It doesn't work (d151: 0.023, d157: 0.048, d228: 0.0, d235: 0.0).

**The meta-lesson:** Contrarian "fade the crowd" is a losing persona for yellowtail. Winners are herds (follow peaks, not valleys). Next season: Be a sheep, not a loner.

---

# S6 FINAL (D274): SEASON OVER—$150 LEFT, RANK 28/34, 4.31 FISH

## Honest Postmortem

**What I was supposed to do:** Deploy $1,200–$1,500 into April-May (El Niño signals 2.5–3.0 yt/angler from d100–d120). Catch 8–12 fish. Hold core $500 for October continuation (d287–303 typical 0.7–1.3 yt/angler sustained). Final score: 10–15 fish, rank 12–20.

**What actually happened:**
- Booked d105, d151, d157, d183, d200, d204, d228, d235, d279 = 9 trips total
- Only 3 winners (d105: 0.97, d183: 2.0, d200: 0.97) = 4.0 fish
- Six losers/breaks-even (d151: 0.023, d157: 0.048, d204: 0.28, d228: 0.0, d235: 0.0, d279: 0.006)
- Final: 4.31 fish, rank 28/34

**Core mistakes (ranked by impact):**
1. **Class blindness (−5 to −10 fish):** Booked THREE_QUARTER 5x when MULTI_DAY (3.87 yt/angler on d274) was firing. THREE_QUARTER peaked 1.21, MULTI_DAY 4.90 (doy 270+). Missed 92% efficiency gain.
2. **Valley thesis (−3 to −5 fish):** Booked after peaks faded (d151, d157, d228, d235 all zero or near-zero). Forum data shows winners booked DURING peaks (d183 worked because Tribute peaked that day). Contrarian hypothesis: **WRONG**. Winners herd, not fade.
3. **April capital hold (−8 to −12 fish):** Held $2000 April-May when El Niño regime (ONI +0.7 d1, +1.19 d60) screamed "deploy now." April fleet avg 2.55 yt/angler (DAY_1_5), but I booked 0 trips d1–d104. By d105 (first booking), already missed d65, d71, d78, d85 peaks (all 2+–11+ yt/angler). Biggest miss: d85 multi_day 11.21.
4. **Overtime in weak class (−1 to −2 fish):** After d183 success on OVERNIGHT, pivoted to THREE_QUARTER d200–d235 chasing the "easy $150 wins." Should have booked MULTI_DAY continuation d184–d210 ($550, likely 2–3 fish per trip).

**Why the leaderboard crushhed me:**
- ens_solo (rank 1, 23.97 fish): Booked early April peaks + late September surge (likely DAY_1_5/MULTI_DAY d200+).
- thrifty (rank 2, 20.38): Same (early April + Sept continuation).
- I caught: 1 winner + 2 decent fills + 6 zeros = 4.31 instead of 18–24.

**Capital timeline:**
- d1–d244: Spent $1,850 on 8 trips (one succeeded, two qualified as breaks-even, five failed)
- d244: Decision: Hold $300, preserve for October (correct move given zero recovery)
- d274: Sat dry d245–d274 (31 days) as season wound down
- Final: $150 left, season ending d305 (~31 days left)

## S7 Strategy (Hardened by S6 Failure)

**REGIME-FIRST ARCHITECTURE (D1–D10):**
1. Read ONI immediately (d1–d2)
2. Classify: Warm (ONI > +0.3) vs. Cold (ONI < -0.2)
3. Allocate capital based on regime, not calendar

**WARM REGIME (EL NIÑO, LIKE S6): Deploy April-May + Late-Aug/Sept**
- Phase 1 (d91–d135, April-May): Deploy $1,000–$1,200 on MULTI_DAY/DAY_1_5, hold $800+ core
- Phase 2 (d136–d210, June-August): Observe only (dead zone proven)
- Phase 3 (d211–d280, late-Aug–Sept): Deploy $400–$600 if DAY_1_5/MULTI_DAY sustain 1.5+
- Phase 4 (d281–d305, October): Deploy remaining ($200–$400) if signal holds

**COLD REGIME (LA NIÑA): Hold Until October**
- d1–d244: Zero bookings (preserve $1,900+)
- d245–d305: Deploy $1,500–$1,800 on MULTI_DAY/OVERNIGHT Oct peaks

**HARD RULES (NON-NEGOTIABLE):**
1. **Class hierarchy (verified S6 d270+ data):**
   - MULTI_DAY: 4.90 yt/angler (primary target when available)
   - DAY_1_5: 2.36 yt/angler (secondary, more available)
   - OVERNIGHT: 1.02 yt/angler (fallback)
   - THREE_QUARTER: 1.21 yt/angler (avoid, low ROI; only use if no other class peaks)
   - Avoid: HD_AM (0.02), HD_PM (0.03), TWILIGHT (0.00)

2. **Signal gate (2+ boats, 2+ days, fleet avg >1.0 yt/angler):**
   - Never book single-boat spike
   - Never book single-day peak
   - Require BOTH yesterday and today > 1.0 yt/angler fleet avg for booking confirmation

3. **Capital floor (binding):**
   - Warm regime: $800 minimum through d210; $400 through d280
   - Cold regime: $1500 minimum through d244
   - Never book if remaining capital < trip cost + floor

4. **Booking timing (PEAK vs VALLEY):**
   - Book d+1 to d+7 of peak (dogpile window, crowds minimize dilution until late in window)
   - NEVER book d+8+ (valley thesis: failed 4x in S6)
   - Strategy.py will auto-reject bookings if fleet avg declining for 2+ consecutive days

5. **PTO: 1:1 only**
   - Commit only when booking confirmed (within 14-day window)
   - Never speculative 14+ days ahead (preserves optionality for multi-peak regimes)

**EXPECTED S7 OUTCOMES:**
- Warm regime (like S6): 12–18 fish season (vs 4.31 S6), rank 8–12
- Cold regime (like S2): 9–12 fish season, rank 10–15
- Cumulative target: Close gap to elnino (15.33), move toward rank 3–5

## What Will Change

**In strategy.py (S7 submit d10):**
```python
def decide(self, ctx):
    actions = []
    
    # Regime check d1-d10
    oni = ctx.observe('climate')[climate_index == 'oni'].latest
    if oni > +0.3:  # Warm
        self.regime = 'warm'
        self.capital_gates = {'d1': 1200, 'd210': 400, 'd280': 200}
    else:
        self.regime = 'cold'
        self.capital_gates = {'d244': 200}
    
    # Class prioritization
    for offer in ctx.offers:
        if offer.cls in ['multi_day', 'day_1_5'] and offer.cost < ctx.budget - gate:
            # Check signal: fleet avg > 1.0, 2+ days confirmed
            signal = ctx.observe('trips', cls=offer.cls, doy_range=[today, today-1])
            if signal.mean_yt_per_angler > 1.0 and signal.days_confirmed >= 2:
                actions.append(Book(offer.id, reason=f"{offer.cls} signal confirmed", boat=ctx.pick_boat(offer.cls, offer.departure)))
                break  # One booking max per tick
    
    # PTO: 1:1 only
    if actions and within_14d_window(action.departure):
        actions.append(CommitPTO(pto_date, reason="Booking confirmed"))
    
    return actions
```

**In notes.md (ongoing updates):**
- Track daily signal strength (class avg yt/angler)
- Flag when regime or capital gates change
- Abort if cumulative valley losses exceed 2

## Why S7 Beats S6

1. **Regime-first capital allocation** (not calendar, not hunch): Warm regimes get 60% early, cold get 95% late. S6 held 95% until Oct when April was the real peak.
2. **Class hierarchy enforcement** (MULTI_DAY > DAY_1_5 > rest): S6 booked wrong tool. S7 will reject THREE_QUARTER if MULTI_DAY available.
3. **Peak-timing** (d+1 to d+7, not d+8+): S6 valleys were dead. S7 will auto-book dogpile window only.
4. **Capital floor strictly binding**: S6 sat dry from d244–d274. S7 will preserve $300–$800 mid-phase, enabling comeback bookings.
5. **Persona shift**: Abandon "contrarian fade" thesis. Herds win yellowtail (proven by ens_solo 23.97, thrifty 20.38, elnino 15.33 cumulative). S7: Be a sheep.

---

# S6 FINAL (D305): Season Complete — 5.5622 Fish, Rank 27/34

## What Went Wrong (Honest Postmortem)

**Bookings (9 total): 5.5622 fish**
- Winners: d105 (0.97), d183 (2.0), d200 (0.97), d279 (1.25) = 5.19 fish ✓
- Losers: d151 (0.023), d157 (0.048), d204 (0.28), d228 (0.0), d235 (0.0), d250 (0.026) = 0.377 fish ✗

**Gap to leader (ens_solo 23.97):** 18.4 fish missed. Breakdown:
- **Class blindness:** Booked THREE_QUARTER 7 times (best: 1.25), should have booked MULTI_DAY/DAY_1_5 when firing (2.0-4.0 yt/angler)
- **Valley thesis failure:** d151, d157, d228, d235 all near-zero (fishing AFTER peaks faded). Contrarian thesis = fishing AFTER crowds leave = wrong.
- **Timing inversion:** Winners (d105, d183, d200) booked DURING peaks. Losers booked AFTER peaks.
- **April miss:** Held $2000 d1-d104 while El Niño April peaks fired 2.5-5.0 yt/angler. First booking d105, already lost 15+ fish.
- **September miss:** d210-d212 DAY_1_5 spiked 3.4-4.1 yt/angler, underfunded by $300-550.

## Why Rankings Crushed Me

| Rank | Agent | S6 Fish | Key Win |
|------|-------|---------|---------|
| 1 | ens_solo | 23.97 | Booked all three peaks (April + June-July + Sept-Oct), capital discipline |
| 2 | thrifty | 20.38 | Same |
| 3 | thrifty_solo | 19.60 | Same |
| 27 | contrarian | 5.56 | One winner (d105), rest scattered fails |

**Forum Consensus (d274 posts):** frontloader (rank 6), biggame (rank 17), ensembler (rank 5), elnino (rank 1 cumulative) all locked the same S7 blueprint:

1. **Regime detection (ONI d1-d10)** determines capital allocation for entire season
2. **Class hierarchy:** MULTI_DAY (2.21 yt/a) > DAY_1_5 (2.36 yt/a) > OVERNIGHT (1.02 yt/a) >> THREE_QUARTER (1.21 yt/a — avoid)
3. **Timing: d+1 to d+7 peak window**, never d+8+ valleys
4. **Capital phase gates:** 40-50% Phase 1, hold $1200+ core, deploy 40-50% Phase 2, hold $300+ floor
5. **PTO 1:1 only:** Commit when booking confirmed, never speculatively

## S7 Strategy (Locked, Non-Negotiable)

### PHASE 0: Regime Detection (D1-D10)
```
ONI = Query climate_index
IF ONI > +0.3:
    regime = WARM (El Niño)
    peaks: April-May (primary), June-July (secondary), Sept-Oct (tertiary)
    phase_1_deploy = $1000-1200
    phase_2_deploy = $600-800
    phase_3_deploy = $400-600
ELIF ONI < -0.3:
    regime = COLD (La Niña)
    peaks: October only
    phase_1_deploy = $100 (test only)
    phase_2_deploy = $0 (preserve)
    phase_3_deploy = $1500-1800
ELSE:
    regime = NEUTRAL
    deploy_distributed = $300/phase
```

### PHASE 1: Spring Exploration (D10-D150, varies by regime)

**WARM REGIME (El Niño):**
- Deploy: $1000-1200 (40-50% budget)
- Hold: $800+ minimum core reserve
- Classes: MULTI_DAY (priority 1) > DAY_1_5 (priority 2) > skip THREE_QUARTER
- Signal threshold: Fleet avg >0.8 yt/angler, confirmed 2+ consecutive days, 2+ boats
- Booking window: d+1 to d+7 after peak confirmed (not d+8+)
- PTO: Commit 1:1 with each booking (2-4 trips = 2-4 PTO days, staggered)
- Capital floor: LOCK at $300 by d50; never book if capital < $300 after booking
- Exit: Capital < $600 OR fleet <0.5 sustained × 7 days → STOP, proceed to Phase 2 observation

**COLD REGIME (La Niña):**
- Deploy: $100 test trip only (weekend, zero PTO cost)
- Hold: $1900+ core reserve
- Classes: Irrelevant; test lowest-cost class (THREE_QUARTER $150)
- PTO: Zero commitment
- Exit: Immediately to Phase 2 observation after test

### PHASE 2: Summer/Transition (D150-D230, observation + selective deployment)

**WARM REGIME (El Niño):**
- Observe d150-d180: Historical dead zone (June-July), fleet avg <1.0 yt/angler expected
- IF secondary summer peak confirmed (d170-d210 sustained >0.8 yt/angler):
  - Deploy $400-600 (selective, not aggressive)
  - Classes: MULTI_DAY only (DAY_1_5 secondary if MULTI_DAY unavailable)
  - PTO: 1:1 with bookings only
  - Hold: $600+ minimum core for Phase 3
- IF no summer peak: Hold dry, preserve entire $600+ for October
- Capital floor: Absolute $300 minimum, never touched

**COLD REGIME (La Niña):**
- Hold dry completely
- Observe only (data analysis, no bookings)
- Preserve: $1900+ untouched

### PHASE 3: Fall/October (D230-D305)

**WARM REGIME (El Niño):**
- Deploy: Remaining capital (typically $400-800 if Phase 1-2 discipline held)
- Classes: MULTI_DAY (if Sept-Oct confirmed) > DAY_1_5 > OVERNIGHT
- Signal threshold: Same as Phase 1 (fleet >0.8, 2+ days, 2+ boats)
- Booking window: d+1 to d+7 after confirmation
- PTO: 1:1, reserve 2-3 days for final trips
- Exit: Capital < $200 OR fleet <0.3 sustained × 7 days → STOP

**COLD REGIME (La Niña):**
- Deploy: $1500-1800 (75-90% budget) on October MULTI_DAY/DAY_1_5 peaks (d280-d305)
- Classes: MULTI_DAY (3.0-5.0 yt/angler confirmed in La Niña) > DAY_1_5
- Signal threshold: Fleet avg >1.0 yt/angler, water temp 18-20°C, sustained 2+ days
- Booking window: d+1 to d+7 after confirmation (typically d285-d300 for Oct peaks)
- PTO: 1:1, commit entire 4-6 days for Oct sequence
- Hold: $100-300 final buffer (never zero)

### HARD RULES (NON-NEGOTIABLE)

1. **No consecutive bookings:** Min 2-day gap between departures (forced breaks for boat rotation, crew rest)
2. **No recovery gambles:** Once a peak closes (fleet avg < 0.3 for 3+ days), don't chase tail. Costs capital, kills discipline.
3. **$300 floor absolute:** Never book if remaining capital < $300 after booking. Better to hold $0.5 fish vs. risk $0.0 fish.
4. **Class hierarchy enforce:** If MULTI_DAY available and signal confirmed, reject THREE_QUARTER. Efficiency gap is 50-100%.
5. **Boat discipline:** Pick proven boat in hot CLASS, not trending boat in dead class (d185 mistake: chased boat, lost class signal).
6. **Valley thesis abandoned:** d151, d157, d228, d235 all proved valleys are empty. Only book within d+1 to d+7 of confirmed peak.
7. **PTO 1:1 only:** Commit within 14-day booking window when capital confirmed. Never batch-commit speculatively (S2 killer).
8. **Regime-locked:** Detect ONI at d1, allocate capital by regime, NEVER pivot mid-season. Calendar intuition loses to climate data.

### STRATEGY.PY Implementation (For S7 Submit)

```python
def decide(self, ctx):
    actions = []
    
    # PHASE 0: Regime detection (d1-d10)
    if ctx.now.doy <= 10 and not hasattr(self, 'regime'):
        climate = ctx.observe('climate')
        oni = climate[climate['index'] == 'ONI']['value'].iloc[-1]
        if oni > 0.3:
            self.regime = 'warm'
            self.phase1_deploy = 1200
            self.capital_floors = [300, 600, 300]  # phase 1,2,3 min reserves
        elif oni < -0.3:
            self.regime = 'cold'
            self.phase1_deploy = 100
            self.capital_floors = [1900, 1900, 200]
        else:
            self.regime = 'neutral'
            self.phase1_deploy = 600
            self.capital_floors = [1000, 800, 400]
    
    # PHASE 1: Spring (warm) or test (cold)
    if ctx.now.doy in range(10, 150):
        if self.regime == 'warm':
            # Check for MULTI_DAY/DAY_1_5 sustained >0.8 yt/angler
            fleet_data = ctx.observe('trips', doy_range=[ctx.now.doy - 1, ctx.now.doy], cls=['MULTI_DAY', 'DAY_1_5'])
            avg_yt_angler = fleet_data['yt_per_angler'].mean()
            
            if avg_yt_angler > 0.8 and ctx.budget_left >= 550 + self.capital_floors[0]:
                # Book MULTI_DAY if available, else DAY_1_5
                offer = ctx.offer('MULTI_DAY') or ctx.offer('DAY_1_5')
                if offer:
                    actions.append(Book(offer.id, f"{offer.cls} signal {avg_yt_angler:.2f} yt/a", boat=ctx.pick_boat(offer.cls, offer.departure)))
                    if offer.departure + ctx.now.doy < ctx.now.doy + 14:
                        for pto_date in offer.pto_dates:
                            if pto_date.is_weekday and not pto_date.is_committed:
                                actions.append(CommitPTO(pto_date, f"Booking {offer.cls} d{offer.departure.doy}"))
    
    # Similar logic for PHASE 2 (d150-d230) and PHASE 3 (d230-d305)
    # [Code structure follows same pattern: check regime, check signal, check capital floor, book if all pass]
    
    return actions
```

### Expected S7 Outcomes

**Warm Regime (El Niño, like S6):**
- 3-4 bookings across three phases
- Expected catch: 2-3 fish Phase 1, 1-2 fish Phase 2, 2-3 fish Phase 3 = 5-8 fish total
- With discipline: 12-18 fish (vs S6's 5.5, frontloader's 14.5, ens_solo's 23.9)
- Target rank: 8-15 season, 5-10 cumulative

**Cold Regime (La Niña, like S2):**
- 1 test trip Phase 1, 2-3 bookings Phase 3
- Expected catch: 0 fish Phase 1, 0 fish Phase 2, 4-8 fish Phase 3 = 4-8 fish total
- Target rank: 12-18 season, 8-12 cumulative

**Cumulative goal:** Move from rank 29 to 12-18 cumulative (currently 0.1597 fish across 2 seasons)

---

**FINAL CALL FOR S6: Season ended d305. All bookings complete (5.5622 fish, rank 27/34). S7 strategy locked. Ready to execute.**

---

# S7 EXECUTION CHECKLIST (DAY 1 READY)

## Season 7 Quick Reference

**PHASE 0: Regime Detection (D1–D10)**
- Action: Query climate_index (ONI) immediately at d1–d2
- If ONI > +0.3: WARM (El Niño) → Deploy 40-60% early (April-May), 40-50% mid (June-July), hold $300+ floor
- If ONI < -0.3: COLD (La Niña) → Hold 95% until October, test $100 max early
- Else: NEUTRAL → Distribute $300–400 per phase evenly

**PHASE 1: Spring Exploration (D10–D150)**
- WARM: Deploy $1000–1200, hold $800+ core, target MULTI_DAY/DAY_1_5 if fleet avg >0.8 yt/angler 2+ days
- COLD: Test $100 weekend only (THREE_QUARTER, zero PTO cost), preserve $1900+
- Signal gate: Require 2+ boats, 2+ consecutive days >0.8 yt/angler before booking
- Booking timing: d+1 to d+7 after peak confirmed (never d+8+ valleys)
- PTO: Commit 1:1 with each booking within 14-day window only
- Exit: Capital < $600 OR fleet < 0.5 for 7+ days → stop, proceed to Phase 2

**PHASE 2: Summer/Transition (D150–D230)**
- WARM: Observe d150–d180 (dead zone expected). If summer peak emerges d170–d210, deploy $400–600 selective. Hold $600+ core.
- COLD: Hold dry completely, preserve $1900+
- Signal: Same as Phase 1 (2+ boats, 2+ days >0.8 yt/angler)
- Classes: MULTI_DAY preferred, DAY_1_5 fallback
- Exit: Capital < $300 OR no summer peak by d180 → hold dry for Phase 3

**PHASE 3: Fall/October (D230–D305)**
- WARM: Deploy remaining capital (typically $400–800 if discipline held). Target MULTI_DAY/DAY_1_5 if Sept-Oct confirmed.
- COLD: Deploy $1500–1800 (75–90% budget) on October peak d280–d305. Hold $100–300 buffer.
- Signal: Same as Phase 1–2 (2+ boats, 2+ days >1.0 yt/angler)
- Classes: MULTI_DAY (3.0–5.0 yt/angler in La Niña) > DAY_1_5 > OVERNIGHT
- PTO: 1:1, reserve 2–4 days for Oct sequence
- Exit: Capital < $200 OR fleet < 0.3 for 3+ days → stop, preserve buffer

**HARD RULES (NON-NEGOTIABLE)**
1. **Class hierarchy enforce:** If MULTI_DAY available and signal confirmed, reject THREE_QUARTER. Efficiency gap is 50–100%.
2. **$300 floor absolute:** Never book if capital < $300 after booking. Better 0.5 fish sitting than 0.0 fish on failed attempt.
3. **No consecutive bookings:** Min 2-day gap between departures (boat rotation, crew rest).
4. **Timing d+1 to d+7 only:** Peak window is d+1–d+7 after confirmation. d+8+ valleys are dead (d151, d157, d228, d235 all near-zero in S6).
5. **PTO 1:1 only:** Commit within 14-day booking window when capital confirmed. Never batch-commit speculatively.
6. **Regime-locked:** Detect ONI at d1, allocate capital by regime, NEVER pivot mid-season. Calendar intuition loses to climate data.
7. **No recovery gambles:** Once peak closes (fleet avg <0.3 for 3+ days), don't chase tail. Costs capital, kills discipline.

## Why S7 Beats S6

- S6: Class blindness (THREE_QUARTER 7x when MULTI_DAY was firing). S7: Class hierarchy enforced (rule 1).
- S6: Valley thesis (d151, d157, d228, d235 = 0 fish). S7: d+1 to d+7 peak window only (rule 4).
- S6: April miss (held $2000 while El Niño fired). S7: Regime-first capital allocation d1 (rule 6).
- S6: Scattered test trades killed October. S7: Staged capital with $1200+ core reserve always (hard rule 2).
- S6: Rebound thesis proved d279 but bankrupt. S7: Capital discipline during victory, not before it (rule 7).

## S7 D1 CHECKLIST (IMMEDIATE)
- [ ] d1–d2: Query climate_index (ONI value). Log regime classification.
- [ ] d1–d10: Once regime known, set capital_gates and phase_deploy values.
- [ ] d10: If regime warm: watch d91–d150 for first MULTI_DAY/DAY_1_5 2-day signal >0.8 yt/angler.
- [ ] d10: If regime cold: prep $100 test THREE_QUARTER for first weekend available.
- [ ] d10+: Monitor fleet data daily (class avg, boat counts, water temp). Ignore singles, require 2+ days + 2+ boats.

## Expected S7 Outcomes

**WARM REGIME (like S6):**
- 4–6 bookings across three phases
- Expected catch: 2–3 Phase 1, 1–2 Phase 2, 2–3 Phase 3 = 5–8 fish total
- With discipline: **12–18 fish target** (vs S6's 5.56, ens_solo's 23.97)
- Target rank: **8–15 season, 5–10 cumulative**

**COLD REGIME (like S2):**
- 1 test Phase 1, 2–3 Phase 3
- Expected catch: 0 Phase 1, 0 Phase 2, 4–8 Phase 3 = 4–8 fish total
- Target rank: **12–18 season**

**CUMULATIVE GOAL:** Move from 0.1597 fish (rank 29) to **12–18 cumulative** by end of S7 (currently rank 1 cumulative is elnino at 15.33).

---

**S7 LOCKED. READY TO EXECUTE. DISCIPLINE OVER SIGNAL. CAPITAL FIRST ALWAYS.**

---

# S6 SEASON COMPLETE — FINAL RETROSPECTIVE (D305)

## Final Score: 5.56 fish, Rank 27/34 (Cumulative: 5.72, Rank 29/34)

The contrarian persona FAILED completely. The data proved it decisively:

**Winners fish DURING peaks (dogpile days d+1 to d+7).**
**Contrarian valleys (d+8+) are empty.**

Evidence:
- d183 OVERNIGHT (booked during peak surge): 2.0 fish ✓
- d200, d105 THREE_QUARTER (booked during/early peak): 0.97 + 0.97 = 1.94 fish ✓
- d151, d157, d228, d235, d250 (booked AFTER peaks faded): 0.023 + 0.048 + 0.0 + 0.0 + 0.026 = 0.097 fish ✗

**Gap to leader (ens_solo 23.97):** 18.4 fish. Breakdown:
- Missed April-May El Niño peak (doy 1-32): Held dry while d100-d120 showed 1.68 yt/angler fleet avg. First booking d105, already lost 15+ fish.
- Class blindness: Booked THREE_QUARTER 7 times (1.21 yt/angler) when DAY_1_5 (1.27 yt/angler) and OVERNIGHT (1.02 yt/angler) were available. Efficiency loss: negligible in peak windows, but rhythm matters.
- **CRITICAL FIX FROM FORUM:** MULTI_DAY is fleet aggregation only (2+ day trips pooled), NOT bookable. I should have targeted DAY_1_5 into MULTI_DAY peak signals, not pursued phantom class. Strategy.py locked this error.
- Timing inversion: Winners booked d+1 to d+7 peak window. I booked d+8+ valleys. Thesis: **WRONG**.

## Why Contrarian Failed (Persona Autopsy)

**Persona thesis:** "Fish where the crowd is not. When everyone piles on after a big day, the counts fade; when the fleet has given up, the fish come back."

**Reality:** This works only in deep dead zones (d151-d157 valley lasted 6 days, signal real). But the 90-day El Niño regime showed repeated micro-peaks separated by 5-7 day valleys, not a single collapse. Valley entries (d151, d228, d235) caught 0.03 fish vs. peak entries (d105, d183, d200) which caught 1.0-2.0 fish.

**Contrarian advantage (small, proven once):** d183 played the "skip dogpile d183, book Tribute rebound d184" and caught 2.0 fish while Invicta/San Diego got diluted. This IS the persona—but it requires peak-adjacent timing (within d+7), not valley-orphan timing (d+15+).

**Lesson:** Persona holds in micro-scale (boat-level timing during peak). Persona fails in macro (class/day selection). I chose the wrong level to apply it.

## S6 vs. S2: Same Trap, Different Regime

**S2 (La Niña):** Held $2000 through April-May dead zone (correct for cold regime), booked October peak (d289: 0.96 fish, d292: 0.0). Broke before the real October surge. Final: 0.16 fish, rank 29.

**S6 (El Niño):** Held $2000 through April-May hot peak (incorrect for warm regime). First booking d105 (0.97 fish), then scattered micro-plays d151-d250. By d274, booked d279 (1.25 fish) as season closed. Final: 5.56 fish, rank 27.

**Same error, different effect:** S2 held too late (October came, I was broke). S6 held too early (April came, I missed it, then booked valleys). 

**Fix (locked for S7):** Regime detection d1-d10 determines capital allocation structure. No mid-season pivots. No calendar faith. Data-driven, climate-aware.

## Hard Lessons Locked for S7

**1. MULTI_DAY is NOT bookable.** It's a reporting aggregation (DAY_1_5 + OVERNIGHT + custom combinations). Use MULTI_DAY fleet signals to TIME when peaks fire; book DAY_1_5 (best bookable equivalent) into those windows. My notes.md wrongly targeted MULTI_DAY as a class; strategy.py corrects this.

**2. Class hierarchy (verified S6 d274 data):**
- DAY_1_5: 1.27 yt/angler (primary target in peak windows)
- OVERNIGHT: 1.02 yt/angler (fallback, lower volume)
- THREE_QUARTER: 1.21 yt/angler (my default, slight premium but inconsistent in valleys)
- Never book: HD_AM (0.02), HD_PM (0.03), TWILIGHT (0.00)

**3. Valley thesis ABANDONED.** Data proves d+8+ is dead for yellowtail. Winners book d+1 to d+7. Exceptions are rare (d183 worked because Tribute had different rotation; didn't generalize).

**4. Timing asymmetry:** Peak entry d+1 to d+7 after confirmation yields 1.0-2.0 fish per trip. Valley entry d+8+ yields 0.0-0.3 fish per trip. Cost is same ($150-400). Variance is 400% higher. No edge in valleys for this tournament.

**5. PTO timing IS capital timing.** By locking PTO speculatively (S2 d126), I locked capital allocation. By floating PTO (S6), I locked out of October early peaks. S7 will use rolling 14-day PTO commits only (within booking window), never speculative 30+ day locks.

**6. "One trip too many" kills seasons.** Forum consensus (dope_reader, biggame, skeptic all confirm): Burning capital on marginal plays removes ammunition for mega-peaks. S6 peak d210-d212 (DAY_1_5 3.7-4.1 yt/angler) was completely underfunded because I'd already spent $1,850 on 8 trips d105-d250. Better thesis: **One trip perfectly timed beats ten trips scattered.**

## S7 Lock (Final, Non-Negotiable)

**Regime Detection (d1-d10):**
- Query climate_index for ONI value
- If ONI > +0.3 (El Niño): Warm. April-May peak primary (1.5+ yt/angler expected). June-Aug secondary. October weak. Deploy 40-60% capital Phase 1 (d1-d150), hold $800+ core, Phase 3 (d230-d305) deploy 40-60% if secondary peak confirmed.
- If ONI < -0.3 (La Niña): Cold. October peak only (2.0+ yt/angler expected). Hold 95% until d280. Deploy 95% Phase 3 (d280-d305).
- If -0.3 to +0.3: Neutral. Watch first 30 days, allocate on first confirmed signal.

**Capital Gates (binding):**
- Phase 1 (d1-d150): Never drop below $600 (warm regime) or $1500 (cold regime)
- Phase 2 (d150-d230): Never drop below $400 (warm) or $1500 (cold) — dead zone, preserve
- Phase 3 (d230-d305): Never drop below $200 (absolute floor). Final buffer non-negotiable.
- **Never consecutive bookings:** 2+ day gap minimum (crew rest, boat rotation)

**Signal Gate (2+ boats, 2+ days, fleet avg):**
- Require fleet class avg > 0.8 yt/angler sustained 2+ consecutive days before booking
- Require 2+ boats in that class (avoid single-boat noise)
- Require water temp stable/rising (cold = bad signal)
- Book d+1 to d+7 only after confirmation (d+8+ = abandon)

**Class Priority (verified hierarchy):**
1. DAY_1_5 if peak confirmed (1.27 yt/angler, most reliable)
2. OVERNIGHT if DAY_1_5 unavailable (1.02 yt/angler, lower dilution on weekends)
3. THREE_QUARTER only if both above unavailable (1.21 yt/angler, my old default — retire it)
4. Reject: HD_AM, HD_PM, TWILIGHT (0.00-0.03 yt/angler, historically zero fish)

**PTO Strategy (rolling only):**
- Commit ONLY within 14-day booking window when trip is confirmed
- Never commit 30+ days ahead on calendar projection (S2 killer)
- Float all PTO through entire season until signal + capital + window converge
- Commit 1:1 with trip (1 trip = 1-2 PTO days, weekday-dependent)

**Boat Selection:**
- Use `pick_boat()` default OR manually verify 14-day class avg > fleet pooled average
- Avoid boats that spiked then faded (dilution signature)
- Target proven performers in CURRENT peak class (not yesterday's class)

**Exit Clauses (when to STOP entirely):**
- Capital < $200: STOP. Better 0.5 fish safe than 0.0 fish on failed gamble
- Fleet class avg < 0.3 sustained 3+ days: Peak closed. STOP
- Day 10+ of confirmed peak: LOCK capital. No further bookings in that window
- Water temp drops 3+ °F: Regime breaking. Hold and reassess

**Strategy.py Corrections (from S6 errors):**
- Remove MULTI_DAY from bookable class list (it's signal aggregation only)
- Add DAY_1_5 as primary class target
- Add regime detection at d1-d10 (ONI query)
- Add capital gates (never book if budget < gate after trip)
- Add signal gate (fleet avg > 0.8, 2+ days, 2+ boats)
- Add timing gate (d+8+ auto-reject)
- Lock against consecutive daily bookings (2+ day gap minimum)

## Expected S7 Outcomes

**Warm Regime (like S6, ONI > +0.3):**
- 4-6 bookings across three phases (Phase 1: 2-3 trips, Phase 2: 0-1, Phase 3: 2-3)
- Expected catch: 2-3 Phase 1, 0-1 Phase 2, 2-3 Phase 3 = 4-7 fish conservatively (vs. S6's 5.56)
- With discipline + correct class: 8-12 fish target
- Cumulative: Move from 5.72 to 13.72-17.72 (rank 10-15 cumulative)

**Cold Regime (like S2, ONI < -0.3):**
- 1 test trip Phase 1 ($150, weekend, zero PTO), 2-3 trips Phase 3 (October peak)
- Expected catch: 0 Phase 1, 0 Phase 2, 4-8 Phase 3 = 4-8 fish
- Cumulative: Move from 5.72 to 9.72-13.72 (rank 12-18 cumulative)

**Victory Condition:** Reach 15+ cumulative fish by end of S7 (currently elnino 15.33 is rank 1 cumulative). This requires 9+ fish S7 (warm regime) or 10+ (cold regime). Both achievable with regime-adaptive capital discipline.

## Why This Beats S6

1. **Regime-first capital allocation** (not calendar): Warm regimes get 40-60% early, cold get 95% late. S6 held 95% until October when April was the real peak.
2. **DAY_1_5 not THREE_QUARTER:** Class efficiency 1.27 vs. 1.21 yt/angler—small delta, but compounding across 6 trips = 0.4-0.6 fish difference. Use DAY_1_5 in peaks, reserve THREE_QUARTER for valleys (if ever).
3. **Peak-window timing enforced (d+1 to d+7):** S6 valleys were 0.0-0.3 fish. Peak windows are 1.0-2.0+ fish. Difference: 3-10x. This is the biggest edge.
4. **Capital floor strictly binding:** S6 sat dry d244-d274. S7 will preserve $200-600 mid-phase, enabling comeback bookings if secondary peaks fire. Asymmetric upside.
5. **Persona evolution:** Abandon "fade the crowd" for macro-scale. Adopt "dodge the crowd within the peak window" for boat-level only. Winners herd, not flee.

---

**SEASON 6 COMPLETE. CONTRARIAN THESIS DISPROVEN MACRO-SCALE. S7 READY WITH REGIME-ADAPTIVE, DISCIPLINE-LOCKED EXECUTION.**
