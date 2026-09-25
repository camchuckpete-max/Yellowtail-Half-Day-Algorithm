# S6 SEASON-END RETROSPECTIVE (d335, 21:00 PLANNING TURN)

## FINAL SCORE & CUMULATIVE IMPACT
- **S6 Season Score:** 13.7521 fish (10th place out of 30+)
- **Cumulative Score:** 13.9761 (13th place overall, up from 28th)
- **Budget Remaining:** $20 (broke at d185 due to myth-chasing)
- **PTO Remaining:** 5 uncommitted days
- **Key Metric:** Improved cumulative rank by 15 places from S2, but left 8-12 fish on table due to one unforced error

## WHAT WORKED (✅ DISCIPLINE VICTORIES)
1. **Regime Detection (d91 Climate Lock):** ONI +0.7 → El Niño → April-May peaks = PRIMARY. Correctly identified and booked early.
2. **Peak Identification (d105-d111):** Rode 7 consecutive trips on hot THREE_QUARTER signal (1.5+ yt/angler sustained). Caught 7.52 fish across peak + tail.
3. **Capital Discipline Phase 2 (d113-d182):** Held dry for 70 consecutive days despite 8-day sustained peak d175-d182 (correctly declined due to $100 underfunding + weak PTO alignment).
4. **Avoided TWILIGHT Trap:** Never booked TWILIGHT/HD_PM/HD_AM weak classes despite temptation. Fleet signal 0.0-0.164 yt/angler = noise.
5. **Correct PTO Timing (d105-d112):** Locked 14-day PTO window early (d105-d112 committed by d91), aligned perfectly with spring peak.

## WHAT FAILED (❌ DISCIPLINE BREAKS)
1. **d185 Single-Boat Myth Chase (CRITICAL FAILURE):** New Seaforth d184 showed 0.055 HD_PM, sparked booking d185 HD_PM: 0 yt caught, $80 burned. HD_PM fleet average d185 = 0.0 yt/angler (pure noise). This one error cascaded into capital break.
2. **d112-d120 Tail Missed (STRATEGIC BLINDNESS):** Spring peak continued 2.0-4.0 yt/angler for 9 days (higher than peak 1 start), but I declared victory at d111 and held dry. Opportunity: ~19 fish.
3. **d210-d212 Mega-Peak Watched From Broke ($20):** Season's actual best fishing (DAY_1_5 3.67-4.11 yt/angler) was inaccessible. Cost of d185 error: $80 = ~3-4 fish opportunity (could have booked d210 at $550).
4. **Over-Reacted to Noise, Under-Reacted to Peaks:** The persona trap. Single HD_PM boat on single day = trigger to book. But class-level peak sustained 2-8 days = discipline hold. Backwards logic.

## ROOT CAUSE: CONFLATED SIGNAL WITH NOISE
- **Noise (d185):** One boat, one day, does NOT equal class signal. New Seaforth d184 catch = 2 yt ÷ unclear angler count = 0.055 yt/angler. BUT: HD_PM fleet d185 = 0.0 yt/angler average. One boat ≠ fleet signal.
- **True Signal (d112-d120, d210-d212):** Class fleet average ≥2.0+ yt/angler sustained 3+ days = bookable peak. Should have over-committed capital here, not hoarded.

## S7 PROTOCOL LOCKED: THREE-GATE RULE + REGIME + CAPITAL DISCIPLINE

### Phase 0 (d1-d9): Regime Detection
**Query ONI immediately.** Regime determines capital allocation:
- **Warm (ONI > +0.3):** El Niño → April-May peaks PRIMARY, October secondary. Allocate $800 Phase 1, $1200 Phase 3.
- **Cold (ONI < -0.3):** La Niña → October peak ONLY. Allocate $0 Phase 1, $1600 Phase 3.
- **Neutral (-0.3 to +0.3):** Watch fleet d1-d30, adaptive allocation.

### Three-Gate Rule (EVERY BOOKING DECISION d91+)
**ALL THREE gates required; NONE are optional:**
1. **Signal Gate:** CLASS fleet average ≥0.2 yt/angler (NOT single boat). For DAY_1_5/OVERNIGHT/MULTI_DAY, threshold ≥0.5 yt/angler.
2. **Water Gate:** Scripps Pier ≥18°C sustained (hourly avg, not spike).
3. **Capital Gate:** Budget remaining ≥ trip_cost + phase_buffer. Phase 1 ($800 min), Phase 2 ($0 = hold dry), Phase 3 ($300 min). NEVER go below $300 mid-peak.

**IF all three PASS:** Commit PTO 3-5 days only, book DAY_1_5 > OVERNIGHT > MULTI_DAY priority.
**IF any FAIL:** HOLD DRY. Log which gate failed.

