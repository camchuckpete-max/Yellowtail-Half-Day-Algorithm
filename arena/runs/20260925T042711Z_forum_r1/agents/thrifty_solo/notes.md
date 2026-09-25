# SEASON 6 RETROSPECTIVE (final, day 365) — read this first next season

**Final score: 19.6035, season_rank 3/34** (ens_solo 23.97, thrifty 20.38 ahead of us).
Cumulative: 20.2316, rank 6/34 (S2 0.6281 + S6 19.6035; S2 was a practice season).
13/13 bookings settled and ran, all THREE_QUARTER, avg share 1.508/trip. Budget ended at $50 (of
$2000), PTO at 6/10 (2 of 4 committed PTO days — d138, d140 — never got used, a sunk loss).
Beat every scripted bot by 7x+ and most LLM agents by a wide margin; lost 1st only to two agents
who kept fishing through Aug–Nov while we sat budget-floored from day ~133 onward.

## THE #1 THING TO FIX FOR SEASON 7 — bigger than budget pacing
**TWILIGHT, OVERNIGHT and DAY_1_5 are booked at 16:00 same-day, not 21:00 the day before.** The
nightly self only gets a decision call at **21:00**. There is no other manual decision point.
The *only* way to act on a 16:00 cutoff is `strategy.py` code, and ours sat as the untouched stub
(`"No strategy yet: books nothing."`) for all of season 6. Result: **zero TWILIGHT/OVERNIGHT/DAY_1_5
bookings were even attempted this entire season** — not because budget ran out (it did, separately,
by day 133), but because there was structurally no mechanism to act on them at all. Confirmed by
`rejected_actions_and_errors` being empty (no attempts, not rejected attempts) and all 13 bookings
being THREE_QUARTER.

This matters enormously because day_1_5 was the best-paying class of *this exact season*:
| S6 month | day_1_5 yt/angler | overnight | three_quarter |
|---|---|---|---|
| Aug | 0.33 | 0.18 | 0.23 |
| Sep | 0.66 | 0.30 | 0.49 |
| Oct | 1.00 | 0.04 | 0.39 |
| Nov | **3.36** | 0.07 | 0.61 |
day_1_5 beat 3Q every single month Aug–Nov, by 1.4x–5.5x. This matches the 5-season historical
table below. **Even a perfectly budget-paced season 7 gets nothing from this edge unless
`strategy.py` is actually written and submitted** — the pacing-cap rule alone (below) is necessary
but not sufficient.

**Season 7 action: at the very first planning turn, check whether the `submit_strategy` tool is
available (it was not surfaced in this session's toolset at the S6 season-end turn — confirm this
isn't just an environment quirk). If available, submit code that acts on the 16:00 tick for
TWILIGHT/OVERNIGHT/DAY_1_5 — draft below. If truly unavailable, that means these three classes are
permanently unbookable for this agent and should be dropped from all planning (stop reserving
budget/PTO for day_1_5 — it can never be spent).**

### Draft strategy.py for season 7 (only fill the 16:00 gap; leave 21:00 to the nightly self)
```python
"""Acts only on the 16:00 tick, for TWILIGHT/OVERNIGHT/DAY_1_5 — classes booked same-day at 16:00
that the 21:00 nightly briefing decision can never reach. Leaves HD_AM/HD_PM/THREE_QUARTER/FULL_DAY
(booked at 21:00 on d-1) entirely to the nightly manual decision. Books the best trailing-rate
scheduled boat when a class is bookable (PTO already committed, presumably by the nightly self
ahead of time) and budget_left leaves at least 1.5x the ticket price in reserve."""
from arena.api.ctx import Strategy, Book, CommitPTO

CLS_TO_TRIPS = {"TWILIGHT": "hd_twilight", "OVERNIGHT": "overnight", "DAY_1_5": "day_1_5"}
COSTS = {"TWILIGHT": 80, "OVERNIGHT": 400, "DAY_1_5": 550}
THRESHOLDS = {"TWILIGHT": 0.3, "OVERNIGHT": 0.4, "DAY_1_5": 0.4}


class Strategy(Strategy):
    name = "16:00 gap filler"

    def describe(self):
        return (
            "I only act at the 16:00 tick, on TWILIGHT/OVERNIGHT/DAY_1_5 - the classes booked "
            "same-day at 16:00 that a 21:00 nightly decision structurally cannot reach. For each "
            "bookable one I compare scheduled boats' trailing 14-day yellowtail-per-angler rate "
            "and book the best if it clears a flat threshold and budget_left stays >= 1.5x the "
            "ticket price after booking. I never touch HD_AM/HD_PM/THREE_QUARTER/FULL_DAY (booked "
            "at 21:00 the day before) - those are the nightly self's job. I do not commit PTO "
            "myself; I only book when an offer already shows bookable=True."
        )

    def _trailing_rate(self, ctx, offer_cls, boat, lookback_days=14.0):
        try:
            trips = ctx.observe("trips")
            tcls = CLS_TO_TRIPS[offer_cls]
            df = trips[(trips["cls"] == tcls) & (trips["boat"] == boat)]
            cutoff = ctx.now.t - lookback_days
            df = df[df["fish_date_t"] >= cutoff]
            anglers = float(df["anglers"].sum())
            if anglers <= 0:
                return 0.0
            return float(df["yt"].sum()) / anglers
        except Exception:
            return 0.0

    def decide(self, ctx):
        if ctx.now.hour != 16:
            return []
        for cls in ("DAY_1_5", "OVERNIGHT", "TWILIGHT"):
            cost = COSTS[cls]
            if ctx.budget_left < cost * 1.5:
                continue
            offer = ctx.offer(cls)
            if offer is None or not getattr(offer, "bookable", False):
                continue
            boats = ctx.scheduled_boats(cls, ctx.today) or []
            best_boat, best_rate = None, -1.0
            for boat in boats:
                rate = self._trailing_rate(ctx, cls, boat)
                if rate > best_rate:
                    best_boat, best_rate = boat, rate
            if best_boat and best_rate >= THRESHOLDS[cls]:
                return [Book(offer.id, f"16:00 reflex: {cls} trailing {best_rate:.2f} yt/angler on {best_boat}", boat=best_boat)]
        return []
```
Deliberately does **not** auto-commit PTO (too easy to get the weekday/weekend arithmetic for
multi-day trips wrong in code and waste a scarce PTO day for nothing, which is exactly how S6 lost
2 PTO days already). Instead: **the nightly 21:00 self should proactively `CommitPTO` for
Aug–Oct dates ~14–20 days out when it wants to reserve for an upcoming overnight/day_1_5**, using
`day.plus(1).is_weekend` / `day.plus(2).is_weekend` to check if the fishing/back dates would be
free (0 PTO) before deciding whether spending PTO is worth it — always check `is_weekend`/
`is_holiday`, never guess at a weekday-number encoding.

## Season 7 budget-pacing plan (still valid, now secondary to the fix above)
Season 6 spent $1950 of $2000 on 13x THREE_QUARTER ($150 each) by day 133, all Apr–Jul, leaving
nothing for Aug–Oct. Rule for S7:
1. THREE_QUARTER at $150 is still the right default no-PTO spring/summer play (Apr–Jul) — HD_AM/
   HD_PM are dead essentially every check, every season (0.00–0.03 yt/angler), not worth $80 even.
2. **Hard cap: no more than ~$1100 spent (≈7 3Q bookings) before day ~200 (mid-July).** Check
   budget_left vs day-of-year before booking once budget_left drops under ~$900; skip a night
   rather than blow the cap, even on a good boat.
3. Once $900–1100 is reserved and Aug arrives, let the strategy.py 16:00 reflex (if submitted)
   handle day_1_5/overnight directly — don't let 3Q nibble the reserve below $550 (one day_1_5
   ticket) after that point.
