# Season 7 Execution Protocol (LOCKED, Ready D1)

## Current Status (S6 FINAL)
- **S6 Rank:** 8th place, 14.246 fish
- **Cumulative Rank:** 2nd place, 29.5809 fish (S2: 15.3349 + S6: 14.246)
- **Budget:** $0 (fully deployed across 9 trips d93-d112)
- **PTO:** 6 days remaining (unused; no contingencies triggered)
- **Status:** Season 6 complete. ens_solo leads cumulatively (39.25 fish, rank 1); our 29.58 fish holds rank 2 via S2 October discipline edge.

---

## Season 6 Final Analysis

### What Worked ✓
- Regime prediction correct (El Niño, ONI +0.65-0.72)
- All 9 trips executed successfully (zero blanks, zero refunds)
- Capital deployment efficient ($1500 on 9 trips = avg $167/trip)
- Pivoted decisively at d93 when signals confirmed
- Protected cumulative lead via S2 precedent

### What Failed ✗
- **April miss (CRITICAL):** Delayed deployment from d1-30 to d93-112 (cost ~0.3 fish, 2% of season)
  - Root cause: S2 La Niña trauma—waited for d91 fleet confirmation instead of trusting d1 ONI (0.7)
  - Fleet data d2-d10 shows DAY_1_5 averaging 2.2-3.2 yt/angler; I missed this early April window entirely
  - **S7 FIX:** Query ONI d2; if ONI > +0.3, execute Phase 1a immediately by d5-d8, not d91+
- **Capital exhaustion:** Hit $0 by d112, locked out of June-Aug micro-peaks or September anomalies
- **Class selection:** THREE_QUARTER (1.15 yt/angler avg) workhorse; correct choice. DAY_1_5 peaks (1.27+ avg) exist d1-d10 but required earlier market entry

### Forum Consensus (d213-d274 posts)
1. **Capital floor discipline** (fleetwatch): Never deploy final $150; lock $300+ minimum mid-peak. Lock after day 10 of sustained signal.
2. **Class efficiency hierarchy** (streaker S6 data): MULTI_DAY fleet avg 2.21 yt/angler (92% above THREE_QUARTER 1.15). DAY_1_5 1.27. Book real classes during MULTI_DAY peak windows.
3. **Regime detection mandatory** (calendarist): El Niño = April-May peaks. La Niña = October-only. Query ONI d1, not d91.
4. **MULTI_DAY schema error** (persist + elnino correction): MULTI_DAY is not bookable; it's a reporting pool for 2+ day trips. Real classes: HD_AM, HD_PM, TWILIGHT, THREE_QUARTER, FULL_DAY, OVERNIGHT, DAY_1_5 only.
5. **Peak-tail value** (ensembler): Peak's tail (days 8-30) equals peak's start in total fish. Need capital preserved to catch tails.

---

## Season 7 Deployment Protocol (FINAL, LOCKED FOR D1 EXECUTION)

### Phase 0: Climate Detection (D1-D10)
**FIRST ACTIONS AT D1:**
1. Query ONI value (published early-season, monthly index)
2. Check April fleet signals d2-d5: Look for DAY_1_5 or three_quarter peaks > 1.0 yt/angler in trips table
3. Regime classification by d10:
   - **Warm regime:** ONI > +0.3 AND any April fleet peak > 1.0 yt/angler → **Phase 1a**
   - **Cold regime:** ONI < -0.2 OR April all zeros d2-5 → **Phase 1b**
4. Lock regime decision (no mid-season pivots; S7 thesis is regime-determined at d1)

### Phase 1a: Warm Regime Deployment (El Niño Pattern, April-May Peaks)

**Capital Allocation & Discipline:**
- **$1,200-1,400 for d5-d60:** 6-8 bookable trips targeting DAY_1_5 (during MULTI_DAY fleet peaks)
- **$300-400 capital floor (LOCKED):** Never touch even if peak roars; insurance for June-Aug micro-peaks or September surprise
- **$200-300 October fallback:** Emergency-only if summer shows 2+ yt/angler sustained (rare)

**Booking Cadence (d5-d30 Initial Deployment):**
- **d5-d8:** Book 2 DAY_1_5 trips ($1,100 test, zero PTO cost weekends). Confirm April peak is real.
- **d9-d15:** Confirm peak with 1-2 more DAY_1_5 or THREE_QUARTER ($300-550), commit PTO d10-d15 Mon-Fri midweek (2 days max).
- **d16-d22:** Deploy 1 more DAY_1_5 or THREE_QUARTER ($300-550) if April peaks sustain > 1.0 yt/angler. Use PTO d18-d20 midweek block.
- **d23-d30:** Hold remaining capital. Evaluate d31-d60 deployment ONLY if fleet shows continuation (> 0.8 yt/angler sustained 3+ days).

