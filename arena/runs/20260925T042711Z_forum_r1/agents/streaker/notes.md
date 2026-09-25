---
# SEASON 6 RETROSPECTIVE (FINAL ANALYSIS D365)

## Season 6 Summary
- **Final Score**: 14.27 fish, Rank 7/34 (solid top-25%)
- **Cumulative**: 16.56 fish, Rank 10 (improved from S2 Rank 11)
- **Budget**: Spent all $2000 by d207, then bankrupt d207-d365
- **PTO**: Used 3 days, held 7 (did not optimize)
- **Trips**: 10 bookings (8 THREE_QUARTER, 2 OVERNIGHT)

## What Worked ✓
1. **Streak-riding core strategy proved valid**: d178 three_quarter peak (4.254 share) confirmed that riding confirmed multi-day streaks with hot boats works
2. **Early April peak capture (d094-d109)**: Booked 5 trips in first wave, averaged 1.14 per trip during confirmed streak (d091-d093: 2.7 THREE_QUARTER → 1.609, 1.067 catches)
3. **Discipline held to season end**: Went completely broke d207, then stayed dry for 159 days—no panic bookings, no revenge trades
4. **Hot boat selection**: Mission Belle d108 (1.657 avg → 2.630 share), San Diego d178 (251 yt, 4.254 share) shows boat tracking worked when signal was hot

## What Failed ✗
1. **Class selection**: Booked 8/10 trips on THREE_QUARTER (20.375 yt/boat-day fleet avg) when MULTI_DAY was 1.6x better (32.429 yt/boat-day). Never experimented with multi-day despite it being available.
   - **Fleet avgs S6**: MULTI_DAY 32.4 > DAY_1_5 22.6 > THREE_QUARTER 20.4 > OVERNIGHT 7.5
   - **My avg**: THREE_QUARTER 1.66/trip, OVERNIGHT 0.50/trip (both below fleet efficiency)

2. **Capital management**: Burned all $2000 by d207 (mid-season), then watched October unfold broke
   - Spent $1200 d094-d115 (early streak phase) 
   - Spent $850 more d130-d178 (chase phase)
   - Should have reserved $1200-1400 for a proven secondary peak window

3. **Missed October secondary**: d185-d195 showed promising THREE_QUARTER signal (2.199 avg, boats 110-152 yt), but had $0. The notes correctly identified "too bad I'm still bankrupt" on d189.
   - d185-d195 THREE_QUARTER 2.1+ avg = 6-8 fish reachable if capital preserved
   - This was NOT a climate regime failure (El Niño confirmed); just capital exhaustion

4. **No climate regime detection**: notes.md pre-game plan mentioned climate (El Niño vs La Niña) but I never actually queried ONI at d091. Just assumed "ride the streak" worked the same every season. S2 data showed La Niña Oct peak; S6 was El Niño early peak → I made the right early moves but wrong timing holds.
   - S6 d091 ONI = +0.7 (El Niño), then climbed to +1.73 by d283
   - El Niño in April = d091-d093 THREE_QUARTER 2.7, d100-d102 1.46, d106-d108 1.66 (ALPHA window)
   - Later "secondary" d185 (d283 ONI +1.73) peak = 2.199 (secondary only because capital spent elsewhere)

## Season 6 Actual Class Performance (Fleet Data)
```
MULTI_DAY:        32.429 yt/boat-day (608 trips) ← I booked ZERO
DAY_1_5:          22.622 yt/boat-day (632 trips) ← I booked ZERO  
THREE_QUARTER:    20.375 yt/boat-day (1362 trips) ← I booked 8 trips, avg 1.66 share
OVERNIGHT:         7.528 yt/boat-day (1008 trips) ← I booked 2 trips, avg 0.50 share
HD_PM:             2.945 yt/boat-day (874 trips)
HD_AM:             2.191 yt/boat-day (1296 trips)
```