### Capital Discipline (NON-NEGOTIABLE)
- **Absolute Floor:** Never book if remaining budget < $300. Full stop.
- **Mid-Peak Hold:** Day 7-10 of sustained peak (3+ days ≥1.5 yt/angler), reserve $500+ or exit peak.
- **No Recovery Gambles:** If capital breaks $300, HOLD DRY. No "one trip to get even" trades.
- **Peak Decay (Day 11+ Rule):** After day 10 of sustained signal ≥0.2, lock remaining capital. Do NOT chase tail.

### What to Test Next Season
1. **MULTI_DAY Class Booking:** Forum confirms MULTI_DAY is a signal flag, not direct offer. Book into DAY_1_5 when MULTI_DAY peaks. Test d1-d30 whether bookable MULTI_DAY offers exist or signals translate to DAY_1_5/OVERNIGHT only.
2. **Peak Tail Extension Window:** S6 showed peak tail (d112-d120) is HOTTER than peak start (d105-d111). Test committing PTO for rolling 5-day window instead of fixed 14-day window at season start.
3. **Class Efficiency Ranking:** Verify streaker forum claim that DAY_1_5 > OVERNIGHT > THREE_QUARTER (not opposite). If true, THREE_QUARTER is workhorse early signal, but swap to longer classes when capital allows.
4. **Water Temp as Gate 2 Validator:** Test if 18°C is actually the threshold or if lower (17.5°C, 17°C) works. S6 d91 was 18.3°C (confirmed), but was there usable fishing at 17.8°C anywhere?
5. **"One Hot Boat" Noise Filter:** Implement fleet-wide rule: ONLY book if ≥5 trips recorded for class on that day. If <5, it's noise (likely one or two boats, not representative).

---

# S7 QUICK START (d1-d91 CRITICAL)

**Day 1-9:** Check if ONI is published. Read climate table for latest oni value.
- ONI > +0.3 (El Niño): April-May peaks live. Phase 1 capital: $800 min to book d91+.
- ONI < -0.3 (La Niña): October peak only. Phase 1 hold dry (accumulate $1600+).
- Neutral (-0.3 to +0.3): Watch fleet signal d1-d91, book first sustained peak >0.2 yt/angler.

**Three-Gate Rule (EVERY NIGHTLY DECISION d91+):**
1. CLASS signal ≥0.2 yt/angler fleet avg (DAY_1_5/OVERNIGHT ≥0.5; not single boat noise)
2. Water ≥18°C sustained (Scripps Pier hourly avg)
3. Capital ≥ trip_cost + phase_min ($800 Phase 1 d91-d135, $300 Phase 3 d206-d320)

**HOLD ALL GATES.** Book ONLY if all three pass. NEVER book if budget < $300 mid-peak.

**Phase 2 (d135-d206):** Hold dry. Accumulate capital for Phase 3. Zero bookings.

---

# SEASON 6 & 7 PLAN (d152, 21:00 planning turn — VERIFIED DATA)

## S6 Verified Twin-Peak Regime (Query: S6 d90-d125 THREE_QUARTER yt/angler)

**Peak 1 ("Spring Heat," d106-d111):**
- d106: 1.27 yt/angler
- d108: 2.11 yt/angler
- d111: 3.63 yt/angler (peak high)
- Personal shares: 1.606 → 1.706 → 2.807 (DAY_1_5) → 1.100
- **I booked all 7 days, shared 7.52 fish**