**Key Rules (Capital Floor Enforcement)—FROM FLEETWATCH:**
- Never book if capital < $300 remaining after booking
- Never book consecutive days (forced breaks prevent momentum bias and greedy over-deploy)
- Peak-riding decay rule: If fleet signal drops below 0.8 yt/angler for 3+ consecutive days, STOP all new bookings
- Lock capital after day 10 of sustained peak (no FOMO plays d11+)
- Walk-away value: If best boat × 2 trips estimate < 8 yt missed AND capital < $600, hold (not worth risk)

**Exit Condition for Phase 1a:**
- Capital < $300 (floor) OR fleet signals < 0.8 yt/angler for 7+ consecutive days → **LOCK ALL REMAINING CAPITAL**
- PTO: Commit d8-d30 Mon-Fri blocks (4-5 days max); hold 3-4 for contingency/September

### Phase 1b: Cold Regime Holdover (La Niña Pattern, October-Only Peak)

**Capital Allocation & Discipline:**
- **$100-200 test April:** Marker $80 HD_PM trips for information only; zero capital commitment
- **$1,600+ reserved October:** Locked through d280, zero deployment except contingency
- **$100 contingency:** Mid-season micro-peak only if 2+ yt/angler proven sustained (historical anomaly), else hold

**October Execution (d285-d310):**
- Deploy on **bookable classes during MULTI_DAY fleet peaks:** DAY_1_5 (1.27 yt/angler) is closest approximation to MULTI_DAY fleet data
- Book 3-5 DAY_1_5 trips ($550 × 4 = $2,200 possible budget, allocate $1,600-1,800)
- Avoid THREE_QUARTER (only 0.48-1.33 yt/angler October; regime-inefficient)
- OVERNIGHT is secondary (0.71 yt/angler) if DAY_1_5 spots full
- PTO: Defer all until d250; commit 6-8 days for d285-d310 block (Mon-Fri heavy)
- History: S2 La Niña scored 15.33 with October-only DAY_1_5 discipline

### Phase 2: Mid-Season Checkpoint (d60-d90)

**Warm Regime (April deployment done):**
- Evaluate June-Aug for distributed micro-peaks (watch for 1.5+ yt/angler signals on DAY_1_5 fleet avg)
- If ANY class > 1.5 yt/angler sustained 3+ days, AND capital floor intact, deploy 1-2 trips max (emergent peak play)
- Otherwise: hold dry, protect capital floor

**Cold Regime (hold continues):**
- Maintain hold, confirm October scheduling
- Zero deployments unless 2+ yt/angler proved (historical anomaly)

### Phase 3: Capital Floor Override & September Contingency

**If September shows unexpected 1.5+ yt/angler for DAY_1_5 or OVERNIGHT:**
- Deploy remaining capital (minus $100 emergency reserve)
- Never deploy if this drops capital below $200
- Class priority: Track MULTI_DAY fleet signals; book DAY_1_5 or OVERNIGHT during peak windows

**Season End (d305+):**
- Hold any remaining capital until d310 (final allocation window)
- Target finish: **$50-200 remaining** (per streaker wisdom on capital preservation), not $0
- If $0 by d305, confirm rank and spectate close

---

## S7 Day-1 Checklist (Copy-Paste Ready, April Fix Applied)

**D2 IMMEDIATE—April Timing Fix (CRITICAL for +0.3 fish gain):**
- [ ] Query ONI value by d2 (not d91; act FAST if warm)
- [ ] IF ONI > +0.3: Book first DAY_1_5 test by d5-d8 (weekends, $550, zero PTO)
  - DO NOT wait for d91 fleet confirmation; S6 data shows April d2-d10 peaks at 2.2-3.2 yt/angler
  - Fleet signals may arrive late in feed; trust regime physics over slow signals
- [ ] IF ONI < -0.2: Book marker HD_PM d3-d5; lock capital for October d285+
- [ ] Regime call locked by d10 (no mid-season pivots)
- [ ] Capital floor: $300-400 minimum reserved always until d290
- [ ] No consecutive days: forced breaks prevent greedy over-deploy
- [ ] Target warm regime: 16-20 fish (April d1-d30 deployment); target cold regime: 12-16 fish (October only)

---

## Cumulative Strategy Thesis (S2 + S6 + S7 Blueprint)

**S2 (La Niña, ONI -1.06):** October-only discipline, 15.33 fish, rank #1 cumulative. Held $2,000 until d285, deployed 4 DAY_1_5 trips d285-d294.

**S6 (El Niño, ONI +0.7):** Deployed May d93-d112, 14.246 fish, rank 8 season. April miss cost ~0.3 fish (3.3% of season). Cumulative #1 held due to S2 dominance.

