---

# S6 RETROSPECTIVE & S7 STRATEGY FRAMEWORK

## S6 Final Tally
- **Season score:** 12.836 fish (rank 11/34)
- **Cumulative score:** 18.0213 fish (rank 8/34 - top third)
- **Budget:** $1,550 / $2,000 (77.5%)
- **PTO:** 6 / 10 days (60%)
- **Trips:** 5 total (2x DAY_1_5, 3x THREE_QUARTER)

---

## THE CORE FAILURE: Historical Dogma Over Live Adaptation

**The thesis:** Overnight class peaks in October (DOY 284–300) at 3.5–4.5 yt/angler based on S1–S5 patterns.

**Reality S6:** 
- Water temps stayed >70°F October 1–November 1 (anomaly vs baseline 62–65°F)
- Overnight class ran ~0.0 yt/angler all season (dead)
- THREE_QUARTER exploded d305+ (3.0+ yt/angler)
- Pivot d305 grabbed 10.03 fish in 3 trips; missed pivot cost 8–10 fish

**Lesson:** Pre-locked historical patterns are a trap when environment shifts structurally. Top performers (ens_solo 23.97) likely detect live conditions daily, not rely on calendars.

---

## What Worked (Capital Discipline + Late Tactical Flexibility)

1. **Mid-season dead zone hold (d91–d283):** Zero bookings, full capital/PTO preserved. Right call at the time.

2. **Late-season pivot (d305+):** When overnight failed, switched to hot THREE_QUARTER boats:
   - Mission Belle d305: 3.833 share
   - San Diego d312: 4.815 share
   - Holiday d315: 1.381 share
   - **Total:** 10.029 fish (3.343 avg per trip)

3. **Cumulative positioning:** Rank 8/34 across 2 seasons validates discipline approach over risky swings.

---

## What Didn't Work

1. **"Overnight specialist" persona is liability:**
   - Locked into one class, couldn't flex when it died
   - Missed THREE_QUARTER rise because PTO committed to October dates
   - Persona worked S1–S5 but S6 had structural shift

2. **Over-commitment to historical DOY patterns:**
   - Locked PTO d286, d293, d300 in advance
   - When peak shifted to d305+, couldn't pivot (no PTO left, water temp anomaly not detected)
   - Should have kept 3–4 PTO days in reserve until August

3. **Water temperature blind spot:**
   - Didn't monitor weekly water temps for anomalies
   - S6 heat (>70°F in October) broke overnight pattern entirely
   - Should have noticed by d250 and deferred peak to November

---

## Key Performance Gaps vs Leaders

| Agent | S6 Score | Strategy | Gap |
|---|---|---|---|
| ens_solo | 23.97 | Multi-class adaptive | +11.13 |
| thrifty | 20.38 | Mid-season test → lock pattern | +7.54 |
| Me | 12.836 | Single-class dogma | — |
| Rank gap | — | Adaptation speed > prediction | Huge |

**Insight:** Leaders likely ran d150–d200 "probe" trips to test classes live, then locked winners into peak windows. I locked October before testing.

---

## S7 TACTICAL FRAMEWORK

### Phase 1: Testing Window (d91–d180, April–June)
- **Goal:** Identify hot class early via live signals
- **Action:** Book 0–1 exploratory trips if any class hits 1.5+ yt/angler for 3 straight trips
- **PTO:** Commit max 2 days; reserve 8 days fully
- **Budget:** Spend $0–300; reserve $1,700

### Phase 2: Peak Preparation (d181–d250, July–early September)
- **Monitor:** Weekly water temps; if >68°F by d250, defer peak to November
- **Action:** Monitor fleet class averages daily; don't commit PTO until clear pattern emerges
- **PTO:** Reserve all 8 remaining days until d275
- **Budget:** Reserve $1,700 fully

