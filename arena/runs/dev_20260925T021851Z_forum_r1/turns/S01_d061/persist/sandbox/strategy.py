"""Momentum strategy: react to what the fleet caught in the last one to three days,
per trip class, favoring whichever class actually produces yellowtail.

Persona: "yesterday tells you tomorrow." No weather, no oceanography, just recent
pooled yellowtail-per-angler, checked separately for each trip class.
"""
import pandas as pd
from arena.api.ctx import Strategy, Book, CommitPTO

LOOKBACK_DAYS = 3
PTO_RESERVE = 2  # never pre-commit below this many PTO days left
BUDGET_RESERVE = 100.0  # never spend below this
PTO_TRIGGER_RATE = 0.1  # how hot recent big-trip catches must be to bet PTO 14d out

# Best expected value first: day_1_5 and overnight historically catch yellowtail on
# far more of their trips, and at far higher rates per angler, than half-day trips.
CLASS_PRIORITY = (
    ("DAY_1_5", ("day_1_5",)),
    ("OVERNIGHT", ("overnight",)),
    ("THREE_QUARTER", ("three_quarter",)),
    ("HD_PM", ("hd_pm", "hd_unspecified")),
    ("HD_AM", ("hd_am",)),
)


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather inputs. Each tick, for every trip class "
            "(day_1_5, overnight, three_quarter, hd_pm, hd_am) compute pooled "
            "yellowtail kept+released per angler over trips fished in the last three "
            "days. Try classes in order of historical value per trip (day_1_5, "
            "overnight, three_quarter, hd_pm, hd_am); book the first one whose recent "
            "rate is above zero, that is bookable, and that leaves at least $100 "
            "budget. Only one trip is booked per tick. A run of zero-catch days "
            "naturally stops booking since the lookback is only three days. Once a "
            "day, at the 21:00 tick, if the pooled recent rate across day_1_5, "
            "overnight and three_quarter is at least 0.1 fish per angler and more "
            "than 2 PTO days remain, pre-commit PTO for the weekday 14 days ahead "
            "(skipping weekends/holidays, which are free), betting that a live bite "
            "is likely to still be running when that date arrives, since the 14-day "
            "PTO rule leaves no other way to react to it. Boat choice always uses the "
            "default scheduled-boat picker."
        )

    def on_turn(self, ctx):
        pass

    def _rate(self, ctx, df, classes):
        if df is None or df.empty:
            return 0.0
        sub = df[df["cls"].isin(classes)]
        if sub.empty:
            return 0.0
        anglers = sub["anglers"].sum()
        if anglers <= 0:
            return 0.0
        return float(sub["yt"].sum() / anglers)

    def _recent_trips(self, ctx):
        rows = ctx.observe("trips")
        if rows is None:
            return None
        df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
        if df.empty or "cls" not in df.columns:
            return None
        today_doy = ctx.today.doy
        today_season = ctx.today.season
        recent_doys = [today_doy - i for i in range(LOOKBACK_DAYS)]
        mask = (df["fished_date_season"] == today_season) & (
            df["fished_date_doy"].isin(recent_doys)
        )
        return df[mask]

    def decide(self, ctx):
        actions = []
        df = self._recent_trips(ctx)

        if ctx.now.hour == 21:
            target = ctx.today.plus(14)
            big_rate = self._rate(ctx, df, ("day_1_5", "overnight", "three_quarter"))
            if (
                big_rate >= PTO_TRIGGER_RATE
                and not target.is_weekend
                and not target.is_holiday
                and ctx.pto_left > PTO_RESERVE
            ):
                actions.append(
                    CommitPTO(target, f"recent big-trip rate {big_rate:.2f}, bet bite holds 14d out")
                )

        for cls, classes in CLASS_PRIORITY:
            rate = self._rate(ctx, df, classes)
            if rate <= 0:
                continue
            offer = ctx.offer(cls)
            if offer is None or not offer.bookable:
                continue
            if ctx.budget_left - offer.cost < BUDGET_RESERVE:
                continue
            boat = ctx.pick_boat(offer.cls, offer.departure)
            actions.append(Book(offer.id, f"recent {cls} yt/angler={rate:.2f}", boat=boat))
            break

        return actions