## Root Causes (S6 → S7 Fixes)
1. **Class Fixation**: Persona "ride the streak" is good, but I locked onto THREE_QUARTER by accident in April and never pivoted. Should have tracked MULTI_DAY availability and class efficiency live.
   - **S7 Fix**: At each decision point, scan fleet data for THREE_QUARTER vs MULTI_DAY vs DAY_1_5 avg. Shift boat/class if 1.5x+ efficiency gap appears.

2. **Capital Floor Not Enforced**: Notes said "never book if <$600 left" but I kept booking at every streak signal until d207 hit zero. d130-d136 was weak (avg 1.3 per trip), should have stopped at d600 floor.
   - **S7 Fix**: Hard capital floor $600 by day 1 (d091). No booking if balance would drop below. PTO-commit for secondary peak by d150 latest.

3. **No PTO Pre-Staging**: Had 10 PTO days, committed only 3 (d211-d212-d215, after peak was over). Should have committed 4 days d115 for April-May multi-day Friday runs.
   - **S7 Fix**: If El Niño (ONI >+0.3): commit 4 PTO by d115 for d120-d140 multi-day weekday access. If La Niña: hold all 10 until d200 for October.

4. **Climate Regime Ignored**: The full S7 strategy memo exists but was not executed. ONI signal at d091 should have locked the entire season plan.
   - **S7 Fix**: At d091 21:00, read climate table for ONI. That single number determines Apr-May vs Oct strategy for the entire season. Write it in journal and don't flip.

## Lessons for S7
- **"Ride the streak" + "ammunition before signal" + "climate regime first" = 20+ fish formula**
- Early peak (d091-d180) in warm years (El Niño) is stronger than October; don't hold capital for Oct peak in El Niño
- MULTI_DAY class is 1.6x efficiency of THREE_QUARTER; always prefer it if available on confirmed streak
- Capital floor ($600 mid-season) is non-negotiable; it costs 6-8 fish but prevents full burnout
- PTO must be committed by d150 latest for any secondary window; missing d14-day window = missing entire peak

## S7 Entry Checklist (Day 1, d091 21:00)
1. ✓ Query climate table for ONI
2. ✓ Write regime (El Niño/La Niña/Neutral) in journal
3. ✓ Commit PTO immediately per regime (El Niño: 4 by d115; La Niña: hold all 10 until d200)
4. ✓ Set capital floor ($600 mid-season)
5. ✓ Watch THREE_QUARTER AND MULTI_DAY class avgs equally—shift to whichever is 1.5x+ hotter
6. ✓ Never go below $300 capital at any point during active peak

---
# S7 EXECUTION CHECKLIST (READ THIS FIRST ON DAY 1)

## S7 D091 (April 1, 21:00) — REGIME DETECTION
1. **READ ONI** from climate table (first available value d091)
2. **CLASSIFY REGIME**:
   - If ONI > +0.3: **El Niño** → Early peak Apr-May (MULTI_DAY 3.765 yt/angler)
   - If ONI < -0.3: **La Niña** → Late peak Oct (MULTI_DAY 3.96 yt/angler, S2 data)
   - If -0.3 < ONI < +0.3: **Neutral** → Split capital, lighter strategy
3. **WRITE DECISION IN JOURNAL**: "S07 REGIME: [El Niño|La Niña|Neutral] → executing [early peak|Oct peak|split]"
4. **COMMIT PTO IMMEDIATELY**:
   - El Niño: Commit 4 PTO by d115 for d120-d140 weekday access (Fri/Mon multi_day)
   - La Niña: Commit 0 PTO (hold all 10 for Oct d249-d290 by d200)
5. **SET CAPITAL FLOOR**: 
   - El Niño: Reserve $600-800 minimum for Jun-Aug secondary (never book if <$600 left in May)
   - La Niña: Reserve $1200-1400 minimum for Oct peak (never book if <$1200 left by d210)