4. PTO: only commit when budget_left is comfortably above the price of the trip you intend to book
   on that date, and only 14+ days out as required. Never commit speculatively.

## Structural facts confirmed across seasons 1–6 (stable priors, safe to reuse)
- HD_AM/HD_PM: dead nearly every check, every season. Never worth booking.
- THREE_QUARTER: reliable positive in spring/summer, especially in warm-ENSO seasons (3, 4, 6).
- **day_1_5: the single best-paying class Aug–Nov of a warm-ENSO season, confirmed in 5/6 seasons
  including S6 itself (table above) — but it needs (a) real budget reserved ($550/ticket), (b) PTO
  planned 14+ days ahead, AND (c) actual `strategy.py` code, since the booking cutoff is 16:00
  same-day and no manual decision point can reach it.**
- overnight: more boat/season-dependent than day_1_5 — good in S3/S4 fall, weak in S1/S5/S6 (S6:
  overnight never topped 0.3 yt/angler Aug–Nov, well under day_1_5) — treat as secondary.
- Season 5 was the one year 3Q beat day_1_5 through fall — always check the current season's own
  trailing rate rather than assuming the calendar pattern holds blindly.
- ONI ~0.65–0.80 (mild-moderate El Niño) in S6 behaved like S3/S4, not S1/S2/S5 — a positive ONI
  read early in a season is a reasonable signal to lean into the day_1_5 fall plan.

## Mechanics confirmed this season (don't re-derive)
- The nightly self is reliable: 13/13 bookings settled with zero rejected actions all season —
  the 21:00 decision loop itself is not the failure point.
- Budget-floor below $80 (HD's price) makes the rest of a season a dead end — confirmed by 5
  separate check-ins (d182–d335) with zero change. Once budget_left < 80 and no PTO-funded trip is
  pending, stop pulling data each check-in; there is nothing left to decide.
- `submit_strategy` tool was not present in this session's toolset at the S6 season-end turn —
  worth re-checking at the S7 season-start turn; if present, submit the draft above immediately,
  don't wait.

## What to check early in season 7
1. Is `submit_strategy` available? If yes, submit the 16:00-gap-filler code turn one, not later —
   every week without it is a week the day_1_5 edge goes uncaptured, same as all of S6.
2. Read ONI as of day 1 — moderate positive (like S3/S4/S6) → lean into the fall day_1_5 reserve;
   flat/negative (like S1/S2/S5) → keep more flexibility, don't over-commit the reserve early.
3. Enforce the $1100-by-day-200 spending cap explicitly every night once budget_left < $900 —
   this is the one discipline failure that cost us 1st place in S6.
