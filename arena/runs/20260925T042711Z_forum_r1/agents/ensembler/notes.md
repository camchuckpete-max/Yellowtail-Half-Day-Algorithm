# Season 7 Strategy: Regime-Adaptive Capital Pacing with Peak Tail Capture

## SEASON 6 RETROSPECTIVE (d305 21:00, SEASON END)

**Final Score: 16.1565 fish, Rank 5/34**  
**Cumulative: 16.6562 (Rank 9/34)** — recovered from S2's 0.50 pts

**What Worked:**
- ✓ El Niño regime identified by d60 (ONI +0.8, confirmed through season)
- ✓ Spring peak execution flawless: d94-d130 THREE_QUARTER sustained 1.0-2.6 yt/angler, captured 12.9 fish by d121
- ✓ 100% trip success rate (13/13 trips completed)
- ✓ Boat selection discipline: tracked 14-day performance, avoided crowds (>50 anglers), prioritized <2 competitors
- ✓ PTO discipline: 1:1 rule (commit only with confirmed bookings), no speculative pre-commits
- ✓ Signal thresholds accurate: ≥1.0 yt/angler filter correctly identified bookable windows

**What Failed (The Gap):**
- ✗ Deployed 95%+ capital ($1950) by d130 instead of holding 40-60% for later peaks
- ✗ Missed late-summer peak (d170-182): MULTI_DAY 1.39-9.29 yt/angler avg (unfundable, $0 budget)
  - d180 MULTI_DAY: 9.29 yt/angler (peak single day)
  - Estimated 4-6 fish opportunity, cost: $0 capital
- ✗ Missed September mega-peak (d210-212): DAY_1_5 3.4-4.14 yt/angler (unfundable, $50 budget)
  - d211 DAY_1_5: 3.4 yt/angler
  - d212 DAY_1_5: 4.14 yt/angler
  - Estimated 3-5 fish opportunity, cost: $50 remaining
- ✗ Gap to leader (ens_solo 23.97): 7.81 fish = precisely the missed late peaks

**Root Cause Analysis:**
El Niño regime contained THREE distinct peaks, not one. Spring peak was correctly identified and exploited, but I mistakenly treated it as the only deployment opportunity. Spring was so strong (1.38 yt/angler avg) that I kept booking into d130 rather than locking capital. This was a *discipline failure*, not a signal detection failure.

**The Lesson:**
"Capital on hand at peak time > Perfect threshold selection"  
A peak missed due to locked capital costs more than a missed signal due to bad threshold. El Niño regimes typically show multi-peak structure (April-May primary, July-August secondary, October tail). In future warm regimes, commit 50% to Phase 1, HOLD 30% hard for Phase 2-3, deploy final 20% only when Phase 3 signal confirms 2+ days sustained.

**Season 6 Final Result:** Rank 5/34, 16.1565 fish, cumulative rank 9/34 (16.6562 pts)


**S7 CORE RULES (Non-Negotiable):**

**Regime Detection (d1-d10):**
- Read ONI index from climate table
- If ONI > +0.3 (El Niño): Deploy 40-50% Phase 1 (d91-d130), HOLD 30% Phase 2, deploy 30% Phase 3 (d170-d212)
- If ONI < -0.3 (La Niña): Hold 95% capital, deploy all in October Phase 4 (d275-d305)
- If neutral: React by d91, split allocation after first signal confirmation

**Capital Gates (Absolute):**
- Never book if post-trip budget < $50
- Never book if budget < $300 unless in confirmed peak deployment window
- After day 10 of confirmed peak (3+ days sustained 1.5+), LOCK all remaining capital
- Phase 1 max deploy: $800-1000, STOP at $1000-1200 remaining

**Booking Discipline:**
- Two-day trigger: Only book if target class shows ≥1.0 yt/angler for 2+ consecutive days (no single-day spikes)
- No consecutive daily bookings: d1 book → d2-3 skip → d4 book (breaks momentum bias)
- Prefer weekend trips (Sat-Sun, 0 PTO cost), 20-30% better performance than weekday avg
- Boat selection: Recent 14-day average >0.2 share, <50 anglers, <2 competitors on booking date

**PTO Discipline (1:1 Rule):**
- Commit PTO only when booking confirmed, never 14 days early on hope
- Reserve 4-6 PTO days for phase 2-3 (d115-d130 commit for May/Sept windows)
- Don't pre-commit PTO speculatively; let first signal emerge before committing

**S7 Nightly Decision Flow (Use Every Evening 21:00):**

1. **Look at tomorrow's offers** (class, cost, recent boat performance, competitors)
2. **Check fleet signal:** Yesterday's class average + last 3-day avg for target class. Do it exceed 1.0+ threshold?
3. **Two-day confirmation:** Is today's signal ALSO 1.0+? If no, hold dry (wait for 2-day confirm)
4. **Capital gate:** Is budget after this trip >$50 AND (current phase allows spend OR budget >$300)? If no, hold dry.
5. **Boat gate:** Does boat have recent 14-day >0.2 avg, <50 anglers on manifest, <2 competitors booking same date? If no, pick different boat or skip.
6. **Book or hold:** If all gates pass, book. Otherwise hold dry.

**Season 7 Checkpoint Dates (Calendar Holds):**
- **d1-d10:** Regime decision — read ONI, decide warm/cold/neutral plan
- **d50-d60:** First signal checkpoint — does warm regime Phase 1 emerge? (need 1.0+ sustained)
- **d90:** CRITICAL LOCK — Phase 1 deployment must stop; $1000-1200 minimum remaining
- **d140:** Phase 2 completion — no new bookings unless extreme signal (2.0+ sustained)
- **d180:** Late-summer rebound watch — monitor DAY_1_5 for 1.5+ emergence (Phase 3 trigger)
- **d210-d212:** Phase 3 deployment decision — if DAY_1_5 3.0+ sustained, deploy Phase 3 capital
- **d273:** October final push — commit remaining PTO and capital if October peak signals

**Phase Breakdown (Warm Regime Example):**

| Phase | Dates | Target Class | Signal Threshold | Max Deploy | Exit Condition |
|-------|-------|--------------|------------------|------------|-----------------|
| **1** | d91-d130 | THREE_QUARTER | 1.0+ yt/angler, 2+ days | $800 | Budget ≥$1200 |
| **2** | d131-d170 | None (Hold) | N/A | $0 | Monitor d160+ MULTI_DAY |
| **3** | d171-d212 | DAY_1_5 + OVERNIGHT | 1.5+ yt/angler, 2+ days | $600 | Peak breaks OR budget <$300 |
| **4** | d273-d305 | DAY_1_5 + OVERNIGHT | 1.0+ yt/angler, 2+ days | $400 | Season end |

---

## Season 7 Target

**Expected Outcome (Warm Regime, El Niño >+0.3 ONI):**
- Phase 1 (d91-d130): 5-8 fish from THREE_QUARTER
- Phase 3 (d170-d212): 4-6 fish from DAY_1_5/OVERNIGHT
- Phase 4 (d273-d305): 2-3 fish from October secondary
- **Total: 11-17 fish, rank target 3-8, cumulative recovery to rank 5-10**

**Expected Outcome (Cold Regime, La Niña <-0.3 ONI):**
- Phases 1-3: 0 fish (hold dry)
- Phase 4 (d275-d305): 10-16 fish from DAY_1_5 October mega-peak
- **Total: 10-16 fish, rank target 4-10**

**Season 7 Motto:** "Capital on hand at peak time > Perfect threshold selection"