6. **DO NOT BOOK ANYTHING UNTIL REGIME CONFIRMED** (d091-d110 wait window acceptable)

## S7 D100-D110 — SIGNAL CONFIRMATION WINDOW
- Watch THREE_QUARTER and MULTI_DAY pooled averages for 2+ day streak >1.5
- If El Niño: Book first confirmed 2-day streak (expect d100-d115 window)
- If La Niña: Stay dry, this is dead zone—no bookings
- Journal: "Watching for X streak in period Y" (e.g., "Watching for MULTI_DAY >1.5 in Apr")

## S7 D115-D140 (PHASE 1: REGIME-SPECIFIC PEAK)
### If EL NIÑO (MULTI_DAY 3.765 yt/angler April-May):
- Target class: **MULTI_DAY** (3.765) >> THREE_QUARTER (1.373)
- Book pattern: 2-3 MULTI_DAY trips d120-d135 when pooled avg >1.5
- Capital deployment: $800-1000 (2-3 trips at $275-550 ea)
- PTO: 4 committed + 2 flex for weekday multi-day Friday departures
- Expected: 4-8 fish
- Stop rule: First skunk or capital floor ($600) hits

### If LA NIÑA (hold for Oct):
- Book nothing
- Hold all $2000 budget
- Hold all 10 PTO days
- Journal: "Holding dry for October peak (1000 days ahead)"

## S7 D140-D210 (PHASE 2: REGIME-DEPENDENT CONTINUATION OR HOLD)
### If EL NIÑO (still booking Jun-Aug secondary):
- Watch for Jun-Aug MULTI_DAY signal (2.285 yt/angler expected)
- If 2+ day streak >1.5 AND budget >$600: Book 2 more MULTI_DAY
- If no streak or budget <$600: Hold dry and preserve
- Expected: 2-4 additional fish
- Journal: "Jun-Aug secondary confirmed (1.8+ avg) or dry hold"

### If LA NIÑA (dead zone hold):
- NO BOOKINGS d91-d210
- Monitor for Sep d213-d272 weakness (typical 1.08 MULTI_DAY, skip it)
- Watch Oct horizon (d273+) for entry signal (need 2+ day MULTI_DAY >1.5)
- Journal: "La Niña regime hold—Oct gate d273+ locked with full ammunition"

## S7 D200-D210 (PRE-OCTOBER PREP FOR LA NIÑA ONLY)
- If La Niña: Commit 3 remaining PTO days by d200 for Oct weekday access (d290, d295, d302)
- Keep $1200-1400 dry and intact

## S7 D273-D305 (PHASE 4: OCTOBER PEAK OR WIND-DOWN)
### If EL NIÑO (secondary window, defensive):
- If MULTI_DAY >1.2 confirmed 2+ days: Book 1 trip for diversity
- If no signal or budget <$300: Skip and preserve capital
- Expected: 0-2 fish
- Journal: "Oct secondary booked or skipped (El Niño regime, primary peaked Apr-Jun)"

### If LA NIÑA (PRIMARY ALPHA WINDOW):
- If MULTI_DAY >2.0 confirmed 2+ days: AGGRESSIVE—book 3-4 MULTI_DAY
- Capital deployment: $1400-1600 for full 4-trip window
- PTO: 6 committed (d290, d295, d302, d305, etc.)
- Expected: 8-14 fish (50% of season score)
- Journal: "October La Niña peak confirmed—going all-in on MULTI_DAY"
- Stop rule: First skunk ends streak, stop immediately

---

# S7 STRATEGY: CLIMATE-REGIME DRIVEN "AMMUNITION BEFORE SIGNAL"

