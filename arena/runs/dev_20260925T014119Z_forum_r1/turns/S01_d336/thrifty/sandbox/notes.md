# Thrifty Season 1 - Day 306 FINAL STATUS

## Final Score & Rank
- **Season Score**: 0.1296 fish (6th/7 agents - last place)
- **Final Leaderboard**: B_BIG 7.89 (1st), temp_first 6.38 (2nd), persist 1.38 (3rd), B_PERSIST 0.34 (4th)
- **Budget left**: $30 (spent $1,970 of $2,000) - locked out, can't book ($80 minimum)
- **PTO left**: 2 days (8 committed early at doys 17-39, never used before d245)
- **Days remaining**: ~59 (d306 to ~d365)
- **Status**: Complete budget lockout; season effectively ended at d275

## Trip Performance - 15 Total Trips
- 14 trips: 0.0 fish (skunks)
- 1 trip: 0.1296 fish (d154 THREE_QUARTER: 7 yt caught, 52 anglers, 1 competitor)
- Booking timeline:
  - d35-57: 8 THREE_QUARTER trips, $1,200, 0 fish (early season, cold water)
  - d99-120: 4 HD_PM trips, $320, 0 fish (no bite signal)
  - d154-162: 3 THREE_QUARTER trips, $450, 0.1296 fish (d154 only scored)

## Why This Strategy Failed
1. **Early commitment trap**: Booked 8 three-quarter days at doys 35-57 before any bite signals existed
2. **No feedback loop**: Each trip cost $150-170 vs $80 half-days, burning budget on speculation
3. **Timing > Volume**: persist caught 10x more (1.38 vs 0.1296) using reactive 3-day rolling YT tracker
   - persist: waits for bite signals BEFORE booking, one trip per hot class per day, budget/PTO reactive
   - thrifty: pre-booked far ahead during cold period, volume over timing

## Leader Strategies (What Beat Me)
1. **B_BIG (7.89)**: Simple but effective - full budget on 1.5-day Friday trips in Aug-Sept (offshore window)
2. **temp_first (2.55)**: Water temp (Scripps Pier 7-day mean + 3-day trend) + offshore bite tracking (YT per angler on overnight/1.5-day, last 6 days), commits PTO once water >= 63°F
3. **persist (1.38)**: Tracks 3-day rolling YT SUM by class (no averaging), books cheapest hot class when > 0; pre-commits PTO by historical doy seasonality

## Next Season (S2) Key Changes
1. **Reactive booking**: Don't pre-commit PTO or book trips until fleet signals are hot
   - persist: sum(yt) over last 3 days by class > 0 triggers booking
   - temp_first: combine water temp >= 63°F AND offshore bite >= 0.8/angler OR bid >= 2
2. **3-day rolling tracker**: Sum recent fleet YT by class (not average), simpler than seasonality patterns
3. **Delay first trip**: Wait until doy 100+ when historical patterns show fish; d154-162 was our only hot window
4. **Budget discipline**: With $2k budget = ~14-25 trips max, each booking must have live bite signals
5. **PTO strategy**: 
   - Only commit 14-20 days ahead AFTER water signals warm (temp >= 63°F)
   - Use historical seasonality as tiebreaker (doy 150-170, 250-318 peaks)
   - Never pre-commit; save for actual hot signals
6. **Trip class mix**:
   - Early season (doy 35-150): weekend THREE_QUARTER ($150) or HD_PM ($80) only when bite is clear
   - Fall window (doy 250-318): offshore OVERNIGHT/DAY_1_5 when water warm AND bite strong
   - Ignore weekday fishing unless bite is extremely hot (justify PTO cost)

## Strategy Updated
- Changed to "Season End Holdout" - runs cleanly, returns empty actions
- Describe() documents the failure analysis and next season plan
- Will hold without booking for remaining 120 days

## Season 2 Implementation Plan

### Core Algorithm (Day 1)
```python
# 3-day rolling YT sum by class (persist logic):
recent_trips = trips[(trips.fish_date_doy >= today.doy - 3) & (trips.fish_date_doy <= today.doy)]
hot_classes = set()
for cls in ["HD_AM", "HD_PM", "THREE_QUARTER", "TWILIGHT", "OVERNIGHT", "DAY_1_5"]:
    if recent_trips[recent_trips.cls == cls]["yt"].sum() > 0:
        hot_classes.add(cls)

# Book cheapest hot offer if bookable
if hot_classes and budget >= 80:
    for offer in ctx.offer() ordered by cost ascending:
        if offer.cls in hot_classes and offer.bookable:
            Book(offer.id, boat=ctx.pick_boat(offer.cls, offer.departure))
            break
```

### PTO Strategy (Pre-commit 14 days ahead)
- Use historical seasonality: doy 150-170 (spring) and doy 250-318 (fall) have highest YT/trip rates
- Water trigger: only commit PTO for weekdays when water signal is warm (>=63°F from Scripps Pier or ONI)
- Commit every 14 days on Fridays + Mondays in hot windows
- Never pre-commit before water signals warm

### Budget Allocation
- Total: $2,000
- Reserve $800-1000 for fall offshore (doy 250-318)
- Use remaining $1,000-1,200 for spring/summer reactive bookings ($80-150 per trip)
- This allows ~12-15 trips vs my 15 trips of waste

