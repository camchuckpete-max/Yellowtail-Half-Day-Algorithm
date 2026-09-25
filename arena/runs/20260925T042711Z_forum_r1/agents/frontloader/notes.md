## S06 d001 Planning Turn - Season Opening Strategy

### Current State (d001, 21:00)
- Budget: $2000 intact
- PTO: 10 days intact  
- Cumulative rank: #3 (14.204 fish from S2, practice seasons 1-5 not counted)
- Water temp: 16.06°C (61°F) - cold, spring pattern
- Season 6 fishing: doy 1 only, 0 yt average (just started)
- Climate: ONI around -0.36 to 0.92 (variable, neutral to cool regime)

### S2 Retrospective & Key Insights
**What worked:**
1. Discipline through dead zone (April-Sept hold proven effective)
2. October thesis 100% correct (doy 287-303 delivered 5.0+ yt/angler day_1_5)
3. Three-trip deployment sweet spot ($1650 for 14.2 fish = 8.5 fish per $1000)
4. Boat selection matters (Condor baseline 2.27-3.59 yt/angler proved predictive)
5. PTO flexibility via Friday-only commits (zero return-day cost)

**What missed:**
1. Early Sept mega-peak (doy 268-274) entirely missed - elnino caught 1.0-1.5 fish here
2. d275 THREE_QUARTER booking ($150, 0 fish) - wrong class in peak window
3. Calendar rigidity (locked Oct d287-297 in July, actual early peak appeared doy 268-274, 20 days early)
4. Strategy.py remained placeholder - nightly manual decisions drove results

**Key Learning:** TWO peaks, not one
- Early Sept window (doy 250-274): Soft opening doy 250-267 (0.31-1.14 avg_share), hot days doy 267-269 (1.14-1.23 avg_share)
- October window (doy 275-310): doy 280 peak (2.68 avg_share, 60 yt/angler!), doy 287 secondary peak (2.26 avg_share)
- Water temp ≥18°C sustained signals early peak, ≥16°C sustained signals October main peak
- Day_1_5 ONLY in peaks (3.6-5.2 yt/angler), never THREE_QUARTER (0.005-0.13 yt/angler)

### S06 Playbook (Refined from S2 Experience)

**Phase 1 (April-June, doy 1-180):** Strict dead zone hold
- Budget: $1400 reserved (do NOT deploy)
- PTO: 8 days reserved (do NOT commit)
- Action: Zero bookings through d179
- Monitor: Water temp daily from doy 180+; if ≥18°C sustained (3+ days), prepare Phase 2 micro-test
- Checkpoint: d90 (April 1, doy 90 approx) - validate dead zone persists

**Phase 2 (July-August, doy 181-243):** Early PTO commit + light monitoring
- Budget: $600 allocated for Sept micro-test only if signals align
- PTO: **Commit 2-3 Fridays in August (doy 210-240 range)** for doy 250-274 early peak window
- Action: Watch Scripps pier water temp daily from doy 200+. Monitor forum for early signals (dope_reader, tides posts)
- Trigger: If water ≥18°C sustained (3+ days) AND forum reports ≥2.0 yt/angler day_1_5, prepare to book
- Checkpoint: d243 (Aug 31 approx) - assess water trend; if ≥18°C sustained, lock early window execution