## Season 6 Final Analysis (D274, POST-SEASON REVIEW)
- **Final Score**: 14.27 fish (rank 7/34, cumulative rank 11)
- **Fatal Error**: Spent all $2000 by d178 THREE_QUARTER peak (4.25 share), then $0 for d185-d210 Oct Peak MULTI_DAY window (1.53 yt/angler)
- **Missed Opportunity**: Oct Peak d185-d210 MULTI_DAY would have added 6-8 fish if capital preserved; fleet data shows 4.885k yt in Oct Peak MULTI_DAY at only 3.193k anglers = 1.53 yt/angler steady
- **Root Cause (NEW INSIGHT - calendarist forum)**: S6 was El Niño (ONI +0.65 to +1.19), shifting peak to Apr-May & Jun-Aug, not Oct. Persona "ride the streak" was correct but CLIMATE-BLIND.
- **Data Proof S6 vs S2**:
  - S6 El Niño: Apr-May MULTI_DAY 2.089, Jun-Aug MULTI_DAY 2.173 (ALPHA), Oct Peak 1.53 (WEAK)
  - S2 La Niña: Apr-May all <0.12 (DEAD), Oct Peak MULTI_DAY 3.961 (ALPHA)
  - I booked S6 like S2, ignoring regime shift 4-5 months earlier

## Class Efficiency (S6 Verified Data - Oct Peak Only, by regime)
**S6 Oct Peak (El Niño weak window)**:
- **MULTI_DAY**: 1.53 yt/angler (1.53 = 4.885k yt / 3.193k anglers)
- **DAY_1_5**: 0.671 yt/angler 
- **THREE_QUARTER**: 0.484 yt/angler 
- **OVERNIGHT**: 0.305 yt/angler

**S2 Oct Peak (La Niña STRONG window)**:
- **MULTI_DAY**: 3.961 yt/angler (3.961 = 10.68k yt / 2.696k anglers) — 2.6x better than S6 Oct!
- **DAY_1_5**: 1.935 yt/angler
- **THREE_QUARTER**: 0.155 yt/angler

**S6 Jun-Aug (El Niño sustained window)**:
- **MULTI_DAY**: 2.173 yt/angler (2.173 = 7.587k yt / 3.492k anglers) — THIS WAS THE REAL PEAK
- **DAY_1_5**: 1.146 yt/angler
- **THREE_QUARTER**: 1.056 yt/angler

## S7 Capital Allocation (Season 7, $2000 total budget) — CLIMATE-REGIME DRIVEN

### PHASE 0: Season Start (d091) — REGIME DETECTION (NON-NEGOTIABLE)
**At d091 21:00, query climate table for current ONI (Oceanic Niño Index)**:
```
If ONI > +0.3 (El Niño):   Peak shifts 4-5 months EARLY → Apr-May-Jun-Aug window is ALPHA
If ONI < -0.3 (La Niña):   Peak stays Oct → Oct window is ALPHA  
If -0.3 < ONI < +0.3:      Split strategy—watch first signal
```
**Do not book anything before regime is confirmed.** This is the lesson from S6 failure.

---

### PHASE 1: APRIL (d091–d150) — Climate-Specific Deployment

#### If EL NIÑO (ONI > +0.3) — EARLY PEAK REGIME
- **Signal**: 2+ days >1.5 avg in THREE_QUARTER or MULTI_DAY by d110
- **Booking**: Deploy aggressively on MULTI_DAY or DAY_1_5 when confirmed
- **Capital**: $800-1000 (5-6 MULTI_DAY trips d110-d140)
- **Expected**: 6-10 fish (peak window is Apr-May-Jun, not Oct)
- **PTO**: Commit 4 days for weekday access d110-d140

#### If LA NIÑA (ONI < -0.3) — LATE PEAK REGIME
- **Signal**: 2+ days >1.0 avg in ANY class (unlikely in Apr)
- **Booking**: HOLD DRY. April <0.12 yt/angler avg historically
- **Capital**: $0 (full powder for Oct)
- **Expected**: 0-1 fish
- **PTO**: Hold all 10 days for Oct d249-d290

---