### Boat Selection
- Always use `ctx.pick_boat(cls, day)` - the default boat that ran that class most in last 60 days
- This auto-selects based on success rate

### Trip Class Hierarchy (By Cost/Payoff)
1. **Weekends/holidays with no PTO cost**: THREE_QUARTER ($150) or HD_PM ($80) if bite is hot
2. **Weekday HD_PM ($80)**: Only if bite extremely strong, justifies 1 PTO day
3. **Fall offshore (doy 250-318)**: OVERNIGHT/DAY_1_5 ($400-550) when water warm AND bite >=0.8/angler
4. **Avoid weekday full-day/overnight early season**: Not enough signal to justify PTO

### Key Failures to Avoid
1. ✗ Pre-booking without bite signals (d35-57: 8 trips, $1,200, 0 fish)
2. ✗ Committing PTO before water warms or bite exists (lost 8 PTO days at d17-39)
3. ✗ Booking expensive trips when signals are weak (should use cheap half-days to test)
4. ✗ Averaging YT per trip (persist uses SUM over 3 days by class, more sensitive)

### Success Formula (What Beat Me)
- **persist (1.38)**: 3-day sum > 0 trigger, cheapest class first, pre-commit PTO from history
- **B_BIG (7.89)**: Pure volume on 1.5-day offshore in Aug-Sept (doy 250-318)
- **temp_first (6.38)**: Water temp (>=63F) + offshore bite (>=0.8/angler) + 3-day trend

### Data to Monitor Each Turn
1. Fleet YT sum by class (last 3 days) - tells us what's hot NOW
2. Water temp from Scripps Pier 7-day mean (>=63F = offshore season)
3. Offshore catch rate (YT/angler on overnight/1.5-day last 6 days)
4. PTO calendar - never book without 14-day pre-commitment for weekday fishing

## Season 2 Strategy Update (Day 306)

### Strategy Rewritten
Submitted new `strategy.py` "Reactive Bite Tracker" implementing:
- 3-day rolling YT sum by class (like persist)
- Books cheapest hot offer when class has > 0 YT in last 3 days
- Reserves $800+ for fall offshore window (doy 250-318)
- Commits PTO 14 days ahead only in peak windows (doy 150-170 spring, doy 250-318 fall)
- Uses ctx.pick_boat() for boat selection (default best performer)

### Key Algorithm Change
**Old**: Pre-book without signals → 14 skunks + 1 hit
**New**: Wait for 3-day rolling sum > 0 → reactive only when fleet confirms bite

### Arena Server Status
Arena MCP server DOWN (CONNECTION_CLOSED) at day 306 21:00 - cannot submit strategy or query data.
Strategy file written and ready when server reconnects.

## Final Season 1 Summary (Day 336)

### What Happened
- Day 306-336: Strategy held (no new bookings)
- Final score: 0.1296 fish (6th/7 agents, last place)
- Budget: $30 locked out (can't afford $80 minimum)
- Spent: $1,970 of $2,000

### Winning Strategies Analyzed
1. **B_BIG (7.89)**: Simple offshore focus - all budget on 1.5-day Friday trips Aug-Sept (doy 235-273)
   - High variance, high reward in known hot window
2. **temp_first (6.38)**: Water temp (Scripps Pier 7d mean >= 63-65F) + offshore bite (YT/angler >= 0.8-2.0)
   - Sophisticated signal combination, reactive, offshore focus
3. **persist (1.38)**: 3-day rolling YT sum by class, cheapest when > 0
   - Simple, reactive, handles both inshore/offshore

### Why I Lost
- Premise wrong: "volume beats timing" failed; timing beat volume 60x over
- Pre-committed PTO d17-39 (spring boost), never used before d245 when fleet finally signaled
- Booked d35-57 during cold season ($1,200 on 8 trips, 0 fish) - should have waited for bite signals
- Only success: d154 (0.1296 fish) when bite was actually hot (three_q avg 11.9 fish/trip on d149-153)

### Season 2 Must-Do
1. **Implement persist's 3-day rolling sum approach**: sum(yt) by class over last 3 fished days, book when > 0
2. **No pre-booking**: Wait for actual fleet bite signals before booking anything
3. **Budget discipline**: ~14-18 trips max at $80-150/trip vs my 15 trips (many skunks)
4. **PTO strategy**: 
   - Only commit 14 days ahead when signals are warm OR in proven peak windows
   - Never pre-commit PTO that won't be used
   - Focus on doy 150-170 (spring) and doy 250-318 (fall/offshore)
5. **Trip mix**:
   - Early season (doy 1-200): weekend THREE_QUARTER ($150) or HD_PM ($80) only with bite > 0
   - Fall (doy 200-318): OVERNIGHT/DAY_1_5 ($400-550) when water warm (>=63F) AND bite strong
   - Avoid expensive trips (>$200) unless bite confirmed
6. **Water temperature triggers**: Monitor Scripps Pier 7-day mean >= 63F (offshore season), ONI > 0 (warm year)

### Data to Monitor Each Turn (Season 2)
- Last 3 days YT sum by class (trips table, fleet-wide)
- Scripps Pier 7-day mean water temp (if available via ONI/climate data)
- Budget tracking ($ remaining, max trips affordable)
- PTO calendar (14-day pre-commitment rule)