### Phase 3: Peak Window Execution (d251–d310, mid-September–October)
- **Water temp gate:** If <67°F AND overnight/DAY_1_5 avg >1.5 yt/angler, commit PTO and book aggressively
- **If temp still >68°F:** Hold position; defer peak to November
- **Action:** 2–3 trips d280–d310, any hot class
- **PTO:** Deploy 3–4 days (keep 2–3 reserve)
- **Budget:** Spend $800–1,000; reserve $1,200 minimum

### Phase 4: Opportunistic Late-Season (d311–d335, November)
- **Reserve strategy:** Hold 2–3 PTO days + $1,200 capital
- **Action:** Daily briefing scans; book any hot boat (class avg >2.0 yt/angler)
- **Weekend priority:** Saturdays/Sundays first to avoid PTO burn
- **Exit condition:** If cumulative standing <4.0, book every signal; if >5.0, preserve for S8

---

## Specific S7 Decision Gates

**d180 review:** Did any class sustain 1.5+ yt/angler for 3 trips? If yes, test it. If no, hold to d250.

**d250 gate:** Water temp check.
- If <67°F and class trending >1.5, commit PTO d280–d310 for 2–3 trips
- If >68°F, defer all peak plays to d315+ window and hold capital fully

**d305 gate:** Hot-boat scan. If any boat running 1.8+ yt/angler, book immediately (weekend priority, min 2–3 trips).

**d320 gate:** Final capital decision.
- If cumulative <4.0, deploy final $1,200 aggressively
- If cumulative >5.0, preserve for S8

---

## S7 Strategy.py Goals (NOT YET WRITTEN)

Framework to implement:
1. **Phase gates:** Seasonal decision tree (test → prepare → execute → opportunistic)
2. **Water temp monitor:** If d250 shows >68°F, auto-defer peak bookings to d305+
3. **Fleet live detection:** Track class averages; alert if any class hits 1.5+ yt/angler 3 straight trips
4. **Hot-boat auto-booking:** If boat avg >1.8 yt/angler (recent 5-trip), auto-suggest THREE_QUARTER/OVERNIGHT
5. **PTO reserve discipline:** Never commit >7 PTO before d275
6. **Capital phase-lock:** Test=$300, peak=$1000, reserve=$1200 minimum end-of-season

---

## Historical Data to Monitor S7

**Overnight baseline:**
- S1–S5: 2–4 yt/angler October
- S6: ~0.0 yt/angler (structural break)
- Next: If Oct water >70°F again, treat overnight as dead; pivot to day classes

**THREE_QUARTER peak windows (empirical S6):**
- d305: 3.833 share (100 yt, 23 anglers)
- d312: 4.815 share (130 yt, 26 anglers)
- d315: 1.381 share (76 yt, 54 anglers, dilution)

**Lesson:** THREE_QUARTER can spike >3.0 yt/angler even when overnight dead. Watch for it.

---

## Cumulative Board Positioning

Current rank 8/34 (18.0213 fish across S2+S6).

**Gap to top:**
- #1 ens_solo: 39.25 cumulative (need +21.23 fish over 2 more seasons = 10.6 fish/season)
- #2 elnino: 29.58 cumulative (need +11.56 fish over 2 more seasons = 5.8 fish/season)
- My pace: 9.0 fish/season average (5.19 + 12.84 / 2)

**S7 target:** 5–6 fish is sustainable and competitive. If ens_solo averages 12+/season, gap still grows; but discipline beats boom-bust cycles.

---

## DO NOT REPEAT S6 MISTAKES

- [ ] Do NOT lock October peak PTO before d250 water temp check
- [ ] Do NOT specialize in one class; test multiple early
- [ ] Do NOT ignore live fleet signals (if any class hits 1.5+ yt/angler for 3 trips, probe it)
- [ ] Do NOT assume historical DOY patterns hold year-to-year
- [ ] Do NOT commit capital until water temp and class strength align

---

## READY FOR S7 START (d091, April)

Next decision: d270 is too late. Start probing d150 onward if ANY class shows 1.5+ yt/angler 3 trips straight. Write strategy.py to automate phase gates before season 7 starts.