**Peak 2 ("Tail Heat," d112-d120) — MISSED ENTIRELY:**
- d112: 2.04 yt/angler (peak didn't collapse; it CONTINUED)
- d113: 2.35 yt/angler
- d114: **3.98 yt/angler** (even hotter than my best peak day 3.63)
- d117: 2.32 yt/angler
- d118: 3.08 yt/angler
- d120: 1.42 yt/angler
- **Opportunity:** 8 days × avg 2.4 yt/angler = ~19 fish available. I caught 0.

**Collapse (d121+):**
- d121: 0.28 yt/angler
- d122-d125: <0.4 yt/angler (dead zone confirmed)

---

# SEASON 6 POSTMORTEM (S6 d213, 21:00 planning turn — SEASON ENDED BROKE)

## S6 FINAL STATS

**Season 6 Performance:**
- Season score: 13.7521 fish (8th place, 30 agents)
- Cumulative score: 0.224 (28th/30, S2 + S6 = 0.224 + 13.75 = 13.974)
- Budget left: $100 (cannot book anything >$80 trips)
- PTO left: 5 uncommitted days (locked by 14-day weekday lag until ~d196)
- Trips booked: 8 THREE_QUARTER + 1 DAY_1_5 (9 total, all d94-d111)
- Discipline run: 70 days (d113-d182) holding dry

**Leaderboard Context (S6):**
- elnino: 14.246 fish (6th place, cumulative #1 at 15.335)
- thrifty_solo: 19.603 fish (1st place, but cumulative rank 16)
- frontloader: 14.571 fish (3rd place, cumulative #3 at 14.204)
- calendarist: 12.274 fish (9th place, cumulative #4 at 12.794)
- **overreactor:** 13.752 fish (8th place, cumulative #28 at 13.974) ← **Locked out of cumulative top 15 by S2 failure**

## THE WITNESS PEAK: d175-d182 (Underfunded & Held Discipline)

**Live Peak Signal (water 20-21°C sustained):**
- d175: THREE_QUARTER 3.27 yt/angler
- d176: THREE_QUARTER 3.438 yt/angler 
- d177: THREE_QUARTER 3.194 yt/angler
- d178: THREE_QUARTER 2.151 yt/angler
- d179: THREE_QUARTER 1.92 yt/angler
- d180: THREE_QUARTER 1.427 yt/angler
- d181: THREE_QUARTER 2.092 yt/angler
- d182 (TODAY): THREE_QUARTER 2.704 yt/angler

**Why I Held Dry Despite Witnessing 1.4-3.4 yt/angler for 8 consecutive days:**
1. Budget underfunded: $100 < $150 (THREE_QUARTER cost) — no way to book the hot class
2. Only affordable option (TWILIGHT/HD_PM $80): 0.16 yt/angler signal = expected <0.2 fish for $80 investment
3. PTO exhausted: 5 uncommitted days with 14-day lag locking out weekday d183+ bookings (deadline to commit was d169, already passed)
4. No bookable alignment: Weekend trips unavailable at peak time; TWILIGHT boats show weak signal

**Math on holding:**
- Expected value of $80 TWILIGHT trip: 0.16 yt/angler × small angler count = ~0.15 fish expected
- Cost of not fishing: Preserve $100 for S7 capital
- **Outcome: Witness, hold, move.** This is discipline working exactly as intended.

## THE HIDDEN PEAKS: d175-d213 FULL ARC (VERIFIED d213 QUERY)

**d175-d182 (Witnessed, Held Underfunded):**
- Real THREE_QUARTER peak 3.27→3.44→3.19→2.15 yt/angler (8 days sustained)
- **Correctly held because:** capital $100, PTO exhausted, no path to $150 THREE_QUARTER
- TWILIGHT weak (0.16) ≠ real alternative

**d185-d190 (MISSED POST-PEAK EXTENSION):**
- d185: THREE_QUARTER still 2.033 (peak tail continuing)
- My mistake: d185 chased HD_PM "hot boat myth" (New Seaforth 0.055 on d184), got 0 yt, burned $80
- **Why this broke me:** $100→$20 in one trade on a one-day boat signal
- Fleet reality d185-d190: THREE_QUARTER 2.03→4.05→2.11→1.53→1.53 (all >1.5, bookable signal)
- **Cost of myth:** Missed $150 × 3 trips at 2.5+ yt/angler average = 7.5+ fish opportunity

**d191-d202 (MULTI_DAY SUPER-PEAKS — LANDLOCKED):**
- d191 MULTI_DAY: 2.0 yt/angler | d192 MULTI_DAY: 2.365, DAY_1_5: 2.426
- d194-d196: OVERNIGHT 1.739, DAY_1_5 1.291-1.395
- d200-d202: MULTI_DAY 0.72→5.174→1.407 (massive variance but $550 overnight unaffordable)
- **All inaccessible at $20 budget**

**d210-d212 (SEASON'S TRUE MEGA-PEAK — WATCHED FROM DOCK):**
- d210: DAY_1_5 2.293 yt/angler, OVERNIGHT 1.657
- d211: DAY_1_5 3.673 yt/angler (best non-multi-day in season), OVERNIGHT 2.191 
- d212: DAY_1_5 4.107 yt/angler (🔥 SEASON PEAK), OVERNIGHT 2.049
- **Even d213 (today):** OVERNIGHT 0.683, THREE_QUARTER 0.498 (still bookable)
- **Cost of d185 myth:** $400 × 2-3 trips at these rates = 8-12 fish opportunity

**TOTAL SEASON HEAT MAP:**
- d105-d111: Spring peak 1.6-2.8 (booked, 7.52 fish) ✅
- d112-d120: Tail continuation 2.0-4.0 (missed, ~19 fish opportunity) ❌
- d175-d182: Fall rebound 2.15-3.44 (witnessed, held, correct) ⚠️
- d185: Single boat chase myth 0.0 (burned $80) 🔥 UNFORCED ERROR
- d210-d212: Season mega-peak 2.1-4.1 (watched broke) ❌❌

---

## S6 FINAL LESSONS: "THE PERSONA TRAP — OVERREACTION TO NOISE"

**What went right (d91-d111):**
1. ✅ Detected El Niño early (ONI +0.7, water 18.3°C at d91)
2. ✅ Locked October window PTO (d105-d112) with 14-day head start
3. ✅ Rode peak hard (7 trips d105-d111, 7.52 shares, avg 1.08/trip)
4. ✅ Held discipline d113-d182 (70 days dry, $100 + 5 PTO intact)
5. ✅ Avoided TWILIGHT trap (avoided 0.0-0.164 yt/angler noise, many days)

**What went wrong (d105-d111 all-in, d112-d120 missed):**
1. ❌ "All-in" reflex on peak 1 (d111 best trip 1.733 share, then declared victory)
2. ❌ No capital reserved for peak tail (d112-d120 was HOTTER 2.0-4.0 yt/angler, completely missed)
3. ❌ Committed PTO 14 days ahead on fixed window (d105-d112) instead of rolling window (d105-d120)
4. ❌ Confused "good last trip" with "peak is ending" (d111 was peak BEGINNING its tail, not end)

**The Persona Trap:** "Overreactor" means I should react hard to signals, but I **over-reacted to NOISE (d185 boat myth) and UNDER-reacted to SUSTAINED PEAKS (d185-d190 tail, d210-d212 mega-peak).**

After d111 peak (1.733), I was capital-broke ($100 left) but had two seasons of future peaks to watch for:
- d175-d182 real peak: Correctly held (underfunded, no PTO lead). ✅ Discipline.
- d185 boat myth: Single HD_PM boat hot on d184 → chased → $80 burned → 0 yt → $20 left. ❌ Overreaction to noise.
- d210-d212 mega-peak: Watched from broke. Would've netted 8-12 fish if d185 $80 was preserved. ❌❌ Compounded error.

**Root cause:** Conflated "one good boat day" (d184 New Seaforth 0.055, 2 yt) with "peak signal". Boat performance ≠ class performance. ONE hot boat on one day is noise if the class average is weak (HD_PM d185 fleet avg 0.0 yt/angler).

**Result: Witnessed TWO peaks from broke (d175-d182 held correctly, d210-d212 held wrong). Season 6 score 13.75 (8th), cumulative 0.224 (28th). Capital broke on d185 myth = underfunded for the real mega-peak d210-d212.**

## S7 STRATEGY: "THREE-GATE RULE (REGIME + PEAK TAIL + CAPITAL BUFFER)"

**Core Problem Solved:** S2 broke on scout overspend, S6 broke on myth-chasing. Both suffered from underfunding the true mega-peak. Season 6 proved peaks have multi-phase structure (spring peak d105-d120, fall rebound d175-d212) spanning **110+ days**.

**Phase 0: Climate Detection (d1-d30)**
- Check if ONI published by d9-d30
- ONI > +0.3 (Warm/El Niño): April IS bookable, deploy early
- ONI < -0.3 (Cold/La Niña): April dead, hold for October peak
- ONI -0.3 to +0.3 (Neutral): Watch fleet, book first signal ≥0.2 yt/angler

**Phase 1 (d91-d135): Adaptive Scout (CAPITAL CAP $400 MAX)**
- IF warm regime: Book 2-3 scout trips d91+, budget cap $400 (was $300, raised to account for $550 overnight optionality)
- IF cold regime: Hold dry, accumulate capital
- IF neutral: Watch fleet signal, book 1 scout if confirmed ≥0.3 yt/angler

**Phase 2 (d135-d206): Accumulate & Watch (PEAK TAIL HUNTING)**
- IF warm: Hold dry, accumulate $1400+ for fall peaks ($150 × 8-10 trips for d175-d212 range)
- IF cold: Hold dry, accumulate $1200+ for October mega-peak (d287+ as S2 shows)
- IF neutral: Selective booking only if signal ≥0.2 + water ≥18°C
- **NEW:** Watch for "sustained peaks" = 2+ days at 2+ yt/angler → extend 5-8 days more

**Phase 3 (d206-d320): Peak Execution (MEGA-PEAK WINDOW)**
- IF warm (like S6): Sept signal d206-d212 is the mega-peak, NOT Sept open. Deploy $800-1000 for d210-d212 class peaks.
- IF cold (like S2): Skip Sept, deploy October ($1200-1400) when water ≥18°C + DAY_1_5 ≥0.3
- IF neutral: Test Sept 1-2 trips ($200-300), hold for October

**Hard Rules (NON-NEGOTIABLE):**
1. **No single-boat chasing:** One hot boat on one day = noise. Only book if CLASS average ≥ threshold (not 1 boat ≥ threshold).
2. **Peak tails cost more than peaks:** Reserve 25-30% of capital for d112-d120 (Spring tail) + d210-d212 (Fall mega-peak). S6 proof: d210-d212 was BEST fishing (4.1 yt/angler) but came after spring peak burn.
3. **Three-gate rule (don't book until all three pass):**
   - Gate 1: Class fleet avg ≥ threshold (≥0.2 or ≥0.5 for OVERNIGHT/DAY_1_5)
   - Gate 2: Water temp ≥18°C sustained (not one-day spike)
   - Gate 3: Capital reserved ≥ trip cost + $800 buffer (can't book if breaking this rule)
4. **Commit PTO 3-5 days only** (not 14+ speculative windows)
5. **Pause after 3 consecutive booking days** (check if signal sustained ≥ original threshold on day 4)
6. **Hold $400-500 minimum always** (landlocked otherwise)

## S7 STARTING CAPITAL & PTO

- Budget: $2000 (fresh S7) + $100 (S6 remainder) = $2100 total
- PTO: 10 days (fresh S7) + 5 days (S6 remainder) = 15 total
- **Cumulative deficit:** elnino 15.335 leads, I'm at 13.974 = 1.36 fish behind
- **To reach top 15 cumulative:** Need S7 score ≥ 2-3 fish minimum (cumulative 16+). If both peaks fire (April + October in warm regime, or October in cold), 6-10 fish reachable → cumulative 20-24 → top 10 possible.

## S7 d91 CHECKLIST (Immediate)

1. **Check climate:** Is ONI published? If yes, use it to pick regime (warm/cold/neutral)
2. **Check water temp:** Scripps Pier avg. If ≥18°C, bookable. If <17°C, hold.
3. **Check fleet signal:** Last 3 days avg. Day_1_5 ≥0.3 or THREE_QUARTER ≥0.8 = scout trigger
4. **If warm + signal ≥0.3:** Book 1 THREE_QUARTER scout ($150), reason = "Warm regime detected, Phase 1 scout."
5. **If cold + no signal:** Hold dry, accumulate capital for October (d287+)
6. **If neutral + signal ≥0.2:** Book 1 scout ($150), commit PTO 3-5 days only, track spend ≤$300 cap

## S7 IMMEDIATE ACTIONS (Before d91 Nightly Turn)

1. **Submit strategy.py** (Three-Gate rule: regime + signal + capital) at next 21:00 nightly turn
2. **Verify ONI data is available** d1-d30; if yes, set regime flag (warm/cold/neutral)
3. **Pre-commit S7 PTO windows:** Check calendar d91-d135; if warm regime, lock d105-d115 window (3-5 days). If cold, skip April.

## S7 NIGHTLY CHECKLIST (d91+, every 21:00)

**EVERY TURN (All gates required to book):**
1. **Gate 1 (Signal):** Class fleet avg (not single boat) ≥0.2 yt/angler (or ≥0.5 for OVERNIGHT/DAY_1_5)
2. **Gate 2 (Water):** Scripps Pier ≥18°C sustained (not one-day spike)
3. **Gate 3 (Capital):** Budget ≥ trip cost + phase buffer ($800 Phase 1, $300 Phase 3)

**IF all three gates pass:**
- Commit PTO 3-5 days ahead ONLY (exact calculation backward from fishing date)
- Book DAY_1_5 first (priority 1), then OVERNIGHT (priority 2), then THREE_QUARTER (priority 3)
- Reason: "Signal X.XX yt/angler, water X°C, capital $X, phase [1/2/3]"

**IF any gate fails:**
- HOLD DRY. No booking. Log gate that failed.

**CRITICAL CAPITAL RULES (S6 VERIFIED FAILURE MODE):**
- Phase 1 (d91-d135): Never deploy if budget < $800 remaining (trip cost + $800 buffer minimum)
- Phase 2 (d135-d206): HOLD DRY. Accumulate capital. Zero bookings.
- Phase 3 (d206-d320): Never deploy if budget < $300 remaining (trip cost + $300 buffer minimum)
- Absolute floor: Never go below $300 total during any active peak (S6 d185 myth broke this, watched mega-peak d210-d212 from $20)
- **One trip too many kills seasons:** If unsure about capital sufficiency, HOLD DRY. Season ends Oct 31; peaks continue but you won't have money.

**End-of-season (d320+):**
- Only book if budget ≥ $300 remaining AND signal ≥0.3 AND water ≥18°C
- Otherwise hold dry and preserve $100+ buffer

---

## S6 DATA VERIFICATION (d335, Final Analysis)

**S6 Window Peaks (Fleet Averages by Class):**
- April-May (d91-d151): THREE_QUARTER avg 1.227, peak 4.024 (55 days)
- June-August (d152-d243): All classes weak (avg 0.6-0.8, peaks 4.0)
- September (d244-d274): Dead zone (avg 0.3-0.6)
- October+ (d275+): **DAY_1_5 avg 1.882, peak 8.353** ← Season's best fishing

**S6 Critical Peaks I Missed:**
1. **d112-d120 tail:** THREE_QUARTER 2.2-4.0 yt/angler (8 days, ~19 fish opportunity) ← Under-capitalized, could not book
2. **d175-d182 fall rebound:** THREE_QUARTER 2.15-3.44 yt/angler (witnessed, correctly held dry—underfunded)
3. **d185 boat myth:** HD_PM single boat signal chased, got 0 yt, burned $80 → broke capital
4. **d210-d213 pivot:** DAY_1_5 3.67-4.11 yt/angler (3 days, 3.15 fish opportunity) ← Broke watching
5. **d292-d311 mega-peak:** DAY_1_5 6.1-8.4 yt/angler (10+ days, 20+ fish opportunity) ← Completely broke

**Why I Broke:**
- Booked 7 THREE_QUARTER + 1 DAY_1_5 (d94-d111): Got 7.52 fish ✅
- d185 myth chase: -$80 for 0 yt ❌ (this broke capital discipline)
- Then watched d210-d213 and d292-d311 mega-peaks from $20 budget ❌❌

**S6 Outcome:** 13.75 fish (8th place). Cumulative 0.224 (28th). Would've been 18-20 fish if d185 myth was avoided and capital was preserved for October peaks.

---

## S7 REGIME-BASED STRATEGY (LOCKED FOR EXECUTION d1+)

**S7 Starting Resources:**
- Budget: $2000 (fresh) + $20 (S6 carry) = $2020
- PTO: 10 (fresh) + 5 (S6 carry) = 15 total
- Cumulative deficit: -1.36 fish vs elnino (#1 at 15.33)

**Day 1-9: Climate Regime Detection**
1. Query climate table for ONI (index_id = 'oni')
2. If ONI > +0.3 (El Niño): Deploy early d91-d130 on THREE_QUARTER (avg 1.23), hold d131-d180, then deploy d180-d212 on DAY_1_5 (avg 1.1-3.7)
3. If ONI < -0.3 (La Niña): Hold dry d1-d280, deploy d280-d320 on DAY_1_5 (Oct mega-peak, avg 1.88, peaks 8.3)
4. If -0.3 to +0.3 (Neutral): Watch fleet d1-d91, book first confirmed peak ≥0.3 yt/angler sustained 3+ days

**Three-Gate Rule (NON-NEGOTIABLE for ALL bookings):**
1. **Signal Gate:** Class fleet avg ≥0.2 yt/angler (≥0.5 for DAY_1_5/OVERNIGHT); NOT single-boat noise
2. **Water Gate:** Scripps Pier ≥18°C sustained (hourly avg, not one-day spike)
3. **Capital Gate:** Budget ≥ trip_cost + phase_minimum ($800 for Phase 1, $300 for Phase 3)

**Book ONLY if all three gates PASS. Otherwise HOLD DRY.**

**Class Priority (DAY_1_5 > OVERNIGHT > THREE_QUARTER):**
- DAY_1_5 consistently outperforms by 30-50% in peaks (S6 data: Apr-May peak 1.63 vs THREE_QUARTER 4.02 on same days = only 61% efficiency; but Oct 8.35 DAY_1_5 vs 5.0 THREE_QUARTER = 167% edge!)
- OVERNIGHT secondary (3.0-5.0 peak days)
- THREE_QUARTER workhorse for Phase 1 (d91-d130 El Niño peaks)
- NEVER book TWILIGHT/HD classes (data shows <0.2 yt/angler avg, noise trap)

**CRITICAL: MULTI_DAY is NOT a bookable class** (forum correction confirmed)
- MULTI_DAY is fleet aggregation only (2+ day trips pooled)
- Use MULTI_DAY signals to TIME bookings (when MULTI_DAY peaks, DAY_1_5/OVERNIGHT also peak same days)
- Book into DAY_1_5 during those windows, not the "MULTI_DAY class" itself (doesn't exist as offer)

**Phase Structure:**
- **Phase 1 (d91-d135, Warm regime):** Deploy max $400-800 on THREE_QUARTER (1.23 avg), book 3-5 trips if all gates pass
- **Phase 2 (d135-d206):** HOLD DRY. Zero bookings. Accumulate capital $1200+ for Phase 3
- **Phase 3 (d206-d320, Warm regime):** Deploy $800-1200 on DAY_1_5 when peaks fire (d180-d212 or d280-d320 depending on regime)
- **Cold regime override:** Skip Phase 1-2 entirely, hold dry d1-d280, deploy d280-d320 on October DAY_1_5 mega-peak

**Peak Decay Rule:** After day 10 of sustained signal ≥0.2, lock remaining capital. Do NOT chase tail.

**S7 Target:** 15-20 fish (warm regime) or 12-18 fish (cold regime) → cumulative 16-26 → top 10 cumulative possible

---

## S7 FORUM LESSONS (d244-d305 Post-Mortem Synthesis + Verified Analysis)

**From elnino, streaker, calendarist (top finishers):**

1. **Regime Detection (CRITICAL - elnino won with this)**: Check ONI by d9. Determines entire season structure.
   - **Warm (El Niño, ONI > +0.3):** Peaks in April-May d91-135 AND August-Sept d206-240. MULTI_DAY 1.55-2.02 yt/angler. Deploy $800-1200 early.
   - **Cold (La Niña, ONI < -0.3):** Single October peak d280-310 ONLY. MULTI_DAY 7.28 yt/angler (3.6x warm regime!). Hold dry April-Aug, deploy $1400+ Oct.
   - **Neutral:** Watch fleet d1-d30; first sustained signal ≥0.2 = scout trigger.
   - **VERIFIED S6/S2:** S6 (ONI +1.73) = El Niño twin-peak regime ✓. S2 (ONI -1.06) = La Niña October mega-peak ✓.

2. **Capital Floor (Binding Constraint - verified S6 d185 failure)**: Broke capital = zero fish and zero rank.
   - HARD RULE: Never book if budget < $300 remaining after booking
   - Mid-peak (d7-10 sustained signal): Hold $500 minimum buffer or exit peak
   - S6 d185 lesson: Chased single hot boat (0.055 HD_PM), burned $80 for 0 yt → $20 left → watched 2 peaks from dock
   - elnino rule: "Never deploy last $150; always finish $50-200 remaining"

3. **Single-Boat Myth (S6 d185 confirmed failure)**: One hot boat on one day ≠ class signal. IGNORE.
   - Only count fleet AVERAGE (≥5 trips, ≥3 boats) as signal
   - New Seaforth d184 (0.055 HD_PM on 2 yt) was noise vs actual HD_PM fleet d185 (0.0)
   - Cost: $80 burned = ~3-4 fish opportunity at fall peaks if preserved

4. **Class Efficiency (Verified MULTI_DAY 50-200% above THREE_QUARTER):**
   - **S6 Spring (d91-135):** MULTI_DAY 1.551 > THREE_QUARTER 1.337 (+16% edge)
   - **S6 Fall (d175-213):** MULTI_DAY 2.018 > DAY_1_5 1.180 > THREE_QUARTER 1.095 (+84% edge!)
   - **S2 October (d280-310):** MULTI_DAY 7.279 >> DAY_1_5 3.578 >> OVERNIGHT 2.905 (MULTI_DAY DOMINATES)
   - **S7 Priority:** Book MULTI_DAY if available; else DAY_1_5; else OVERNIGHT; never THREE_QUARTER/HD if higher-class is available
   - **Why:** MULTI_DAY boats spend 24+ hours on yellowtail grounds, higher catch rates

5. **Water Temp Threshold (Confirmed)**: 18°C sustained = bookable. Below 17°C = dead.
   - S6 d91 water 18.3°C = gate FIRED
   - Peaks don't fire at 17°C. Wait for 18°C+ before committing PTO 14 days ahead.

---

## S7 PROTOCOL (d305 LOCKED FOR S7 d1 EXECUTION)

**S7 Starting Resources:**
- Budget: $2000 (fresh) + $100 (S6 remainder) = $2100 total
- PTO: 10 (fresh) + 5 (S6 remainder) = 15 total
- ONI: Currently 1.73 (strong El Niño, likely warm regime for S7)
- Cumulative deficit: -1.36 fish (need S7 ≥ 2-3 to break top 15)

**Phase 0: Climate Detection (S7 d1-d10, IMMEDIATE)**
1. Query climate table for ONI value available by d9
2. If ONI > +0.3: Warm regime → d91 April peaks are REAL peak
3. If ONI < -0.3: Cold regime → October d280+ peaks only peak
4. If -0.3 to +0.3: Neutral → watch d1-d30 fleet signal

**Phase 1 (S7 d91-d135): Adaptive Scout by Regime**
- **IF WARM (like S6):** Scout Phase 1 (max $400 capital deployment)
  - Book d91-d100: 1-2 scout trips (THREE_QUARTER/MULTI_DAY), test signal
  - If fleet ≥ 0.3 yt/angler sustained, lock PTO d105-d135 for peak window
  - Deploy max $800 for peak, preserve $1200+ for Phase 3 (d206-d240)
  - Exit if capital hits $300 floor or signal drops below 0.2 (7+ days)
  
- **IF COLD (like S2):** Hold dry, accumulate capital
  - Zero bookings d91-d135. Preserve all $2100 for October
  - Accumulate $1400+ minimum for Oct multi_day deployment
  
- **IF NEUTRAL:** Selective booking
  - Scout max $300 (1-2 trips), signal threshold ≥0.2 + water ≥18°C both required
  - Exit if signal < 0.2 for 3 consecutive days
  - Preserve $1700+ for next peak window

**Phase 2 (d135-d206): Accumulate & Watch (PEAK TAIL HUNTING)**
- **IF WARM:** Hold dry, accumulate $1200+ for Phase 3 fall peaks (d206-d240)
  - Watch d175-d190 fleet signal (real peaks continue if water ≥18°C + class ≥0.3)
  - Only book if ALL THREE gates aligned: signal, water, capital
  - Book max 3-4 trips if fire, then EXIT (day 11+ is decay)
  
- **IF COLD:** Continue hold dry
  - Accumulate $1400+, defer all PTO
  - Prepare October deployment window d250 onwards
  
- Monitor weekly: Is water ≥18°C? Is class signal >0.2? Is capital >$500?

**Phase 3 (d206-d320): Peak Execution (MEGA-PEAK WINDOW)**
- **IF WARM (like S6):** August-Sept mega-peak window
  - August MULTI_DAY often stronger than May (S6 data: d175-d213 avg 2.02 yt/angler)
  - Deploy $800-1200 if signal ≥0.3 + water ≥18°C sustained
  - Book d206-d212 if fleet hot (3.0+ yt/angler sustained 3+ days)
  - **NEVER book after day 10 of signal** (decay law)
  - Preserve $300 floor always, exit if capital < $300

- **IF COLD:** October peak d280-d310
  - Deploy $1400-1600 MULTI_DAY class (7.28 yt/angler!)
  - Book d287-d297 (proven Friday peak window from S2)
  - Only class to book: MULTI_DAY + DAY_1_5
  - Exit if capital < $300 or signal < 0.5 for 5+ days

**Hard Rules (NON-NEGOTIABLE):**
1. **Three-Gate Rule (All gates required):** Signal ≥0.2 fleet avg (or ≥0.5 for OVERNIGHT/DAY_1_5/MULTI_DAY) + Water ≥18°C sustained + Capital ≥ trip cost + $300 buffer
2. **No single-boat chasing:** One hot boat ≠ class signal. Only count fleet average (≥5 trips, ≥3 boats minimum)
3. **Capital floor $300:** Never book if remaining capital < $300. Never go below $50.
4. **Peak decay (day 11+ rule):** Do not book day 11+ of sustained signal unless signal STRENGTHENS. Exit by day 10.
5. **No recovery gambles:** If capital breaks $300 mid-peak, HOLD DRY. Never chase recovery trades.
6. **Commit PTO 3-5 days only ahead** (not speculative 14+ day windows at season start)
7. **MULTI_DAY priority:** If multiple classes fire same day, book MULTI_DAY first (1.55-7.28 vs 0.7-1.3 others)

**S7 D91+ CHECKLIST (At Each 21:00 Nightly Turn):**
1. Gate 1 (Signal): Is class fleet average ≥ 0.2 yt/angler (0.5 for overnight/day_1_5)? YES/NO
2. Gate 2 (Water): Is Scripps Pier ≥ 18°C sustained (not 1-day spike)? YES/NO
3. Gate 3 (Capital): Is budget ≥ trip cost + $300 buffer? YES/NO
4. **IF ALL THREE YES:** Commit PTO 3-5 days ahead, book DAY_1_5/MULTI_DAY/OVERNIGHT in priority order, log gate status
5. **IF ANY NO:** HOLD DRY, log which gate failed, check next day

**Expected S7 Outcome (If Protocol Holds):**
- Warm regime: 15-20 fish (vs S6's 13.75, avoiding d185 myth + capturing full peak tail)
- Cold regime: 18-25 fish (vs S2's 0.224, with capital fully allocated to mega-peak Oct)
- Cumulative target: 18-25 fish total (vs current 13.974) → Top 5-10 possible

---

## S7 d1 IMMEDIATE ACTIONS (MORNING TURN, 16:00)

**NO BOOKINGS TODAY.** This is climate detection phase, not action phase.

1. **Check climate table:** Query for ONI (index_id = 'oni'). Look for most recent value available by d1-d9.
2. **Record regime classification:**
   - If ONI > +0.3: Write "WARM REGIME DETECTED" → proceed to Phase 1 scout d91
   - If ONI < -0.3: Write "COLD REGIME DETECTED" → proceed to Phase 2 hold dry d1-d280
   - If -0.3 to +0.3: Write "NEUTRAL REGIME" → watch fleet d1-d91 for signal
3. **Check water temperature:** Scripps Pier current temp. If ≥18°C, gate 2 will fire at d91. If <17°C, wait for warming.
4. **Update private notes with regime classification** (today's date + regime + reasoning)
5. **Hold dry:** Do NOT commit any PTO or make any bookings today. Regime detection is the ONLY action.

**This turn's output to verify:** Did I correctly detect ONI value and classify warm/cold/neutral? If yes, S7 is on track.

---

## S6 FINAL SCORE (d335, Season Over)

- **Final Score:** 13.7521 fish
- **Season Rank:** 10/30
- **Cumulative Score:** 0.224 (S2) + 13.75 (S6) = 13.974
- **Cumulative Rank:** 28/30
- **Budget Left:** $20
- **PTO Left:** 5 days
- **Lessons Locked:** Three-Gate Rule + Regime Detection + Capital Discipline
- **S7 Reset:** $2020 budget, 15 PTO, Phase 0 climate detection d1-d9 active

---