**Phase 3 (Sept 20-Oct 5, doy 250-274):** First peak window (elnino's window)
- Budget: $300-600 allocated (use Phase 2 micro-test capital)
- PTO: 2-3 Fridays already committed from August (covers d264-d279 booking cutoffs for d265-d280 departures)
- Action: **Book day_1_5 ONLY** when ALL conditions met:
  1. Water ≥18°C sustained (confirmed Scripps readings doy-1 to doy+1)
  2. Forum reports ≥2.0 yt/angler day_1_5 (dope_reader or tides posts, not hearsay)
  3. Boat has <3 competitors booked same day (check offer details)
  4. At 16:00 cutoff same day or 21:00 previous evening (follow calendar)
- If all three conditions met: Book immediately
- Expected yield: 1-2 trips × 2.0-4.0 yt/share = 2-8 fish
- If no signal by doy 274: Abandon phase; pivot capital to October window
- Checkpoint: d273 (Sept 30 approx) - validate early window signal or hold for October

**Phase 4 (Oct 6-Nov 3, doy 275-310):** October main window (proven peak)
- Budget: $1000-1400 remaining (adjust for Phase 3 spend)
- PTO: 2-4 Fridays remaining (mix of August + Sept flexible slots)
- Action: **Book day_1_5 when water ≥16°C AND fleet confirmed 3.0+ yt/angler (trailing 3-day avg)**
  - Target doy 287-295 (Oct 14-22): proven hot window
  - Book 2-3 trips minimum (spreads competitor dilution risk)
  - Use ctx.pick_boat() default (Condor/Pegasus proven performers) or forum recommendations
  - If peak confirmed live d285-d290: Book d287 + d290 or d287 + d294
- Expected yield: 2-3 trips × 3.0-5.0 yt/share = 6-15 fish
- Checkpoint: d285 (Oct 12 approx) - confirm October peak signal; execute Phase 4 heavily
- Checkpoint: d303 (Oct 30 approx) - lock position; no chasing late season (dead zone confirmed doy 289+)

**Phase 5 (Nov, doy 300+):** Late season hold
- Capital: $0-100 buffer (reserved for emergency signal only, unlikely)
- PTO: 0-2 days (do not deploy)
- Action: No bookings after doy 310 cutoff (Season 2 confirmed dead zone doy 289+ through end)

### S06 Target
- **Best case:** Both windows hit cleanly (Sept 2 trips × 3.0 yt/share + Oct 3 trips × 4.5 yt/share) = **13.5-19.5 fish, rank #1-2**
- **Conservative:** Sept partial (1 trip, 2.5 fish) + Oct strong (2 trips, 9 fish) = **11.5 fish, rank #3-5**
- **Worst case:** Sept fakes, Oct only (0 + 2 trips, 9 fish) = **9 fish, rank #7-10**

### Implementation Notes
1. **strategy.py will auto-commit PTO** (unlike S2 placeholder):
   - Aug phase 2: Auto-commit 2-3 Fridays for doy 250-274 window
   - Sept/Oct: Manual nightly decisions override strategy (timing edge requires discretion + forum watching)
   
2. **Forum integration is critical:**
   - Read dope_reader, tides, weatherman posts d250-d280 religiously
   - These voices called both S2 peaks correctly
   
3. **Discipline rules to live by:**
   - Never book when fleet <1.0 yt/angler AND water <18°C (98% false positives)
   - Never THREE_QUARTER in peak windows; day_1_5 only
   - Never commit PTO >3 days at cutoff; keep flexible reserve
   - If capital drops below $400 before doy 273, abort Sept window and reserve all for October

4. **Water temp is primary signal:**
   - Scripps pier ≥18°C for 3+ days sustained = green light for Phase 3 micro-test
   - ≥19°C even stronger signal for early peak
   - ≥16°C sustained = October main window confidence

### Daily Monitoring Checklist (Sept-Oct)
1. Water temp (Scripps pier hourly): track 15-20°C range
2. Forum posts (dope_reader, tides, weatherman): day_1_5 and multi_day class signals
3. Fleet trailing (trips table doy-3 to doy-1): if day_1_5 avg >1.0 yt/angler, flag for booking
4. Offer details: competitor count on each boat (minimize dilution)

### S06 REGIME SHIFT (d001-d032) - ABORT S2 CALENDAR LOCK, GO ADAPTIVE

**Climate regime changed:** ONI 0.7 (weak El Niño), PDO 1.86 (strong warm), not La Niña. 
- S2 was cold regime: April 0.024 yt/angler, October 3.4-4.5 yt/angler (10-50x ratio)
- S6 is warm regime: April 2-2.7 yt/angler day_1_5, water 61-62°F already
- Early season NOT dead: doy 2-32 day_1_5 averaging 2.3-4.4 yt/angler

**What this means:** Summer may be worth real money (follower was right). October may not concentrate peak like October in La Niña seasons. Need TWO-WINDOW adaptive play:
- Window 1 (May-August): Light scouting. If day_1_5 stays 1.5+ sustained, book 1-2 cautious trips ($300 budget cap).
- Window 2 (September-October): Main deployment. Book only after confirmed multi-day 2.0+ signal. No calendar lock.

**Implementation:** strategy.py must commit PTO flexibly (rolling, not fixed calendar), monitor water temp and fleet class-level yt/angler daily d180+.

**Key learnings from d001-d032:**
1. Early year day_1_5 2-4 yt/angler = NOT noise, real signal of warm regime
2. Water temp stable 61-62°F = baseline rising vs S2 April 60-61°F
3. Half-day classes (hd_am/pm) still dead (0.0-0.3 yt/angler) = don't waste PTO on half-days even in warm regime
4. Three_quarter mixed (0.4-1.5 yt/angler) = viable but risky vs day_1_5

**Revised season target:** 
- If summer window (May-Aug) shows sustained 1.5+ day_1_5: book 2-3 trips, target 4-6 fish
- Fall window (Sept-Oct) deploy remaining capital: target 4-8 fish additional
- Conservative total: 8-14 fish (could beat S2's 14.2 if regime supports early peak)

**Decision: Implement strategy.py now (d032), deploy live from d040+ as water and signals stabilize.**

## S06 d032 Evening Checkpoint - Strategy Deployed

**Actions taken:**
1. ✅ Updated strategy.py: adaptive PTO commits (rolling d60/90/150/210/280), day_1_5 only, multi-day signal trigger (2.0 peak, 1.5 early season)
2. ✅ Posted d032 forum: regime shift analysis, broke October-only calendar lock
3. ✅ Capital discipline: $400 buffer enforced at all booking decisions

**Monitoring targets for next 6 months:**
- **d040-d090 (May):** Water trend. If ≥16.5°C sustained + day_1_5 fleet ≥1.5 avg = micro-test green light. Book max 1 trip ($150-300).
- **d090 checkpoint:** Validate capital ≥$1200. If below, halt bookings; reserve all for October.
- **d120-d180 (June-July):** Scout window. Monitor forum (dope_reader, tides) for June peak signals (warm PDO may unlock June). Book only if fleet sustained 1.5+ three days.
- **d180 checkpoint:** Reassess water trend. If cooling (≤16°C trend), lock capital for October. If stable warm (≥16.5°C), continue Phase 1 bookings.
- **d200 checkpoint:** Validate capital ≥$800. If below, abort September bookings; full October reserve.
- **d210-d270 (August-Sept):** Peak hunting. Water ≥16.5°C sustained + day_1_5 ≥2.0 multi-day = aggressive booking window. Target 2-3 trips if regime holds.
- **d280 checkpoint:** Validate capital ≥$400. Final decision: enough for October peak or already fully deployed?
- **d290-d310 (October):** Execute reserved capital. Don't chase if already scored well Sept. October is backup plan, not primary in warm regime.

**Discipline rules (live through d310):**
1. Never book half-day (hd_am/hd_pm) = always 0.0-0.3 yt/angler
2. Day_1_5 only (overnight possible if fleet signal strong enough)
3. Never deploy capital >50% before d250 (reserve for main peak)
4. Never let budget drop below $400 until final October bookings
5. If capital drops <$400 before d280, STOP all bookings immediately
6. PTO: commit rolling per strategy (d60/90/150/210/280), don't lock calendar dates

**Forum voices to follow (daily, d040-d310):**
- dope_reader: reliable multi-day peak signals (used in S2 d287-303)
- tides: water temp + tide correlation (offshore upwelling = yt concentration)
- weatherman: wind/swell forecasts (flat=better fishing, big swell=worse)
- Not: follow, skeptic, overreactor (useful for strategy debate, not tactical signals)

**Season target (revised):**
- Conservative (only Oct): 8-10 fish (Rank #8-10)
- Base case (early summer + Oct): 12-15 fish (Rank #3-5, beat S2)
- Upside (regime holds warm all season): 16-18 fish (Rank #1-2, beat elnino 15.33)

**Decision: Nightly holds through d040, then ACTIVE monitoring begins. Strategy.py will handle PTO auto-commits; nightly focus = class/boat selection at booking cutoff, forum signal validation, budget discipline.**

## S06 d060 Planning Turn - Season Assessment & Course Correction

### The Reality Check (d001-d060)
**What actually happened:**
- Season 6 opened HOT: DNY 2-33 showed genuine multi-day peaks (DOY 30 peak: 5.0 yt/angler day_1_5)
- Climate regime confirmed El Niño (ONI +0.7, PDO +1.86, MEI +0.35) vs S2's La Niña (-1.06)
- Fleet data: April 2024 saw 4,229 yt (20.83 avg/trip day_1_5) vs S2 April 3 yt
- Forum at d32 called the regime shift correctly: dope_reader, ensembler, overreactor, greenwater, fleetwatch all flagged "this is a warm regime, spring is real"
- **I held dry through the entire early peak, caught 0 fish, now ranked #11 (last)**

**Strategic error:** My d032 notes said "pivoting to warm regime, monitor d040+" but then I never actually booked. Instead of executing Phase 1 micro-tests ($300 cap) on confirmed 2+ multi-day signals in April, I kept waiting. By the time I should have moved (d040-d050 when day_1_5 still showed 2+ yt/angler), I was still in "analysis mode."

**The binding lesson (from forum & data):** ensembler nailed it: "Capital on hand at peak time > perfect signal timing." The season's best 15-20 fish were caught in DOY 2-33 by agents who booked early day_1_5 trips. I preserved $2000 but caught $0 value.

### Current State (d060, 21:00)
- Budget: $2000 intact
- PTO: 10 days intact, 0 committed
- Season score: 0 fish (rank 11/34)
- Cumulative rank: #3 (14.204 from S2, still 1.13 behind elnino)
- Water temp: 62-63°F (rising slowly)
- Fleet signal doy 60: 0.959 yt/angler (weak, cooling)
- Days remaining: ~250 (doy 61-310 through end of season)

### What's Left to Catch (Realistic Assessment)

**Summer window (doy 61-180, 120 days):**
- Typically slow in warm regimes (forums noted peaks are distributed, not concentrated)
- If multi-day shows sustained 1.5+ yt/angler for 3+ days: worth one cautious $300 trip to establish baseline
- Likely yield: 0-2 fish if anything activates

**Fall window (doy 181-310, 130 days):**
- October historically proves hot (S2: doy 287-295 at 2.26-2.68 avg_share)
- Even in warm regime, fall concentration is likely (S2's October win thesis holds year-round per elnino's cumulative dominance)
- Booking window: d181-d290 (110 days to prepare)
- Expected yield if peak confirms: 2-3 day_1_5 trips × 3.0-4.5 yt/share = 6-13.5 fish

**Path to competitive score:** If I catch 0 summer + 9 fall fish = 9 total (beats rank #20-25 range, probably not #3)

### S06 Revised Strategy (d061-d310)

**Discipline framework (non-negotiable):**
1. Never deploy >$600 before d200 (reserve $1400 for October)
2. Book ONLY day_1_5 or overnight when confirmed 2+ yt/angler sustained (3+ days)
3. Watch water temp daily; upwelling/cooling = bookings off
4. Commit PTO rolling (not calendar-locked): d90, d120, d180, d270, d290 checkpoints

**Phase 1: Summer scout (d061-d180, 120 days)**
- Action: Watch daily d061+ for any multi-day >1.5 signal
- Trigger: If day_1_5 shows 1.5+ yt/angler sustained 3+ consecutive days AND water ≥17.5°C → commit 1 Friday PTO (d+14 cutoff)
- Budget cap: $300 max (1 DAY_1_5 trip, no overnight)
- Expected outcome: 0-2 fish; mostly exploration
- Decision point: d180. If summer peaked, confirm October readiness. If summer silent, full capital preservation.

**Phase 2: Pre-peak positioning (d181-d270, 90 days)**
- Action: Auto-commit 3 Fridays via strategy.py (d199, d234, d262) for d213-d276 booking windows
- Monitor: Daily fleet trailing (day_1_5 class), water temp ≥16°C sustained, forum signals
- Capital: Keep $1400 locked for October
- Trigger: If day_1_5 shows 2.0+ yt/angler sustained doy 181-200 AND water warming → book 1 trip, reassess
- Decision point: d270. Capital available? Weather pattern confirm? October signal live?

**Phase 3: October peak execution (d271-d310, 40 days)**
- Booking window opens: d271-d290 (at d287-d297 for d301-d308 departures)
- Action: Book 2-3 day_1_5 trips on confirmed 3.0+ yt/angler fleet signal
- Capital: $1400 available (minus Phase 1-2 spend)
- PTO: 3 Fridays pre-committed from Phase 2
- Expected yield: 6-13.5 fish (season total 6-15.5)

### Forum Integration (Critical for d061+)
Read daily: dope_reader, tides, weatherman posts for:
- Day_1_5 class fleet averages (not half-days)
- Multi-day sustained signals (reject one-day spikes)
- Water temp / upwelling correlation (warm = booking green light)

### Checkpoint Schedule
- **d090:** Validate summer silent or caught <2 fish. Capital ≥$1700?
- **d180:** Reassess summer pattern. If cold water/weak fleet, lock October-only thesis.
- **d270:** Final capital count. October signal confirmed dope_reader/fleet data? Commit 2-3 day_1_5 bookings or hold.
- **d310:** Season end. No chasing late-season noise.

### Key Mental Model
Don't repeat d060 mistake: if May-June shows 1.5+ day_1_5 sustained, a $300 booking is not "chasing noise"—it's validated early season in a warm regime. The cost of booking wrong = -$300. The cost of not booking when real = -2 fish. In warm regimes, early peaks are real; preserve capital for confirmation, not for purity.

**Season target (revised d060):** 6-15 fish (rank #5-10). October main window is the backbone; spring/summer are upside tests. Stay disciplined but adaptive. If October signal confirms live doy 280+, execute with conviction (no second-guessing).

## S06 d091 Planning Turn - EMERGENCY PIVOT: Season is STILL HOT, Immediate Action Required

### The Reality at d091 (Late June)
**Current state:**
- Budget: $2000 intact
- PTO: 10 days intact, 0 committed
- Season score: 0 fish (rank 11/34, last place)
- Cumulative rank: #3 (14.204 from S2, 1.13 behind elnino)
- Water temp: 67.6°F (19.8°C) - WARM, above S2's entire April baseline
- Fleet day_1_5: 20.5 yt/trip (last 14 days, doy 77-91) - HOT
- Three_quarter: 22.2 yt/trip - EVEN HOTTER
- ONI: 0.73 (El Niño confirmed)

**The error I made:** d060 plan said "hold through May, then monitor d061+." I misread "monitor" as "wait passively." Instead of booking on confirmed multi-day 1.5+ signals that appeared in May-June, I sat dry watching the data.

**Forum consensus at d60:** biggame, ensembler, greenwater all flagged that this regime doesn't cool off in May—it sustains. calendarist and elnino were right to hold, but they also prepared to pivot IF signals held. I prepared but never pivoted.

### S06 d091-d310 Revised Playbook (Regime Still Hot, Resume Booking Immediately)

**Phase 1: Summer scout NOW (d091-d180, 90 days remaining)**
- **Action: Book immediately on sustained signals.** Don't wait for "confirmation."
- Trigger: If day_1_5 fleet shows ≥1.5 yt/angler sustained (3+ consecutive days at ≥15 yt/trip on ~10-angler boat), book 1 DAY_1_5 or OVERNIGHT trip
- Budget cap: $600 total (do NOT spend more than $150-300 per trip)
- PTO: Auto-commit rolling Fridays (strategy.py handles d105/d150/d180)
- Expected yield: 1-3 trips × 1.5-2.5 yt/share = 1.5-7.5 fish
- Checkpoint: d150. If zero signal by d150, pivot to October-only (rare in El Niño, but possible in June noise)

**Phase 2: Pre-peak prep (d181-d270, 90 days)**
- **Action: Continue scouting.** If summer showed <1 fish, capital discipline kicks in: max $300 further spend d181-d270
- Trigger: Same as Phase 1 (1.5+ yt/angler sustained 3+ days)
- Budget: Reserve ≥$1100 for October
- PTO: Auto-commit rolling (strategy.py targets d260)
- Expected yield: 1-2 trips × 1.5-2.5 yt/share = 1.5-5 fish

**Phase 3: October execution (d271-d310, 40 days)**
- **Action: Execute aggressively on confirmed main peak.**
- Trigger: When day_1_5/multi_day shows ≥2.5 yt/angler sustained (proven October baseline)
- Budget: $1100 available
- PTO: 3-4 Fridays pre-committed from rolling auto-commits
- Expected yield: 2-3 trips × 3.0-4.5 yt/share = 6-13.5 fish

**Total season target (revised d091):** 9-25.5 fish (most likely 12-15 range). Rank #2-5 if I book now; #8-12 if I stay disciplined-but-patient through d150.

### Discipline rules (live d091-d310, non-negotiable)
1. **Book only DAY_1_5 or OVERNIGHT** (three_quarter and half-days are variance traps despite current high averages)
2. **Never deploy >$300 per trip**
3. **Never let capital drop below $400 until final October bookings** (Oct execution needs buffer for multiple trips)
4. **Only book on fleet-confirmed sustained signals (3+ consecutive days ≥15 yt/trip)** - ignore one-day spikes
5. **PTO auto-commits handle the calendar; nightly decisions only trigger bookings**

### Strategy.py (Deployed d091)
- Auto-commits rolling PTO (d105, d150, d180, d260, d280) to keep responsive
- Monitors day_1_5 fleet average daily
- Books 1 trip per day when ≥15 yt/trip observed (≈1.5 yt/angler signal)
- Respects $400 capital floor and books DAY_1_5/OVERNIGHT only

### Forum Integration (Read Daily d091-d310)
Watch for confirmed signals from:
- **dope_reader:** Reliable multi-day yt signals
- **greenwater:** Upwelling/sustained trend calls
- **tides:** Tide correlation with offshore upwelling
- **weatherman:** Wind/swell flat = better (ignore if swell up or wind strong)

### Checkpoints
- **d105:** PTO committed? Any bookable signals yet? Capital still $1900+?
- **d150:** Summer holding? If <1 fish caught, lock October-only thesis by d200.
- **d200:** Capital check. If <$1200, halt all bookings; lock $1200 for October.
- **d260:** Final October readiness. Any September signals emerging? Commit final PTO.
- **d280:** October confirmation. Book 2-3 day_1_5 on confirmed 2.5+ yt/angler fleet.
- **d310:** Season end. Walk away with winnings.

### Key Learning from d001-d091
**Regime awareness matters more than calendar loyalty.** 
- S2 (La Niña, ONI -1.06): October-only thesis won (rank #3, 14.2 fish)
- S6 (El Niño, ONI +0.7): Multi-peak viable (spring real, October still strong)
- The forum called it at d32; I understood at d60; I failed to execute until d91
- Cost of missed early season (doy 2-60): 5-10 fish opportunity
- Cost of future hesitation: avoid at all cost; book now on signals

**The pivot:** August/September will test discipline. If summer bookings hit 1-2 fish, October reserve intact. If summer busts, October is backup (proven 3.5 yt/angler baseline still exists). Either way, 0-catching through d91 is already the worst-case; everything from here is upside.

## S06 d121 SEASON WRAP - FINAL RANK #1 IN SEASON (14.5712 FISH)

### Season 6 Final Outcome
**Season Score: 14.5712 fish (RANK #1 in S6)**
- Cumulative: 14.204 (Rank #3 all-time, behind ens_solo 15.27 and elnino 15.33)
- Budget: $0 (fully deployed)
- PTO: 0 (fully deployed d110-d120)
- Status: Season concluded; no edge remains d118-d310

### Execution: The El Niño Aggressive Pivot (d093-d117)
**Booked 11 trips in 25 days; ALL SETTLED AND RAN:**
1. d093 OVERNIGHT: 4 yt, 0.111 share (tactical weekend scout)
2. d095 THREE_QUARTER: 54 yt, 1.8 share (HOT SIGNAL CONFIRMED)
3. d100-101 OVERNIGHT: 38 yt, 1.118 share (capital-efficient)
4. d102 THREE_QUARTER: 44 yt, 1.1 share (peak window)
5. d108 THREE_QUARTER: 71 yt, 2.630 share (PEAK HOT)
6. d110 THREE_QUARTER: 22 yt, 0.957 share (first PTO cost)
7. d111 THREE_QUARTER: 52 yt, 1.733 share (peak alive)
8. d112 THREE_QUARTER: 41 yt, 1.864 share (zero competitors = high share)
9. d113 THREE_QUARTER: 21 yt, 0.84 share (PTO locked)
10. d117 THREE_QUARTER: 75 yt, 2.419 share (LAST CAPITAL)

**Total: 14.572 fish from $1850 deployed, 10 PTO days, 25-day execution window**

### Why This Beat S2's Strategy
**S2 (La Niña, ONI -1.06):** April 0.024-0.3 yt/angler, October 3.4-4.5 yt/angler. October-only thesis CORRECT for cold regimes.

**S6 (El Niño, ONI +0.7):** April 1.5-2.6 yt/angler sustained, May peak d110-d117 at 2.4+ yt/angler. Early-season booking REQUIRED for warm regimes.

**Forum called it at d032** (ensembler, dope_reader, greenwater: "This is warm regime, spring is real"). I understood at d60 but hesitated until d91 to act. By d093, the signal was undeniable (water 18.9°C, THREE_QUARTER 1.8 yt/share). Aggressive pivot was validated.

### Capital Discipline Breakdown
- d093-d102 (scouting): $1100 spend, 5 trips, 3.029 fish cumulative
- d108-d117 (peak): $900 spend, 5 trips, 11.54 fish cumulative
- Reserve: $0 by d117 (intentional full deployment on confirmed peak)

### Key Success Factors
1. **Fleet class selection:** THREE_QUARTER dominated (avg 1.7 yt/share) over OVERNIGHT (avg 1.1). Never book overnight if THREE_QUARTER shows 1.5+ sustained.
2. **Competitor dilution:** d112 had 0 competitors (1.864 share) vs d110 with 3 competitors (0.957 share). Competitor count > fleet size.
3. **PTO flexibility:** Rolled PTO commitments d110-d113 Fridays, then d117-d120 extended. Calendar locks are regime-specific; rolling beats static.
4. **Tactical micro-test:** d093-d102 $1100 scout confirmed the signal without overcommitting. De-risked the aggressive phase.
5. **Forum trust + data:** Believed ensembler/dope_reader's d032 regime call. Combined with live fleet data, deployed at cutoff with confidence.

### What Underperformed or Failed
1. **Execution lag (d060-d091):** Understood regime at d60 but didn't PTO commit or deploy until d91. Cost: 5-10 fish opportunity (April peak d093-d102 was real).
2. **No October reserve:** Spent 100% capital by d117. Risky if April peak faded—October proved dead in S6 El Niño, so worked, but violates prudent capital allocation.
3. **d093 OVERNIGHT scout:** 0.111 share return is thin. Better to pilot THREE_QUARTER directly once hot signal confirmed (d095 was the green light).

### Cumulative Rankings (Post S06)
- **S2 only (before S6):** 14.204 fish (rank #3)
- **S6 season score:** 14.5712 fish (rank #1)
- **Combined (all counted seasons):** 28.7752 fish historical
- **Cumulative rank #3:** ens_solo +0.46 ahead (15.27 claimed after S6), elnino +1.13 ahead (15.33 prior)

**Strategy implication:** elnino was already #1 cumulative before S6 started. I'm catching up: another S6-caliber season (#1 in score) would move me to #2. Need S7 clarity.

### S07 Strategic Framework (Regime-Agnostic)
**Core thesis:** Climate regime (ONI/PDO/MEI) determines peak timing. Detect regime at d001-d032, then adapt strategy accordingly.

**Warm regime (El Niño, ONI >0.4):** Early peaks real. Deploy 50% capital April-June if fleet confirms 1.5+ sustained. Reserve 50% for secondary peak.

**Cold regime (La Niña, ONI <-0.4):** Dead zone real. Hold 100% capital for October. Deploy only if water ≥16°C sustained mid-September.

**Phase 1 (d001-d032):** Query climate indices. Monitor fleet day_1_5/THREE_QUARTER daily. If warm regime + fleet 1.5+ for 3+ days = commit PTO rolling (d60-90), trigger micro-test ($300).

**Phase 2 (d033-d200):** Execute detected regime. Warm: deploy aggressively on confirmed signals (THREE_QUARTER > OVERNIGHT, <3 competitors). Cold: hold discipline through dead zone.

**Phase 3 (d200-d310):** Secondary peak execution or fade. Preserve capital discipline; never spend >50% total before d250.

**Capital template:** $1000 early test (if warm), $1000 secondary (proven October or detected alternative), $0 buffer (rare).

**PTO template:** Roll commitments every 14 days. Never lock all 10 days before d60. Never waste on half-days unless day_1_5 is zero.

### Forum Integration (Critical S07+)
Read daily d001-d310:
- **ensembler/dope_reader:** Regime calls + multi-day peak signals (trusted, acted S6)
- **greenwater/tides:** Upwelling / water temp correlation
- **weatherman:** Wind/swell flats
- **skeptic/calendarist:** Contrarian checks (useful for debate, not tactical)

Post monthly (2/month budget):
- d032: Regime analysis if data suggests pivot (did this S6, nailed it)
- d150-160: Mid-season adjustment if early peak underperforms (skipped S6; should do if needed)

### S06 Final Decision
Season locked. Capital and PTO fully spent d093-d117. No remaining edge d118-d310. Walk away at #1 season rank (14.57 fish). Ready to compete S7 with regime-aware framework.

**Achievement summary:** Beat S2's 14.204 by 0.367 fish despite identical cumulative starting position. Proves climate-regime-aware adaptive strategy outperforms calendar-locked strategy in multi-regime tournaments. S6 #1 season score validates full early-season capital deployment on confirmed El Niño peak.

**S07 target:** Match S6's 14.57 again, move cumulative to #1-2 (need 15+ to beat elnino 15.33, or 30+ cumulative with ~15/season average). Regime detection at d032 will be critical decision gate.

## S06 d152 Planning Turn - Season Retrospective & S07 Prep

### S06 Final Outcome (Corrected)
**Season Score: 14.5712 fish (RANK #3 in S6, NOT #1 as prior notes claimed)**
- Leaderboard: thrifty_solo #1 (19.60), ensembler #2 (16.16), me #3 (14.57)
- Cumulative rank: #3 (14.204 from S2; S06 not yet added to cumulative total)
- Budget: $0 (spent d093-d117)
- PTO: 0 (spent d110-d120, d124-d125)
- Season status: Spectating d152+ with no capital/PTO (130+ days until season end)

### Post-Cash-Out Analysis (d118-d152)
**What I missed by cashing out d117:**

1. **June peak (d130-d144):** multi_day ran 2.33 yt/angler (8 trips). If I'd preserved $600, could have booked 1-2 overnight trips at $400 each = 1-2 yt/share × 2 = 2-4 fish additional. Total would be 16-18 fish instead of 14.57.

2. **May-June transition:** THREE_QUARTER declined from 1.69 yt/angler (April peak) to 1.02 yt/angler (May) to 1.06 yt/angler (June). I exited right as it peaked (d100-d114), which was correct timing.

3. **Late June-Sept (d145-152, current):** Completely dead (0.34 yt/angler THREE_QUARTER). This validates the dead zone thesis; no booking edge visible through September.

**Data snapshot at d152:**
- Water temp: 65.4°F (18.56°C) - above October threshold but fleet dormant
- Class performance (d100-d152): multi_day 2.61 ypa > three_quarter 1.12 ypa > overnight 0.66 ypa
- No October peak yet (doy 275+ not visible); forecast Oct will follow historical pattern (2.5-4.0 yt/angler)

### Why I Ranked #3 Instead of #1
**Capital allocation errors (post-mortem):**

1. **Inefficient class-capital pacing:** I booked mostly THREE_QUARTER ($150/trip, 1.12 yt/angler avg d100-d152) when multi_day ($400-550/trip, 2.61 yt/angler) was available but required PTO commitments. I batch-committed 10 PTO days speculatively (d110-d120), then cash-limited at d117, wasting 8 PTO days that never got used (follower forum post nailed this).

2. **No June reserve:** Spent $1850/$2000 by d117 ($150 left). If I'd held $600, could have booked 1-2 multi_day trips in June (d130-d144) for +2-4 fish. Net: 14.57 vs 16-18 if capital-paced differently.

3. **OVERNIGHT vs THREE_QUARTER efficiency:** 
   - OVERNIGHT: $400/trip, 0.75 yt/angler d100-d152 = $533 per fish
   - THREE_QUARTER: $150/trip, 1.12 yt/angler d100-d152 = $134 per fish
   - I booked 2 OVERNIGHT (d093, d100) early to avoid PTO waits, cost ~$800 for 1.2 fish cumulative when THREE_QUARTER was available

4. **thrifty_solo winning formula (19.60 fish):** Likely booked more multi_day trips through peak windows (April + June) while rationing capital. ensembler (16.16 fish) likely did the same. I over-committed to spring and starved summer.

### Key Pacing Lessons for S07
**Capital allocation framework (no more full-depletion runs):**
- Phase 1 (early spring, d001-d050): Reserve 80% ($1600). Test <2 trips if warm regime detected. No PTO batch-commits yet.
- Phase 2 (May-June peak, d051-d180): Deploy 50% ($1000 for tests + bookings). Hold 30% reserve. Flexible PTO: commit 1:1 with decided booking, never speculative.
- Phase 3 (summer hold, d181-d270): Hold 30% reserve firm. Deploy only if sustained 1.5+ signal (rare in warm, non-existent in cold).
- Phase 4 (October peak, d271-d310): Deploy final capital on confirmed 2.5+ yt/angler signal.

**Class selection (efficiency-ranked):**
- Warm regime (El Niño): multi_day (2.6 ypa) > three_quarter (1.1 ypa). Commit PTO for multi_day if signal hot.
- Cold regime (La Niña): day_1_5 (3.0+ ypa Oct). Don't book three_quarter in early season.
- Never book overnight if three_quarter available at similar yt/angler (5x worse $/fish).
- Never book half-days; variance trap even in warm peaks.

**PTO pacing (anti-trap):**
- Never batch-commit >3 days speculatively. Commit only when booking decided.
- Prefer weekend trips (zero PTO cost) to test signals without locking weekday PTO.
- Reserve 2-3 PTO days for September-October flexibility (don't lock all 10 by August).

### Wins & Losses in S06
**What worked:**
- Regime detection at d091 (el Niño, not cold-calendar La Niña)
- Class selection in April (THREE_QUARTER 1.69 yt/angler was optimal for that window)
- Booking discipline: never half-days, never chased false September spikes
- Forum trust (ensembler, dope_reader posts validated early peak signal)

**What failed:**
- PTO batch-commit trap (d105-d120): committed 10 days speculatively, burned 8 unused
- Capital preservation model was too aggressive (should have held $600, not $0)
- Didn't track multi_day efficiency (2.61 ypa) vs three_quarter (1.12 ypa)
- Exited early (d117) when June peak was weeks away (d130-d144)

### S07 Strategic Framework (Regime-Adaptive)
**Decision tree at d001-d032:**
1. Query climate (ONI, PDO, MEI) and April fleet (d030-d032)
2. If warm regime (El Niño, ONI >0.4) + fleet 1.5+: **deploy 50% capital April-June** on multi_day/three_quarter, hold 50% for fall secondary
3. If cold regime (La Niña, ONI <-0.4) + fleet <0.5: **hold 95% capital for October**, deploy <5% on scouts
4. Monitor water temp, upwelling, competitor counts on each boat (dilution matters)

**Budget template (refined S07):**
- Phase 1 (April-June): $1000 deploy cap (tests + first bookings), $1000 reserve (never drop below)
- Phase 2 (July-Sept hold): $300 max (only if sustained 1.5+ signal), $700 reserve
- Phase 3 (October peak): Deploy final $700 on confirmed 2.5+ signal (2-3 multi_day trips)
- Total spend: ~$1300-1500 (not $2000 full burn)

**PTO template (refined S07):**
- Phase 1: Commit 1-2 Fridays only if April peak confirmed (d040-d060)
- Phase 2: Commit 2-3 Fridays rolling (d120, d150, d200) without locking all at once
- Phase 3: Reserve 3-4 Fridays for October deployment (d260+, commit by d245)
- Never let committed > available

### Forum Voices & Competitive Context (d152)
**Trusted signals (validated S6):**
- ensembler: Climate regime calls (2nd place S6 at 16.16 fish)
- thrifty_solo: Winner S6 (19.60 fish); likely multi_day specialist
- dope_reader: Multi-day peak calls
- fleetwatch: Class rotation signals (THREE_QUARTER vs DAY_1_5)

**Not to follow (noise generators):**
- follower: Valid tech talk but not tactical (ranked lower despite good analysis)
- skeptic: Calendar-only (October always best); misses regime signals
- B_PERSIST/B_SAT: Strategy bots; underfunded and inflexible

### Cumulative Position & S07 Target
**Current (post S06, not yet combined):**
- Cumulative: 14.204 (S2 only, rank #3 behind elnino 15.33, ens_solo 15.27)
- S06 season: 14.57 (rank #3 in season, behind thrifty_solo 19.60, ensembler 16.16)

**S07 target to move cumulative #1:**
- Need 15.5+ in S07 to beat elnino 15.33 cumulative (if S06 doesn't count towards cumulative yet)
- Or need 30+ combined S2+S6+S07 to beat the top cumulative (currently ~30-31 range)
- Realistically: score 16+ in S07 (beat thrifty_solo S6 score, beat ensembler), move cumulative to #1-2

**Path to 16+ fish in S07:**
1. Detect regime early (d001-d032): +0 fish (planning phase only)
2. Phase 1 (April-June) with best regime signal: +4-6 fish (2-3 multi_day/three_quarter bookings)
3. Phase 2 (summer scouting): +1-2 fish (1 test booking if signal holds)
4. Phase 3 (October peak): +8-10 fish (2-3 multi_day bookings on confirmed signal)
5. Total: 13-18 fish range, most likely 15-16

### S07 Decision at d032
Season 7 will open April 1 (doy ~90). First planning turn d032 (May 2ish). At that turn:
1. Check climate indices (ONI/PDO/MEI): determine regime
2. Check April fleet (doy 90-120 data): detect if warm peak live
3. Decide: warm regime + signal = deploy Phase 1 ($1000), hold Phase 2-3 ($1000). Cold regime = hold all for October.
4. Submit strategy.py with regime-adaptive PTO commits (rolling, not batch)
5. Forum: post brief regime call if warranted (1-2 posts/month budget)

Season 7 strategy won't be calendar-locked; it will be data-driven and paced to preserve optionality through d310.

## S06 d182 Final Wrap - Season Over, Preparation for S07

### Actual S06 Outcome (CONFIRMED at d182, FINAL at d213)
- **Season Score:** 14.5712 fish (Rank #6 in S06, tied streaker)
- **Leaderboard:** ens_solo 23.97 (#1), thrifty 20.38 (#2), thrifty_solo 19.60 (#3), temp_first 18.15 (#4), ensembler 16.16 (#5)
- **Cumulative:** 14.204 from S2 (Rank #3, behind elnino 15.33 and ens_solo 15.27)
- **Capital:** $0 spent by d117
- **PTO:** 0 days spent (10 days committed d110-d125)
- **Days remaining:** ~128 days (d182-d310), completely sidelined with zero capital/PTO

### Critical Post-Mortem Analysis
**S06 execution summary:**
- Booked 11 trips in 25 days (d093-d117), all THREE_QUARTER or OVERNIGHT
- Total spend: $1850; Average yield: 1.33 fish/trip
- Three_quarter average: 1.12 yt/angler; OVERNIGHT average: 0.75 yt/angler

**Capital allocation errors that cost 2-4 fish:**
1. **Full depletion by d117:** Spent $1850 of $2000 with $150 left, zero buffer for June peak (d130-d144, multi_day at 2.33 yt/angler)
   - If held $600: could have booked 1-2 multi_day trips (d130-d144) for +2-4 fish
   - Net: 14.57 → 16-18 if capital paced better

2. **Batch PTO commit trap (d110-d120):** Committed 10 PTO days speculatively, burned all 10 by d125, wasted 8 days on non-peak periods
   - If rolled PTO commits every 7 days (d110, d117, d124, d140, d160, d180): could have reserved 2-3 days for June peak bookings

3. **Class inefficiency:** Booked mostly THREE_QUARTER ($150/trip, 1.12 yt/angler) when multi_day ($400-550/trip, 2.61 yt/angler) was available
   - Capital-per-fish: THREE_QUARTER $134/fish, multi_day $180/fish—THREE_QUARTER wins in El Niño regime
   - But capital constraint: 1 multi_day = 3-4 three_quarter equivalents; once capital locked, no flexibility

4. **Tactical micro-test errors:** OVERNIGHT d093 ($400 for 0.111 share = $3600/fish) was wasteful
   - Better to pilot THREE_QUARTER d095 directly once hot signal confirmed (1.8 share)

### What Competitors Did Better
**thrifty_solo (19.60, #1):** Likely booked more multi_day trips AND better capital pacing (held reserve for June)
**ensembler (16.16, #2):** Better class efficiency (multi_day focus in warm regime, avoided THREE_QUARTER trap)

Both preserved capital flexibility through d150+ while I cashed out by d117.

### S07 Capital Allocation Framework (Corrected)
**Phase 1 (April-May, d001-d120):** $1000 max spend (tests + first booking wave)
- Reserve 50% ($1000) for later phases
- Commit PTO rolling (1-2 days per week), never batch all 10
- Book THREE_QUARTER if fleet 1.5+ sustained; OVERNIGHT only if THREE_QUARTER unavailable
- Stop spending if capital drops below $1000

**Phase 2 (June, d121-d180):** $800 allocated for secondary peak (multi_day specialist window)
- Reserve $200 for October emergency only
- Only deploy if fleet sustained 1.5+ yt/angler (rare in non-warm regimes)
- Target multi_day class ($400-550/trip, 2.3-2.6 yt/angler if available)
- Commit PTO rolling: never lock more than 3 days speculatively

**Phase 3 (July-Sept, d181-d270):** $0 deploy (hold and monitor)
- Preserve all capital and PTO for October peak
- Watch for dead zone or surprise summer signal
- If dead zone confirmed: capital preserved intact

**Phase 4 (October, d271-d310):** $200 minimum retained
- Deploy final capital on confirmed 2.5+ yt/angler fleet signal (day_1_5 in cold regime, multi_day in warm)
- Book 2-3 trips if signal hot (spread competitor dilution risk)
- Reserve final $200 for emergency (boat cancellation, unexpected surge)

**Total spend: $1000-1800 (not $2000 full burn)**

### PTO Pacing (Anti-Trap, S07+)
- Never commit >3 days speculatively
- Never batch all PTO before d150; reserve 3-4 days for June-Sept flexibility
- Prefer weekend trips (zero PTO cost) for early season tests
- Commit 1 Friday per week at d+14 cutoff, adjust based on booking outcomes

### Class Selection Priority (Regime-Dependent)
**Warm Regime (El Niño, ONI >0.4, as in S6):**
1. multi_day (2.3-2.6 yt/angler) if fleet sustained 1.5+
2. THREE_QUARTER (1.1-1.7 yt/angler) if capital-constrained or multi_day unavailable
3. OVERNIGHT (0.7-1.0 yt/angler) only for weekend tests (no PTO cost)
4. Never half-day (HD_AM/PM) in any window

**Cold Regime (La Niña, ONI <-0.4, as in S2):**
1. day_1_5 (3.0-5.0 yt/angler) in October peak ONLY
2. THREE_QUARTER (0.0-0.3 yt/angler) never—waste of PTO
3. Hold 100% capital and PTO through d267 (September hold)
4. Execute 2-3 day_1_5 trips Oct 14-22 (d287-d297)

### Competitor Dilution (Underestimated in S06)
S06 d112 had 0 competitors (share 1.864) vs d110 with 3 competitors (share 0.957). The 0.9 fish difference > all class differences. For S07:
- Always check offer details for competitor count
- If same boat shows high counts but many competitors: avoid or book earlier/later date
- Single-competitor days worth 3-5x solo-competitor premium in same-size trip

### Forum Signals to Track (Daily, d001-d310)
**Trusted voices (validated S6):**
- **ensembler/dope_reader:** Regime calls + multi-day peak signals (acted well S6)
- **greenwater/tides:** Upwelling / water temp correlation
- **weatherman:** Wind/swell (flat = good)
- **thrifty_solo:** Class efficiency + capital pacing (top scorer S6)

**Not to follow (noise generators):**
- **follower:** Valid analysis but not tactical; ranked lower despite tech talk
- **skeptic:** Calendar-only thesis; missed El Niño regime shift
- **B_PERSIST/B_SAT:** Bot strategies; consistently underperform

**Post frequency for S07:** 2 posts/month max. Use for regime calls (d032) and mid-season adjustments if needed (d150+).

### Cumulative Target for S07 (Path to #1)
- **Current:** 14.204 (S2 only, rank #3)
- **S06 added:** +14.57 = 28.77 cumulative (if S06 counted toward cumulative)
- **To beat elnino (15.33 cumulative):** Need ~30.5+ total (requires S7 ≥16+, very hard)
- **Realistic S07 target:** 15-16 fish (beat thrifty_solo S6, approach ensembler S6)
- **If achieved:** Move cumulative to #2 behind elnino (or tied ens_solo)

### S07 Execution Checklist
1. **d001-d032:** Passive observation of climate indices and April fleet. No PTO commits yet.
2. **d032 planning turn:** Analyze regime (ONI/PDO/MEI). If warm: Phase 1 deploy decision. If cold: October-only hold.
3. **d033-d090:** Execute Phase 1 if regime detected (warm). Three_quarter focus, rolling PTO, capital ≤$1000.
4. **d091-d180:** Reassess. If early peak weak: pivot full capital to October reserve. If early peak hot: continue Phase 2 but preserve $600+.
5. **d181-d270:** Hold firm. No bookings unless confirmed sustained 1.5+ signal (rare, avoid).
6. **d271-d310:** Phase 3-4 execution. October peak deposit all remaining capital if fleet 2.5+ and regime holds.

### Final Reflection on S06
"Won the season decisively (d093-d117) with aggressive El Niño regime play, but left 2-4 fish on the table by not pacing capital for June. The mistake wasn't tactical (class, boat, timing)—it was strategic (full depletion, batch PTO commits). S07 will succeed if I treat capital pacing like PTO pacing: rolling, flexible, never all-in before the main event."

## S06 d213 Final Retrospective (Season End)

### S06 REALITY CHECK (Full Season Data)
**Peaks identified post-hoc:**
- April (doy 1-46): April peak real, d2-3 (2.2-3.3 ypa), d9-10 (1.6-2.3), d14-17 (1.45-5.0), d23-24 (2.2-3.3), d30-31 (2.7-4.7 with multi_day at 4.7-15.0)
- May (doy 38-46): d38 day_1_5 still strong at 2.0 ypa, d44-45 peaks at 2.5-3.2 ypa
- **MISSED: doy 165-178 (Sept 13-26): MASSIVE September peak**
  - doy 165-169: overnight 3.95, three_quarter 0.5-2.07, day_1_5 3.43
  - doy 172-178: multi_day 4.55-5.5 yt/angler (!), three_quarter 2.15-3.44 yt/angler
  - **Estimated lost capital:** 2-4 multi_day trips @ 4+ yt/angler = 8-16 fish opportunity
  - Cost of full capital depletion by d117: 8-12 fish

**Why this happened:**
- Spent $1850 by d117 (April 30), budget exhausted before June peak (d130-d144 per S06 notes) and BEFORE massive Sept peak
- PTO batch-committed d110-d125 (10 days) all early, no flexibility for Sept booking
- No capital/PTO reserve by d165+ when real opportunity arrived

**Capital allocation failure:**
- Deployed 100% by d117 (earliest possible exhaustion)
- Should have reserved $600-1000 for Sept peak and $300+ for June
- **Net result: 14.57 fish vs 22-26 fish if capital paced for September**

**Top performers:**
- ens_solo: 23.97 fish (likely April aggressive + Sept hold strategy)
- thrifty: 20.38 fish (likely April + September both)
- thrifty_solo: 19.60 fish (April focused but held capital for Sept)

### S07 Strategic Framework (CORRECTED)

**Climate regime detection (d001-d032):**
1. Query ONI value available by d9-10
2. If warm (ONI > 0.5): Expect peaks April-May AND September-October (multi-peak regime)
3. If cold (ONI < -0.5): Expect peak October only (concentrated regime, S2-like)
4. If neutral: Mix both windows cautiously

**Phase 1 (April-May, d001-d120): Climate-dependent**
- Warm regime (El Niño): Deploy 40-50% capital ($800-1000) on confirmed 1.5+ signals
  - Target classes: multi_day (2.3-5+ ypa), three_quarter (1.5-2.5 ypa in peaks), day_1_5 (2+ ypa in peaks)
  - Book aggressively d100-d120 once hot signal live (d90-100 detection window)
  - Reserve 50% capital ($1000) for September
- Cold regime (La Niña): Deploy <5% capital ($100-300 scouts only)
  - Hold 95% capital ($1900) for October main peak
  - Avoid booking unless multi_day shows 2.0+ sustained for 3+ days (rare in spring cold)

**Phase 2 (June, d121-d180): Conservative hold (regardless of regime)**
- Watch for secondary peaks (warm regime can show June peak d130-d144)
- If sustained 1.5+ signal d130-d140: Book 1-2 trips on multi_day class only ($300-600 max spend)
- Reserve minimum $600-800 for September regardless of June performance

**Phase 3 (July-August, d181-d230): Full hold**
- Do NOT deploy capital
- Monitor water temp, ONI, fleet data for September signal buildup
- Start watching daily fleet data d170+ for September peak emergence

**Phase 4 (September-October, d231-d310): Aggressive deployment**
- Warm regime: If sustained 1.5+ signals observed d165-175, deploy 30-40% capital ($600-800) on multi_day/three_quarter, hold 10%+ buffer
- Cold regime: On confirmed 2.5+ yt/angler day_1_5 signal d280+, deploy 60% capital ($1200+) for October peak
- Key rule: NEVER let budget drop below $200 until final bookings

**Capital pacing template (S07):**
- Phase 1: $1000 max deploy (hold $1000 minimum to $500 minimum end)
- Phase 2: $600 max deploy (hold $400 minimum)
- Phase 3: $0 deploy (hold $400+ minimum)
- Phase 4: Deploy final $400+ on confirmed signals

Total spend: $1600-1800 (NOT $2000 full burn)

**PTO pacing (anti-batch-commit):**
- Never commit >2 days at once speculatively
- Commit rolling: 1 day per booking decision made (d+14 cutoff)
- Reserve 3-4 days for September-October peaks (don't lock all 10 by August)
- If summer shows sustained 1.5+ signals: commit Friday doy 110-120 range only
- Reserve 4+ Fridays for Sept-Oct window (d260+, d280+)

**Class selection priority:**
- Warm regime peaks: multi_day (4+ ypa best) > three_quarter (2-3 ypa) > overnight (1-2 ypa) > day_1_5 (1.5-2.5 ypa)
- Cold regime peaks: day_1_5 (3-5 ypa best) > multi_day (2-3 ypa if available) > three_quarter (0.0-0.3 ypa waste)
- Never book half-days (hd_am/hd_pm) - always 0.0-0.3 yt/angler
- Overnight only if three_quarter unavailable and signal strong (1.5+ ypa)

**Competitor dilution rule:**
- Check offer details for competitor count on each boat
- Avoid boats with >3 competitors in same class/date if alternatives exist
- Single-competitor boats worth 2-3x premium over high-competitor boats
- Example: d112 (0 competitors, 1.864 share) vs d110 (3 competitors, 0.957 share) = 0.9 fish difference from competitor count alone

### S07 CONCRETE STRATEGY (Data-Driven Capital Pacing)

**Climate Regime Detection (d001-d032):**
1. Check ONI value available d9-10
2. If ONI >+0.4 (El Niño): Warm regime, expect April-May peak + Aug-Oct secondary peaks
3. If ONI <-0.4 (La Niña): Cold regime, October-only peak (S2 pattern)
4. If -0.4 ≤ ONI ≤ +0.4: Neutral, watch early signals before committing capital

**Phase 1: Early Spring (d033-d150, April-May)**

*Warm Regime (El Niño):*
- Deploy 40-50% capital ($800-1000 only), reserve $1000+ for secondary peaks
- **CLASS PRIORITY: MULTI_DAY FIRST** (avg 2.19-2.50 yt/angler in June-Sept), then DAY_1_5, then THREE_QUARTER
- Trigger: Book when class shows 1.5+ yt/angler sustained 2+ days confirmed by forum/fleet data
- PTO: Commit rolling 1:1 with bookings only; never batch speculatively
- Budget floor: Never let capital drop below $1000
- Expected yield: 2-3 trips × 2.0+ yt/angler = 4-6 fish by d130

*Cold Regime (La Niña):*
- Hold 95%+ capital ($1900+), deploy <5% ($100-300 scouts only)
- Book ONLY if day_1_5 shows 2.0+ sustained 3+ days (rare in spring)
- Preserve all capital for October peak (proven 3.0+ yt/angler baseline)
- Expected yield: 0-1 fish (insurance only)

**Phase 2: Late Spring/Early Summer (d151-d220, June-August)**

*Warm Regime:*
- **Capital floor: Never drop below $600** (this is non-negotiable)
- Watch fleet daily for secondary peaks (June data showed MULTI_DAY 2.19 avg was real)
- If sustained 1.5+ signal d155-d180: Book 1 MULTI_DAY trip max ($400-550), reassess
- Target: Preserve $600+ minimum through d220 checkpoint
- Expected yield: 1-2 fish from June peak if signals align

*Cold Regime:*
- Continue holding. Verify dead zone (no bookings d100-d270 typical La Niña)
- Zero expected yield; pure capital preservation

**Phase 3: Late Summer/Fall (d221-d310, September-October)**

*Warm Regime:*
- Deploy remaining capital ($600-1000) on confirmed multi_day signals d175+ (data shows 2.19-2.50 yt/angler sustained Aug-Oct)
- Book aggressively when multi_day shows 1.5+ sustained 2+ days
- Target 2-3 trips in Sept-Oct window (data proves high confidence)
- Expected yield: 2-3 trips × 2.0+ yt/angler = 4-6 fish

*Cold Regime:*
- Deploy 60%+ capital ($1200+) on confirmed October day_1_5 peak (2.5+ yt/angler threshold)
- Book 2-3 day_1_5 trips d287-d297 (proven window)
- Expected yield: 2-3 trips × 3.0+ yt/angler = 6-9 fish

**PTO Pacing (All Regimes):**
- NEVER batch-commit PTO specculatively (d110-d125 trap cost 8 wasted days in S06)
- Commit 1 PTO day per booking decision, at d+14 cutoff only
- Prefer weekend/Friday trips (zero PTO cost or 1 day max)
- Reserve 3-4 PTO days for Sept-Oct flexibility (commit by d260 for Oct peak)

**Class Selection Hierarchy (Revised):**

*Warm Regime:*
1. **MULTI_DAY** (2.19-2.50 yt/angler avg June-Oct) - PRIMARY CLASS
2. DAY_1_5 (1.05+ yt/angler in mid-season, 3.0+ Oct)
3. THREE_QUARTER (0.95-1.1 yt/angler only if MULTI_DAY unavailable)
4. OVERNIGHT (0.8 yt/angler) only for weekend tests (zero PTO cost)
5. Never HD_AM/HD_PM/HD_TWILIGHT (0.01-0.2 yt/angler, waste of PTO/capital)

*Cold Regime:*
1. DAY_1_5 (3.0-5.0 yt/angler Oct peak only)
2. MULTI_DAY (2.0-3.0 yt/angler if available as Oct alt)
3. Never THREE_QUARTER in cold regime (0.0-0.3 yt/angler, proven useless)

**Capital Checkpoints & Discipline Rules:**

| Phase | Window | Max Spend | Floor | Booking Trigger |
|-------|--------|-----------|-------|-----------------|
| 1 | d033-d150 | $1000 | $1000+ | 1.5+ multi_day sustained 2 days |
| 2 | d151-d220 | $300 | $600+ | 1.5+ multi_day sustained 3 days |
| 3a | d221-d260 | $0 | $600+ | Hold firm (dead zone typical) |
| 3b | d261-d310 | Deploy all | $50+ | 1.5+ sustained 2+ days (warm) OR 2.5+ day_1_5 (cold) |

**Anti-Traps:**
1. Never book $50-80 fliers on "lone boat" signals (S6 tides post: one $80 lapse locked out season)
2. Never all-in on momentum (fleetwatch post: consecutive days bookings kill objectivity)
3. Never skip peak tails (weatherman post: d115-d120, d175-d190, d210-d212 tails worth as much as starts)
4. Never override hard rules for boredom (tides post: "write holding again" is correct move when uncertain)

**S07 Expected Outcomes:**

*Warm Regime (El Niño, like S6):*
- April-May phase: 4-6 fish from 2-3 MULTI_DAY trips ($800-1000 spend)
- June phase: 1-2 fish from 1 MULTI_DAY trip if signal confirms ($300-400 spend)
- Aug-Oct phase: 4-6 fish from 2-3 MULTI_DAY trips ($600-800 spend)
- **Total: 9-14 fish (vs S6's 14.57 if capital paced, vs actual S6 best-class 20-24 if optimal)**
- Rank target: #5-8

*Cold Regime (La Niña, like S2):*
- April-May: 0 fish (dead zone hold)
- October peak: 6-9 fish from 2-3 DAY_1_5 trips ($800-1100 spend)
- **Total: 6-9 fish (rank #10-15, but S2 scored 14.2 so model is conservative)**
- Rank target: #5-10

**Forum Integration (S07 Daily):**
- Read ensembler, dope_reader, elnino, calendarist posts for regime confirmation
- Read weatherman, greenwater, tides for water temp / upwelling signals
- Post 2 max/month: d032 regime call + d150 or d250 mid-season adjustment if needed

**Decision Gate (d032 Planning Turn):**
1. ONI value confirmed?
2. April fleet data (d030-d032 trips) showing 1.5+ signals?
3. Regime decision: Warm=Phase 1 multi_day deploy ($1000 cap), Cold=October-only hold ($1900 reserve)
4. Submit strategy.py with regime-adaptive rolling PTO commits if desired

### Forum Integration (S07)
**Daily reads d001-d310:**
- ensembler, dope_reader, calendarist: regime calls + multi-day peak signals (trusted, validated S6)
- elnino: April peak timing and regime awareness (ranked #1 cumulative)
- thrifty/thrifty_solo: Capital pacing and class efficiency (ranked #1-3 S06)
- weatherman, greenwater, tides: Upwelling/water temp correlation, wind patterns

**Post frequency:** 2 posts/month maximum
- d032: Regime detection call if warranted (warm vs cold thesis)
- d150-160: Mid-season update if early peak underperforms (pivoting strategy)
- d200+: Optional September peak confirmation or October pivot

### Cumulative Standing Context
- Current cumulative (post S06): 14.204 (rank #3, behind elnino 15.33, ens_solo 15.27)
- S06 score: 14.5712 (rank #6 in season, behind top 5 scorers)
- Gap to #1: 1.13 fish (elnino cumulative), 9.4 fish (ens_solo season)

**S07 target:** 16-18 fish (beat thrifty_solo 19.60, approach ens_solo 23.97)
- If achieved: Move cumulative to #2 (if S06 adds to cumulative, 14.2+16 = 30.2 vs elnino ~30)
- Requires: Perfect regime detection at d032 + capital discipline through Sept peak + 1-2 lucky hot boats

### Lessons Learned (S06 vs S2 vs S7 prep)
1. **Regime beats calendar**: S2 (La Niña, October-only) vs S6 (El Niño, April-May hot). Detect at d10-32, don't force past years' patterns.
2. **Peaks extend longer than expected**: Sept peak (doy 165-178) was real and massive, missed because capital spent April-May. ALWAYS reserve 30-50% capital for secondary peaks.
3. **Capital pacing is 90% of the game**: The difference between 14.57 (me) and 23.97 (ens_solo) was likely capital discipline (holding for Sept) not better signals.
4. **PTO batch-commit is a trap**: Committing 10 days d110-d125 speculatively wasted 8+ days that could have been used Sept-Oct.
5. **Competitor dilution matters**: Single hot boat with 0 competitors beats 3-boat average; always check offer details.
6. **Class hierarchy by regime**: Warm=multi_day domination, Cold=day_1_5 domination. Wrong class in wrong regime = 50% loss.
7. **Multi-day efficiency**: 4+ ypa with $400-550 cost = $100-150/fish. Three_quarter 2+ ypa at $150 = $75/fish. Both viable, but multi_day is backbone for warm regimes with capital.

### S06 d244 Final Analysis (Season Ended d182, Watching d244)

**Actual S06 Result:** 14.5712 fish, Rank #6 in season, Rank #3 cumulative

**Opportunity Cost Analysis (Data-Backed):**
- Spent $1850 by d117 on THREE_QUARTER (avg 1.12 yt/angler observed)
- Missed June peak: MULTI_DAY 2.19 yt/angler (d130-d152, 12 trips fleet-wide) = 2-4 fish lost
- Missed Late August: MULTI_DAY 2.50 yt/angler (d175-d195, 54 trips) = 3-5 fish lost
- Missed Sept-Oct: MULTI_DAY 2.02-2.19 yt/angler (d196-d213, 95 trips) = 2-4 fish lost
- **Total missed opportunity: 7-13 fish** (could have scored 21-28 with capital discipline)

**Root Causes:**
1. **Full capital depletion by d117:** Spent $1850/2000, left $150 buffer (not enough for any booking)
2. **Wrong class focus:** THREE_QUARTER (1.12 yt/angler avg I observed) instead of MULTI_DAY (2.19+ yt/angler)
3. **Batch PTO commit trap:** Committed all 10 days d110-d125 speculatively, burned 8+ on non-peak periods
4. **No phase 2 capital reserve:** Should have held $600-800 minimum through d220

**Why I Ranked #6 Instead of #1-3:**
- ens_solo (23.97 fish): Likely captured April + August + Sept peaks (3 separate deployments)
- thrifty (20.38 fish): Likely deployed selectively with rolling capital pacing
- thrifty_solo (19.60 fish): Likely strong April execution with capital reserve for Aug-Oct
- **Me (14.57 fish):** Heavy April, zero June, zero late-Aug, zero Sept-Oct

**Competitive Insights from Forum (d213 postmortems):**
- **weatherman:** Missed peak tail d117-d120 (1.15-1.52 yt/angler) due to capital lock at d115 booking; estimated 3.9 fish opportunity
- **ensembler:** Locked at d152 with $50, watched d170-d182 DAY_1_5 3.4-4.14 yt/angler unfunded; estimated 2-4 fish opportunity
- **overreactor:** Broke at d185, watched d210-d212 DAY_1_5 4.1 yt/angler unfunded (best non-multi peak in season); estimated 7.5 fish opportunity
- **tides:** One $80 rule-break flier locked budget below class floor for 150+ days; cost entire season
- **streaker:** October MULTI_DAY (4.27 yt/angler peak) requires pre-staged capital; early bookings exhaust ammunition

**Key Lesson Crystallized:**
Capital pacing is the primary variable. Class selection and timing are secondary. The difference between rank #6 (14.57) and rank #1 (23.97) is ~$600 held in reserve from d117-d150 to capture June-Aug peaks that were real and sustained.

### S07 Readiness Check
- ✅ Regime detection framework ready (ONI + d1-10 fleet data)
- ✅ Capital pacing template built with **MULTI_DAY class prioritization** (2.19+ yt/angler proven)
- ✅ PTO rolling schedule planned (1 day per booking, 3-4 reserved Sept-Oct, never batch)
- ✅ Phase 2 capital floor enforced ($600+ minimum through d220, non-negotiable)
- ✅ Anti-trap rules codified (no fliers, no momentum booking, preserve tails)
- ✅ Forum integration strategy (ensembler, thrifty_solo, elnino, weatherman guides)
- ⚠️ Strategy.py not yet written (will submit at d032 planning turn with regime call)

## S06 d305 Final Postmortem - VALIDATED & S07 LOCKED

### S06 Season Closed: 14.5712 fish, Rank #6 in season, Rank #3 cumulative
- Budget: $0 (spent d93-d117)
- PTO: 0 (committed d110-d120, d124-d125)
- Season completely locked out d118-d305 with zero capital/PTO
- All 11 trips settled successfully; no cancellations

### Data Validation (arena_eval d305 analysis)
**Class Performance by Phase (S06 fleet-wide):**
- MULTI_DAY (special 2+ day class): Phase1 3.723 ypa, Phase2 1.799 ypa, Phase3 1.226 ypa
- THREE_QUARTER: Phase1 1.320 ypa, Phase2 0.964 ypa, Phase3 0.363 ypa
- DAY_1_5 + OVERNIGHT combined: Phase1 1.414 ypa, Phase2 0.808 ypa, Phase3 0.284 ypa

**Frontloader booking window (d93-d117, THREE_QUARTER):**
- d93: 1.482 ypa (246 yt)
- d108: 1.993 ypa (279 yt, peak day)
- d111: 3.463 ypa (142 yt, single excellent day)
- d117: 2.144 ypa (253 yt, final peak)
- Average: 1.512 ypa across my 8 THREE_QUARTER trips (solid for the class)

**What I missed (if capital available):**
- Phase2 (d118-d220) MULTI_DAY: 218 trips, 1.799 ypa = 1.2 fish opportunity per $400 trip
- If I'd held $800 budget: 2 MULTI_DAY trips × 1.8 ypa = 3.6 fish (vs actual $0)
- Phase3 (d220-d310) MULTI_DAY: 353 trips, 1.226 ypa = 0.8 fish per $550 trip (weaker)

**Competitive gap (14.57 vs ens_solo 23.97 = 9.4 fish):**
- ~5-6 fish from not booking Phase2 MULTI_DAY (1.8 ypa was real)
- ~3-4 fish from not booking any Phase3 (declining performance)
- Net: could have scored 20-21 fish with capital discipline (hold $1000+ through d220)

### Mechanism of Failure: Three Vectors
1. **Full capital depletion d117:** Spent $1850/2000 in 25 days, left $150 buffer
2. **Class selection sub-optimal:** THREE_QUARTER 1.5 ypa was fine for Phase1, but MULTI_DAY 3.7 ypa existed (not attempted)
3. **Phase2 capital reserve not executed:** My notes said hold $600-800, but spent all by d117 anyway

### Why ens_solo Won (23.97 fish)
Most likely:
- Captured Phase1 (April): 5-6 fish on MULTI_DAY or optimal THREE_QUARTER
- Held capital through Phase2
- Captured Phase2 (June-Aug): 6-8 fish on MULTI_DAY (1.8 ypa) or strong THREE_QUARTER
- Captured Phase3 (Sept-Oct): 8-10 fish on remaining peaks
- Total: 19-24 fish with proper sequencing

### Forum Consensus at d274 (FINAL LOCK)
Forum voices (d274 postmortems): biggame, weatherman, ensembler, elnino, streaker, calendarist all converge:

**1. Climate Regime (ONI) is the Primary Decision Variable**
- El Niño (ONI > +0.3): April-May peak REAL, June-Aug secondary peak REAL (MULTI_DAY 1.8+ ypa), Oct decay
- La Niña (ONI < -0.3): April dead (0.0-0.3 ypa), October single mega-peak (DAY_1_5 3.0+ ypa)
- **Lock decision at d10**: No mid-season pivots allowed

**2. Capital Sequencing (Not Pacing) Wins**
- Never deploy >60% in one phase window
- MULTI_DAY class availability varies by phase; must preserve capital for confirmed peaks
- Example: S06 Phase1 MULTI_DAY 3.7 ypa (elite), Phase2 1.8 ypa (good), Phase3 1.2 ypa (OK)
- Deploy Phase1 if warm (40-50% capital), hold rest for Phase2-3 confirmation (60-50%)

**3. Class Selection: Regime-Dependent, Data-Backed**
- **Warm regime (El Niño):** MULTI_DAY >> THREE_QUARTER (S06 data: 3.7/1.8/1.2 ypa vs 1.3/0.96/0.36 ypa)
- **Cold regime (La Niña):** DAY_1_5 only (S2 formula: October 3.0+ ypa, April 0.06 ypa)
- Never book three_quarter in cold regime (<0.3 ypa waste)
- Never book half-days (hd_am/hd_pm) in any regime

**4. PTO Discipline: Rolling 1:1, No Batch**
- Commit exactly 1 day per booking decision, 14 days ahead
- Never commit speculatively (S06 trap: d110-d120 batch lock wasted 8 days)
- Reserve 3-4 Fridays for Phase3-4 execution (don't lock all 10 by d200)

### S07 Locked Execution Plan (Data-Driven, Regime-Adaptive)

**Phase 0: Regime Detection (d1-d10) - NO TRADING, ANALYSIS ONLY**
1. d1-d2: Query ONI index (climate determines season)
2. d3-d10: Monitor April fleet data (doy 93-102 frame)
3. d10 decision gate: 
   - If ONI > +0.3 AND fleet shows 1.5+ yt/angler d3-d10: **WARM regime, deploy Phase1**
   - If ONI < -0.3 OR fleet <0.5 yt/angler d3-d10: **COLD regime, hold for October**
   - If neutral: **SPLIT regime, light Phase1, hold Phase2-3**
4. Submit strategy.py at d10 with regime call embedded; no changes after

**Phase 1: Spring Execution (d10-d150, ~140 days)**

*Warm Regime (El Niño):*
- Capital: Deploy max $1000 (40-50%), hold min $1000 (50-60%)
- Class: MULTI_DAY primary (3.7 ypa Phase1, target it), THREE_QUARTER secondary (1.3 ypa fallback)
- Trigger: Class shows 1.5+ yt/angler sustained 2+ days (confirmed not spike)
- Booking cadence: 2-4 trips d30-d60 (probe window), reassess d61+
- **Hard floor**: Never drop below $1000 post-booking during Phase1
- Exit: Day 10 of sustained signal crest (lock capital, stop deploying)
- Expected yield: 4-8 fish

*Cold Regime (La Niña):*
- Capital: Deploy max $100 (insurance test only), hold min $1900
- Book: NONE unless DAY_1_5 shows 2.0+ yt/angler sustained 3+ days (rare in spring)
- Expected yield: 0 fish (intentional dry hold)

**Phase 2: Summer Hold Strict (d150-d230, ~80 days)**

*All Regimes:*
- Capital: ZERO new deployments (maintain hard floor from Phase1)
- **Exception trigger only:** If sustained 1.5+ class signal d160-d200, ONE test trip ($150-300 max)
- PTO: Only commit if Phase1 booking triggers more trips; never speculative
- Reserve minimum: $600-800 for Phase3
- Expected yield: 0-1 fish (mostly reserve preservation)

**Phase 3: Fall Execution (d230-d310, ~80 days)**

*Warm Regime:*
- Capital: Deploy $400-800 remaining (based on Phase1-2 spend)
- Class: MULTI_DAY if 1.5+ ypa observed (1.8 ypa Phase2, 1.2 ypa Phase3 possible), else THREE_QUARTER
- Trigger: Class sustained 2+ days + water confirms
- Booking: 1-2 trips d245-d280 if Phase2 testing holds signal
- **Hard floor**: Maintain $200 minimum to d310 (emergency reserve)
- Expected yield: 3-6 fish

*Cold Regime:*
- Capital: Deploy $1400+ (60-70%) on confirmed DAY_1_5 peaks
- Class: DAY_1_5 only when 2.5+ yt/angler (October proven baseline)
- Trigger: d280+ confirmed 2.5+ yt/angler multi-day signal from forum/fleet data
- Booking: 2-3 trips d287-d305 on peaks (avoid greedy tail chasing after d10 of peak)
- Expected yield: 6-12 fish

**Capital & PTO Enforcement Checkpoints**

| Phase | Window | Budget Floor | PTO Constraint | Exit Trigger |
|-------|--------|--------------|---|---|
| 0 | d1-d10 | Full $2000 | None | Regime confirmed |
| 1 | d10-d150 | $1000 min | 1:1 per booking, max 2-3 days | Day 10 of crest |
| 2 | d150-d230 | $600-800 min | 1 per test only | Hold firm |
| 3 | d230-d310 | $200 min | 2-3 Fridays max | End of season |

### S07 Expected Outcomes (Data-Backed Forecast)

**Warm Regime (El Niño, like S6):**
- Phase 1: 4-6 fish from 2-3 MULTI_DAY trips (3.7 ypa × $800-1000)
- Phase 2: 0-2 fish from 1 test trip or hold (1.8 ypa declining)
- Phase 3: 4-6 fish from 2 trips on Aug-Sept secondary (1.2-1.8 ypa)
- **Total: 8-14 fish (target 12-13, rank #5-8, beat S06's 14.57 with proper sequencing)**

**Cold Regime (La Niña, like S2):**
- Phase 1: 0 fish (dry hold)
- Phase 2: 0 fish (dry hold)
- Phase 3: 8-12 fish from 2-3 DAY_1_5 trips (3.0+ ypa × $1400+)
- **Total: 8-12 fish (target 10, rank #8-12, expect rank #5-10 cumulative if history repeats)**

### Anti-Traps (Proven S06 Failures)
✗ **Phase1 full depletion** (S06 d117: $1850/2000 = zero Phase2-3 optionality)
✗ **Batch PTO commits** (S06 d110-d120: locked 10 days, used only 2 in peak windows)
✗ **Class blindness** (S06: booked THREE_QUARTER 1.3 ypa when MULTI_DAY 3.7 ypa existed in Phase1)
✗ **Single-boat chasing** (overreactor d185: $80 myth booking = locked out of $1900 main peak d210-d212)
✗ **Mid-peak consecutive bookings** (momentum trap: forces booking on day 8+ of peak when declining)
✗ **Ignoring regime signals** (biggame, calendarist d274: read ONI but calendar-veto'd optimal execution)

### Why S07 Will Score 14-18 Fish
S06 left 9.4 fish on table (23.97 ens_solo vs my 14.57). Root cause: full capital depletion d117, missing Phase2-3 peaks at 1.8 and 1.2 ypa.

S07 formula:
- Phase1: 4-6 fish (same execution as S06 d93-d117, DAY_1_5 priority when fleet signals hot)
- Phase2: Hold + 1 test = 0-2 fish (capital preservation, $600+ floor)
- Phase3: 6-8 fish (full deployment on confirmed secondary DAY_1_5/OVERNIGHT peaks)
- **Total: 10-16 fish** (median 13-14, approaching top 5 cumulative)

### S07 Strategy.py (Regime-Adaptive, Auto-Deploying)
Will encode at d10:
1. Query ONI + April fleet average (d3-d10)
2. If warm (ONI > +0.3): **Auto-commit 2 Fridays for Phase1 d30-d60 window** (removes hesitation)
3. If cold (ONI < -0.3): **Auto-commit 0 days until d280** (prevents false signals)
4. Monthly rolling: check d60, d120, d180, d250 for regime confirmation (pivot only if ONI >1.5 inverts)

### CRITICAL S07 CORRECTION (Post d305 Forum)
**MULTI_DAY is NOT bookable.** elnino and follower corrected the entire cohort's S7 plans at d305.

- MULTI_DAY appears in fleet aggregation data (2+ day classes pooled), avg 2.21 yt/angler in S6
- But RULES.md's bookable classes are ONLY: HD_AM, HD_PM, TWILIGHT, THREE_QUARTER, FULL_DAY, OVERNIGHT, DAY_1_5
- Use MULTI_DAY fleet signals to identify WHEN peaks fire, then BOOK DAY_1_5 (closest bookable equivalent to MULTI_DAY efficiency)
- ens_solo (rank 1, 23.97 fish) and thrifty_solo (rank 3, 19.6) likely booked DAY_1_5 during high MULTI_DAY signal windows, not MULTI_DAY itself

**S07 Revised Class Priority:**
1. **DAY_1_5** (1.27 yt/angler in warm, 3.0+ yt/angler in cold October)—primary bookable class
2. **OVERNIGHT** (0.71 yt/angler in warm)—fallback if DAY_1_5 unavailable
3. **THREE_QUARTER** (1.37 yt/angler in warm)—tertiary, capital-efficient but lower yield
4. Never HD_AM/HD_PM/TWILIGHT (0.01-0.2 yt/angler, waste of PTO)

### S07 Ready: Decision Framework Locked
Season 7 strategy is deterministic and data-driven. No more calendar loyalty. No more capital all-in. No more PTO batch lock. Regime detection at d10 gates the entire season; nightly bookings defer to this framework with zero mid-season pivots.

---

## S07 LOCKED FRAMEWORK (d335 Final Prep)

### Regime Detection Phase (d1-d10, NO TRADING)
1. Monitor ONI climate index d1-d5 (becomes public by d9-d10)
2. Observe early April fleet data (d3-d10): DAY_1_5 and THREE_QUARTER class averages
3. Classify by d10:
   - **Warm** (El Niño): ONI > +0.3 OR April fleet avg > 1.5 yt/angler DAY_1_5 → Twin peaks (April-May + Aug-Oct)
   - **Cold** (La Niña): ONI < -0.3 OR April fleet < 0.5 yt/angler → October-only peak
   - **Neutral**: -0.3 ≤ ONI ≤ +0.3 → Monitor d50+ before committing strategy

### Phase 1: Spring Execution (d10-d150, ~140 days)

**Warm Regime (El Niño):**
- Capital: Deploy max $1000 (40-50%), **floor $1000 minimum** through d150
- Class: DAY_1_5 primary (target 1.5+ yt/angler sustained 2+ days), OVERNIGHT secondary, THREE_QUARTER fallback
- Trigger: Class fleet avg ≥1.5 yt/angler sustained 2+ days + water ≥17°C sustained
- PTO: Commit 1 day per booking decision at d+14 cutoff (rolling, never batch). Target 2-3 Fridays d30-d90 for d44-d104 bookings
- Booking cadence: 2-4 trips max April-May (spread competitor dilution risk)
- Exit: Day 10 of confirmed signal peak (lock capital, stop deploying)
- Expected: 4-6 fish from 2-3 DAY_1_5 trips

**Cold Regime (La Niña):**
- Capital: Deploy max $100 (insurance test only), **floor $1900 minimum** through d280
- Book: NONE unless DAY_1_5 shows 2.0+ yt/angler sustained 3+ days (rare in spring, unlikely)
- PTO: Hold all 10 days; no commits yet
- Expected: 0 fish (intentional dry hold)

### Phase 2: Summer Hold + Secondary Scout (d150-d230, ~80 days)

**All Regimes:**
- Capital: **Maintain hard floor from Phase 1** (no new large deployments)
- Exception trigger only: If sustained 1.5+ yt/angler DAY_1_5 signal d160-d200, ONE test trip max ($150-400)
- PTO: Only commit if Phase 1 booking triggers more trips (1:1 rule)
- Reserve minimum: $600+ for Phase 3
- Expected: 0-1 fish (mostly reserve preservation)
- **Key rule:** Do NOT book consecutively. If you booked d10, skip d11-d13, book d14 only if sustained signal.

### Phase 3: Fall Execution (d230-d310, ~80 days)

**Warm Regime (El Niño):**
- Capital: Deploy $400-800 remaining (based on Phase 1-2 spend)
- Class: DAY_1_5 if 1.5+ yt/angler observed (peak window), OVERNIGHT if 1.0+, never THREE_QUARTER alone (class declining)
- Trigger: Class sustained 2+ days + water confirms + capital ≥ $300 post-booking
- Booking: 1-2 trips d245-d280 if Phase 2 testing holds signal; 2-3 trips if Phase 3 hot
- **Hard floor:** Maintain $200 minimum through d310 (emergency reserve)
- Exit: Day 10 of peak, or capital drops $200 floor, whichever first
- Expected: 4-6 fish from 2-3 DAY_1_5 trips

**Cold Regime (La Niña):**
- Capital: Deploy $1400-1600 (70-80%) on confirmed October DAY_1_5 peaks
- Class: DAY_1_5 ONLY when 2.5+ yt/angler (proven October baseline)
- Trigger: d280+ confirmed 2.5+ yt/angler multi-day signal from forum/fleet data
- PTO: Commit 2-3 Fridays for d280-d310 bookings (d265-d280 cutoff window)
- Booking: 2-3 trips d287-d305 on confirmed peaks (avoid greedy tail chasing after day 10)
- Expected: 8-12 fish from 2-3 DAY_1_5 trips

### Capital & PTO Enforcement Checkpoints

| Phase | Window | Budget Floor | Budget Ceiling | PTO Constraint | Exit Trigger |
|-------|--------|--------------|---|---|---|
| 0 | d1-d10 | Full $2000 | No deploy | None | Regime confirmed, no trading |
| 1 | d10-d150 | $1000 min | $1000 deploy max | 1:1 per booking, max 3-4 days total | Day 10 of peak, or capital drops $1000 |
| 2 | d150-d230 | $600 min | Hold (exception $300-400 test only) | 1 per test only | Signal fades or capital drops $600 |
| 3 | d230-d310 | $200 min | Deploy all remaining | 2-3 Fridays for Oct | Season end d310 |

### Anti-Trap Checklist (Proven S06 Failures)
✗ **Phase1 full depletion** (S06 d117: $1850/2000 spent = zero Phase2-3 optionality) → Hold $1000+ floor through d150
✗ **Batch PTO commits** (S06 d110-d120: locked 10 days, used only 2) → Commit 1:1 with bookings only
✗ **Single-boat chasing** (overreactor d185: $80 myth booking) → Only count class fleet avg, never single boats
✗ **Momentum booking** (consecutive days d108-d113: forced lower-quality bookings) → Skip 2-3 days between bookings
✗ **Peak tail greedy** (dope_reader d191+: booked day 12-15 of peak when quality declined) → Lock capital after day 10
✗ **Wrong class in wrong regime** (S6 THREE_QUARTER when DAY_1_5 available) → Prioritize DAY_1_5 always

### Class Efficiency Reference (S6 Data, Regime-Dependent)
**Warm Regime (El Niño, S6):**
- DAY_1_5: ~1.27 yt/angler (primary target)
- OVERNIGHT: ~0.71 yt/angler (fallback, capital-efficient $400/trip)
- THREE_QUARTER: ~1.37 yt/angler (viable but declining mid-season)

**Cold Regime (La Niña, S2):**
- DAY_1_5: 3.0-5.0 yt/angler October only (primary target)
- THREE_QUARTER: 0.0-0.3 yt/angler (waste, avoid)
- OVERNIGHT: 0.5-1.5 yt/angler (fallback if DAY_1_5 unavailable)

### Forum Signals to Trust (Daily d1-d310)
**Reliable voices for regime + peak calls:**
- elnino, ensembler, dope_reader: Climate regime + multi-day signal correlation
- thrifty_solo, ens_solo: Capital pacing + class efficiency (top season scorers)
- weatherman, greenwater, tides: Water temp + upwelling patterns

**Not to follow (noise or inflexible):**
- skeptic, calendarist: Calendar-only thesis, missed El Niño regime
- follow, overreactor: Signal-chasing without capital discipline

### S07 Post Frequency & Content
- **d10 (if regime signal clear):** Post regime call (1-2 sentences). Commit public to strategy.
- **d150 (if Phase 1 underperforms):** Post adjustment if needed (1 post allowance).
- **d250-d280 (if regime shift detected):** Post pivot if needed (1 post allowance).
- Total: 2 posts/month max. Focus on regime confirmation, not daily noise.

### S07 Success Metrics
**Warm Regime Target (El Niño, 60% likely):**
- Phase1 (April-May): 4-6 fish (2-3 DAY_1_5 @ 1.5 yt/angler avg)
- Phase2 (June-Aug): 0-2 fish (hold, optional 1 test)
- Phase3 (Sept-Oct): 4-6 fish (2-3 DAY_1_5 @ 1.5 yt/angler avg)
- **Total: 8-14 fish expected** (median 11-12)
- Rank target: #5-10 season, move cumulative toward #1-2

**Cold Regime Target (La Niña, 35% likely):**
- Phase1-2: 0 fish (dry hold)
- Phase3 (Oct): 8-12 fish (2-3 DAY_1_5 @ 3.0+ yt/angler)
- **Total: 8-12 fish expected** (median 10)
- Rank target: #8-12 season, defend cumulative #3

### Key Mental Model for Nightly Decisions (d11-d310)
Every evening at 21:00, you have **one job**: check if today's fleet data matches the regime trigger (class avg ≥X for 2+ days, water ≥Y°C), and if capital/PTO allow, book ONE trip. Never book consecutively. Never chase single boats. Never override capital floor. Strategy.py handles PTO auto-commits; your job is class/boat selection and capital discipline at the booking cutoff.

**Regime is fixed at d10.** If ONI was +0.5, you commit to "warm regime April-May heavy, hold summer, deploy Sept-Oct secondary" and do NOT change course mid-season based on weak July signals. Season 6 saw weak June-July noise; calendar-locked regimes ignore that noise and wait for August-September confirmation. This is the edge: patience + discipline.

### S07 Nightly Checklist (Use Every Evening d11-d310)
1. Check class fleet avg (DAY_1_5, OVERNIGHT, THREE_QUARTER) for today's trips
2. Check water temp (Scripps pier if available)
3. Check capital remaining and PTO remaining
4. If fleet ≥trigger AND water ≥threshold AND capital ≥$300 after booking AND PTO ≥1 available:
   - Book 1 trip (preferred class per regime)
   - Commit 1 PTO day at d+14 if weekday booking
5. If not all conditions met, pass (hold)
6. Never book twice in 3 days. Never drop capital below floor. Never book after day 10 of peak.

---

**Season 7 is ready to deploy. Regime detection at d10 gates everything. No hesitation. No second-guessing. Execute the framework and let the climate do the work.**

## S06 SEASON-END RETROSPECTIVE (d365 Planning Turn)

### Final S06 Score: 14.5712 fish (Rank #6 in season, Rank #3 cumulative)

**What worked:**
1. **Regime detection**: Pivoted from Oct-only strategy (S2 La Niña pattern) to April-heavy after d91 forum signals; El Niño El Niño regime was real and live. Decision to abandon calendar lock and trust ensembler/dope_reader at d032 paid off (even though I was slow to act until d91).
2. **Aggressive spring execution**: d093-d117 booking run captured 14.57 fish in 25 days. Three_quarter class (avg 1.12 yt/angler observed) was solid for April window given capital constraints. Beat S2's 14.2 cumulative despite identical budget.
3. **Class discipline**: Never booked half-days (HD_AM/PM). Stuck to THREE_QUARTER and OVERNIGHT only. This rule held.
4. **Competitor awareness**: d112 with 0 competitors (share 1.864) vs d110 with 3 competitors (share 0.957) shows boat selection matters—check offer details always.
5. **Forum integration**: Read ensembler, dope_reader, greenwater daily. Their regime calls were validated.

**What failed:**
1. **Full capital depletion by d117**: Spent $1850/2000 in 25 days, left only $150 buffer. This killed Phase 2-3 optionality.
   - June peak (d130-d152): DAY_1_5 class 2.19 yt/angler = 2-4 fish opportunity (0 caught)
   - August peak: DAY_1_5 2.50 yt/angler = 2-3 fish opportunity (0 caught)
   - September peak (d165-d178): DAY_1_5 4.55-5.5 yt/angler = 8-12 fish opportunity (0 caught)
   - **Total missed: 12-19 fish. Couldhave scored 26-33 with capital discipline.**

2. **Batch PTO commit trap (d110-d120)**: Locked all 10 PTO days speculatively in 4 days, then burned 8+ unused on non-peak periods. Should have committed 1 day per booking only (rolling).

3. **Wrong class in peak window**: Booked THREE_QUARTER ($150/trip, 1.12 yt/angler observed d93-d117) when DAY_1_5 was available and (post-hoc data shows) averaged 1.27 yt/angler in same window. Not a massive difference, but class hierarchy was unclear mid-season.

4. **No Phase 2 reserve**: Notes said "hold $600-800 through d220" but I executed $0 by d117. This wasn't a data-reading error; it was a discipline failure. I saw the framework but didn't enforce the capital floor rule.

5. **Execution lag (d060-d091)**: Understood regime shift at d60 after forum posts, but hesitated 30+ days before deploying. Cost 5-10 fish from late-April peak window (d093-d110 was the tail; d075-d093 was the head).

**Competitive gap:**
- ens_solo (23.97 fish): Likely captured April + June + August + September peaks through rolling capital pacing
- thrifty_solo (19.60 fish): Likely April strong, held $600+, captured secondary peak
- **me (14.57 fish)**: April only, zero everything after

The gap is 9.4 fish. Root cause: capital sequencing, not timing or boat selection.

**Key metrics (S06 vs S2):**
- S2: 14.204 fish (La Niña regime, October-only thesis worked)
- S6: 14.5712 fish (El Niño regime, April-only execution despite knowing multi-peak pattern)
- Cumulative (post-S06): 28.7752 (rank #3, 0.8 behind elnino 29.58, 10.5 behind ens_solo 39.25)

### Critical Learning: Regime Beats Calendar, Capital Pacing Beats Timing

**Climate regime (ONI) is the primary decision variable:**
- Warm (El Niño, ONI > +0.3): April-May peak REAL + August-September secondary peak REAL. Multiple 2+ yt/angler DAY_1_5 windows across season.
- Cold (La Niña, ONI < -0.3): April dead (0.0-0.3 yt/angler), October single mega-peak (DAY_1_5 3.0+ yt/angler).
- Lock regime decision at d10 based on ONI + April fleet data. No mid-season pivots.

**Capital sequencing wins tournaments:**
- Deployed 100% by d117 = rank #6 (missed 70% of season by value)
- Deploy 40-50% by d120, hold 50-60% for secondary peaks = likely rank #2-3 (ens_solo pattern)
- The difference between #1 and #6 is $600 held in reserve from d117-d220, deployed at d165+ (September peak window)

**Class efficiency by regime:**
- **Warm (El Niño):** DAY_1_5 primary (1.27 yt/angler observed S6), THREE_QUARTER secondary (1.37 yt/angler but declining mid-season), OVERNIGHT fallback (0.71 yt/angler)
- **Cold (La Niña):** DAY_1_5 primary Oct only (3.0-5.0 yt/angler), never THREE_QUARTER (<0.3 yt/angler), OVERNIGHT only if DAY_1_5 unavailable

**PTO discipline:**
- Batch-commit trap (S06 d110-d120): locked 10 days in 4 days, wasted 8. Cost: zero flexibility for secondary peaks.
- Rolling 1:1 discipline: commit 1 day per booking decision at d+14 cutoff. Reserve 3-4 days for Phase 3. Never speculatively lock >3 days at once.

### S07 Execution Plan (Ready to Deploy)

**Regime Detection (d1-d10, no trading):**
1. Query ONI value available by d9-d10
2. Check April fleet data (doy 93-102): DAY_1_5 and THREE_QUARTER class averages
3. Classify by d10:
   - Warm (El Niño, ONI > +0.3): Twin peaks (April-May + Aug-Oct). Deploy Phase1 ($1000 cap), hold $1000 minimum through d150.
   - Cold (La Niña, ONI < -0.3): October-only peak. Deploy <$100 in Phase 1-2, hold $1900 for October.
4. No trading before regime lock.

**Phase 1 (d10-d150):**
- Warm: Deploy max $1000, hold min $1000. Book DAY_1_5 when fleet ≥1.5 yt/angler sustained 2+ days. Commit 1 PTO day per booking (rolling, not batch).
- Cold: Deploy <$100 (scouts only), hold $1900. Book nothing unless DAY_1_5 ≥2.0 sustained 3+ days (rare in spring).
- Expected: 4-6 fish (warm), 0 fish (cold).

**Phase 2 (d150-d230):**
- All regimes: Maintain hard floor from Phase 1. Exception trigger only: if sustained 1.5+ DAY_1_5 signal d160-d200, book 1 test trip max ($300-400).
- Reserve minimum $600 for Phase 3.
- Expected: 0-1 fish (mostly reserve preservation).

**Phase 3 (d230-d310):**
- Warm: Deploy $400-800 remaining. Book DAY_1_5 when fleet ≥1.5 yt/angler sustained 2+ days. Target 1-2 trips (Aug-Sept secondary window).
- Cold: Deploy $1400+ on confirmed October DAY_1_5 ≥2.5 yt/angler. Book 2-3 trips d287-d305.
- Maintain $200 minimum floor.
- Expected: 4-6 fish (warm), 8-12 fish (cold).

**Anti-Traps (S07 discipline rules):**
✗ Never deploy >60% capital in one phase window
✗ Never batch-commit PTO speculatively (1:1 rule only)
✗ Never let budget drop below phase floor (Phase1: $1000, Phase2: $600, Phase3: $200)
✗ Never book consecutively (skip 2-3 days between bookings to avoid momentum trap)
✗ Never chase single-boat signals (count class fleet averages only)
✗ Never override regime call mid-season based on weak July noise (patience wins)

**Forum integration (daily d1-d310):**
Read: elnino, ensembler, dope_reader (regime + multi-day calls), thrifty_solo, ens_solo (capital pacing guides), weatherman, greenwater, tides (water temp patterns).
Post: 2 max/month. d10 regime call, d150-d250 adjustment if needed.

### S07 Success Metrics
**Warm regime target:** 9-14 fish (Phase1 4-6, Phase2 0-1, Phase3 4-6). Rank #5-10 season, move cumulative toward #1-2.
**Cold regime target:** 8-12 fish (Phase1-2 0, Phase3 8-12). Rank #8-12 season, defend cumulative #3.

Regime lock at d10 is the entire edge. Execute with no second-guessing.

---

**Season 6 complete. Rank #6 season (14.57), Rank #3 cumulative (28.78). S07 ready to deploy with regime-adaptive, capital-paced framework. No calendar lock. No full depletion. No PTO batching. Discipline: $1000 Phase1 floor, $600 Phase2 floor, 1:1 PTO commits, rolling bookings. Regime decided at d10. Win the secondary peaks.**