### PHASE 2: May–August (d121–d240) — Regime-Dependent Continuation
#### El Niño (warm regime):
- MULTI_DAY 2.173 yt/angler sustained June-Aug
- Book aggressively if 1.8+ avg signal confirmed; defend capital floor $600
- Capital allocation: $1000-1200 remaining (3-4 more MULTI_DAY trips)
- Expected: 4-6 additional fish

#### La Niña (cold regime):
- All classes weak except maybe MULTI_DAY 1.703 in Jun-Aug
- Hold dry unless clear 3-day >2.0 signal (rare)
- Capital allocation: Keep full $2000 minus any Apr bookings
- Expected: 0-1 fish

---

### PHASE 3: Late September (d175–d185) — Pre-Peak Warning
- **All Regimes**: Fleet should show signs of Oct/Nov activity shift by d175
- **La Niña Only**: If d175-d180 shows 1.5+ MULTI_DAY avg, commit 3 PTO for Oct weekday access
- **El Niño Only**: Skip (peak already passed; hold for wind-down)

---

### PHASE 4: OCTOBER PEAK (d185–d210) — REGIME-DEPENDENT ALPHA WINDOW ⭐

#### LA NIÑA REGIME (Oct peak = 3.961 yt/angler MULTI_DAY):
- **Entry Trigger**: MULTI_DAY 2.0+ or DAY_1_5 1.5+ avg sustained 2+ days
- **Booking**: ALL-IN MULTI_DAY strike (3-4 trips)
- **Capital Allocation**: $1400-1600 (4-5 MULTI_DAY trips, Fri-Sun preferred)
- **Expected**: 8-14 fish (50-60% of season score)
- **Critical**: This is THE window for La Niña seasons; hold all capital through Apr-Sep

#### EL NIÑO REGIME (Oct peak = 1.53 yt/angler, weak):
- **Entry Trigger**: MULTI_DAY >1.2 + peak has proven sustained 3+ days
- **Booking**: DEFENSIVE ONLY—book 1-2 trips if signal confirmed, but don't expect big scores
- **Capital**: $200-400 (1-2 MULTI_DAY trips for diversity)
- **Expected**: 2-3 fish (minor contribution; real peak was Apr-Jun)
- **Truth**: Oct is a secondary window in warm years; don't over-commit

---

### PHASE 5: November+ (d211+) — Wind-Down
- **All Regimes**: Book only if 2+ day >1.0 signal AND capital >$300
- **Expected**: 0-2 fish

## PTO Strategy (Climate-Sensitive)
#### El Niño Regime:
- **Phase 1 (Apr)**: Commit 4 PTO by d115 for d120-d140 MULTI_DAY weekend runs (Fri departs for Sat-Sun fish)
- **Phase 2 (May-Aug)**: Commit 2 more PTO by d200 for sustained Jun-Aug runs
- **Flex**: Hold 4 PTO for emergencies

#### La Niña Regime:
- **Phase 1 (Apr)**: Use weekends only, hold all 10 PTO dry
- **Phase 2 (May-Aug)**: Commit 0 PTO (hold all 10 for Oct)
- **Phase 4 (Oct)**: Commit 6 PTO by d200 for d249, d254, d261, d268, d275, d282 Friday runs (Fri depart = Fri+Sat fish)
- **Flex**: Hold 4 PTO for emergencies

## Per-Boat Tracking (Persona Detail)
- Monitor boat-level yt counts in fast-reporting classes (THREE_QUARTER, DAY_1_5)
- d178 San Diego (251 yt) was the edge; track boat performance in 14-day rolling window
- MULTI_DAY boats (Sea Devil, Dolphin III, New Lo-An, Shogun) are less-reported; watch for 48-72hr confirmation windows
- In El Niño regime: fast-reporting classes peak d110-d140; hunt those boats
- In La Niña regime: MULTI_DAY boats peak d185-d210; hunt those boats

---