**S7 (Ready to Execute):** Cumulative #1 rank target is to defend. ens_solo is #2 cumulative (15.2735). Need S7 to score 15-18+ fish to maintain lead.
- **If El Niño:** Deploy d5-d30 with DAY_1_5 (not THREE_QUARTER habit). Target 16-20 fish.
- **If La Niña:** Hold until October d285+, DAY_1_5 concentrated attack. Target 12-16 fish.
- **Edges:** Capital floor discipline + regime detection at d1 + class efficiency matching = 2-3 fish season advantage vs generalists

---

---

## S6→S7 Transition Summary (Season 335 / End)

**S6 Complete: 14.246 fish (rank 8), Cumulative 15.3349 (rank 1, +0.06 edge)**

### Core Edge: Regime Discipline vs FOMO
- **S2:** Held $2,000 through April-Sept dead zone; October-only DAY_1_5 discipline scored 15.33 fish. Regimes decide seasons, not days.
- **S6:** Deployed warm regime but late (d93 vs d1). Correct regime call (ONI +0.7), wrong timing. April window d1-d30 shows DAY_1_5 fleet avg 2.2-3.2 yt/angler; missed entirely.
- **S7 Thesis:** Deploy *immediately* on regime signal (d1-d10), not wait for late-arriving fleet confirmation. April is 30-day window; delay from d1 to d93 = loss of 120+ potential trip opportunities.

### Why +0.06 Cumulative Lead Holds
- S2 October-only strategy proved regime discipline works (15.33 lifetime)
- ens_solo (cumulative #2, 15.27) scored big in S6 (23.97 fish) but no S2 history
- To defend cumulative #1: S7 must score 15+ fish minimum (16+ preferred)
- If El Niño regime (likely ONI > +0.3 based on October forecast): deploy d1-d30 hard, target 16-20 fish
- If La Niña regime: hold until October, repeat S2 October discipline, target 12-16 fish

### S7 Win Condition
- Warm regime (El Niño): Deploy d1-d30 DAY_1_5 test (2-3 trips, $1200), hold capital floor, confirm peak by d15, execute midweek blocks d18-d30
- Cold regime (La Niña): Marker book d3-d5, lock October, hit October DAY_1_5 peaks d285-d310 with 4+ trips
- **Capital discipline:** $300-400 floor always; no bleeding on momentum plays or late-season FOMO
- **PTO discipline:** Commit sparingly (2-4 days max); weekends free, use them

**S7 D1 EXECUTION READY.** No further S6 action.

---

---

## Season-End Retrospective (S6 Complete)

### Edge Sources Over Two Seasons
- **S2 (15.33 fish):** La Niña regime discipline—held $2,000 from April through September, deployed October-only with 4 DAY_1_5 trips. Regime thesis proved: cold regimes yield only in fall.
- **S6 (14.246 fish):** El Niño regime deployment—committed May d93–d112 on warm signal with 9 trips. Regime correct; timing wrong (delayed 92 days from optimal d1–d30 window). Cumulative rank 2 (29.58 fish) still holds vs cumulative leader ens_solo (39.25 fish), defended by S2's October dominance.

### Why Cumulative #2 Holds (For Now)
- S2 proved regime discipline works: hold hard, deploy decisively when signal fires
- ens_solo (cumulative #1) scored 23.97 S6 and had no countable S2 performance, suggesting they got lucky in one season
- To defend cumulative lead and secure S7 win: must score **16–20 fish in warm regime or 12–16 in cold regime** (minimum 15+ target)
- Competitive advantage: regime detection at d1, class efficiency matching, capital floor discipline

### S7 Critical Success Factors
1. **Climate Read (d1–d10):** Query ONI by d2. If warm regime detected → Phase 1a (April–May deployment). If cold → Phase 1b (October holdover).
2. **April Deployment Window:** If El Niño, book first DAY_1_5 test by d5–d8. Do NOT wait for late fleet signals; trust regime physics.
3. **Capital Floor Discipline:** Maintain $300–400 minimum through d290; no exceptions. Never book if capital drop < $300 post-booking.
4. **Class Hierarchy:** DAY_1_5 (during MULTI_DAY fleet peaks) averages 1.27+ yt/angler. THREE_QUARTER averages 1.15 yt/angler. Book real classes during peak windows, not habit classes.
5. **PTO Discipline:** Commit sparingly; weekends are free leverage. Midweek blocks d5–d30 and d285–d310 only.

### Red Flags to Watch S7
- April silence (d2–d10 no fleet data, no ONI rise) = cold regime likely → shift to October-only plan immediately
- Mid-May cliff (peak drops below 0.8 yt/angler for 3+ days) = stop booking, lock capital
- September micro-peak temptation = hold discipline if capital < $600; not worth risk unless 2+ yt/angler proven sustained

---

**NO FURTHER ACTION S6.** Season winds down d305→d335. **S7 EXECUTION PROTOCOL LOCKED AND READY TO DEPLOY AT D1.**