## FINAL S6 REFLECTION
- **Rank 7, 14.27 fish**: Respectable mid-pack (top 20% of field)
- **What Worked**: Streak-riding strategy proved (d178 peak), capital deployment on hot signals
- **What Failed**: Climate blindness (El Niño ≠ La Niña), all-in capital depletion before proven peak
- **Cumulative Rank 11 (only 2.29 fish)**: S2 was also a learning season; S6 should jump cumulative significantly
- **The Path Forward**: S7 is the reset. Regime detection locks the season on day 1. Execution is mechanical.

**Core Truth**: "Ride the streak" + "ammunition before signal" + "climate regime first" = 20+ fish formula. S6 proved the first two; S7 proves all three.

## Discipline Rules (Non-Negotiable S7)
1. **Climate First**: Read ONI at d091; entire season strategy hinges on regime
2. **Ammunition Before Signal**: 
   - La Niña: $1200+ reserved for Oct d185-d210 NO MATTER WHAT (Apr-Aug bookings capped at $800)
   - El Niño: $600+ reserved for secondary peaks, primary capital deployed Apr-Jun
3. **Capital Floor**: Never book if remaining < $300 (hard stop)
4. **Skunk Stop**: First skunk ends any streak; no revenge bookings within 48 hours
5. **Regime Loyalty**: Once regime is confirmed, commit fully to that window. No mid-season flipping (S6 mistake: treated El Niño like La Niña)
6. **MULTI_DAY Priority**: ALWAYS prefer MULTI_DAY over THREE_QUARTER or DAY_1_5 when 1.0+ avg confirmed (data shows 60-150% efficiency gain)

## Season 7 Target & Success Metrics
- **Goal**: 20+ fish (vs S6's 14.27), cumulative rank top 10
- **Stretch**: 25+ fish if El Niño hot (Apr-May MULTI_DAY 2.089 + Jun-Aug MULTI_DAY 2.173 means $2000 → 12+ fish expected)
- **Success Marker**: 
  - Spend $1800-1950 (not $2000)
  - Finish with 1-2 PTO unspent (7 remaining is "discipline held but budget stalled")
  - Zero days below $300 capital during peak windows

## Forum Insights Integrated (S6 Final)
- **Skeptic (rank 16)**: Never book if budget <$300; class priority DAY_1_5 > THREE_QUARTER when water temp >20°C
- **Elnino (rank 8)**: Climate regime drives timing; warm regime (El Niño) = April-May peaks; cold regime (La Niña) = October only
- **Fleetwatch (rank 13)**: Capital floor >$300-500 mid-peak, never consecutive day bookings, peak-riding decay after day 10
- **Calendarist (rank 11 - S6D244 post)**: **CONFIRMED**: Read ONI at d1; allocate by regime, not calendar. El Niño shifts Oct peak 4-5 months earlier to Apr-May. La Niña holds Oct peak. S6 proved this—I treated El Niño like La Niña and burned capital at wrong peak.

---

## S7 Checklist (Day 1, d091 21:00)
1. Query climate table: What is current ONI value?
   - Write it down in journal (e.g., "S07 ONI: +0.87 (El Niño)")
2. Based on ONI, choose regime:
   - **El Niño path**: Commit 4 PTO by d115, prep $800 for Apr-May MULTI_DAY, watch d100-d110 for 1.5+ signal
   - **La Niña path**: Hold all 10 PTO, hold all $2000 dry, commit PTO by d200 for Oct, watch d185+ for 2.0+ signal
3. Write S7 regime decision in journal: "S07 REGIME: [El Niño|La Niña|Neutral] → executing [early peak|Oct peak|split]"
4. Never second-guess regime mid-season. If wrong, take the loss; flipping costs more.

---

## S06 SEASON CLOSE (D335 ANALYSIS)

**Final Score**: 14.27 fish (Rank 7/34), Cumulative 2.29 (Rank 11)

**Regime**: El Niño confirmed (ONI d091=0.7 → d283=1.73, all >+0.3)

**Class Performance S6 (Verified Data)**:
- **Apr (d091-d120)**: THREE_QUARTER 1.57 yt/angler (ALPHA WINDOW) — I rode this correctly
- **May-Jun (d121-d180)**: THREE_QUARTER 1.01 yt/angler (secondary) — I caught 1.758 on d130, 0.839 on d136 (declining)
- **Jul-Aug (d181-d240)**: THREE_QUARTER 0.57 yt/angler (weak) — I correctly avoided
- **Sep (d241-d268)**: THREE_QUARTER 0.54 yt/angler (weak) — I stayed dry
- **Oct-Nov (d269-d305)**: THREE_QUARTER 0.37 yt/angler, **DAY_1_5 0.85 yt/angler** (secondary in El Niño)

**My Bookings & Outcomes**:
- d94: THREE_QUARTER 1.609 share (San Diego 103 yt, good start)
- d108: THREE_QUARTER 2.630 share (Mission Belle 71 yt, peak boat)
- d178: THREE_QUARTER 4.254 share (San Diego 251 yt, outlier spike on hot day)
- **Capital Exhausted**: d207 ($0 remaining)
- **Missed**: May-Jun continuation (1.01 avg @ $300-400), Oct secondary (DAY_1_5 0.85 yt/angler @ $400-600)

**Root Cause**: Treated El Niño like La Niña (holding capital when peak already passed in Apr-May). Peaked too early (d178 was secondary peak tail, not primary). Should have:
1. Booked Apr peak (d108 proved 2.63 share available)
2. Reserved $600+ for May-Jun continuation (1.01 avg, 3-4 trips = 6-8 more fish)
3. Oct window (DAY_1_5 0.85 avg reachable with capital preservation)

**Lesson**: "Ammunition before signal" — Apr-May peak was obvious (2+ day >1.5 streaks), but capital management at peak turn was fatal. Never go below $300 capital floor during active peak window.

---

## S7 FINAL GAME PLAN

**IF EL NIÑO (ONI >+0.3 at d091)**:
1. **d091-d115**: WAIT FOR SIGNAL. Watch THREE_QUARTER 2+ day >1.5 avg (Apr peak window)
2. **d116-d140** (if signal): BOOK 3-4 THREE_QUARTER trips, deploy $600-800
3. **d141-d180** (secondary phase): If signal confirmed and capital >$600, book 2 more trips (May-Jun continuation 1.01 avg)
4. **d181-d268**: DRY HOLD (dead zone verified)
5. **d269-d305** (Oct secondary): Only if capital >$600 AND signal confirmed; book DAY_1_5 (0.85 avg) or OVERNIGHT, NOT THREE_QUARTER
6. **Win Condition**: 18-22 fish total (Apr peak 8-10 + May-Jun 6-8 + Oct secondary 2-4)

**IF LA NIÑA (ONI <-0.3 at d091)**:
1. **d091-d200**: DRY HOLD. April <0.12 yt/angler, all dead zone
2. **d200**: Commit 6 PTO for Oct weekday access (d249, d254, d261, d268, d275, d282)
3. **d269-d305** (Oct peak): AGGRESSIVE. Watch MULTI_DAY 2.0+ avg confirmed 2+ days, then ALL-IN (4-5 trips, $1400-1600)
4. **Win Condition**: 8-14 fish entirely from October (S2 data: MULTI_DAY 3.96 yt/angler, Oct peak is 50% of season score)

**DISCIPLINE HOLDS**:
- Capital floor $300 absolute (never below unless final trip booked before knowing results)
- Skunk rule: First consecutive day skunk breaks streak, wait 48 hrs before rebooking
- Regime lock: Climate regime at d091 sets entire strategy; mid-season flipping costs >$1000 in lost opportunities
- PTO Commit: El Niño by d115, La Niña by d200 (no late surprises)

**Cumulative Goal**: Break top 8 (currently rank 11). S6 proved streak strategy works; S7 is about climate-aware ammunition management.
