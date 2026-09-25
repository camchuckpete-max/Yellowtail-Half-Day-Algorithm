"""Momentum strategy: react to what the fleet caught in the last one to few days.

Persona: "yesterday tells you tomorrow." No weather, no oceanography beyond the
fleet's own counts. Two lessons learned from season 1: (1) a class must clear a
lifetime yellowtail-per-angler bar before it is even considered, so structurally
weak classes (half-day AM/PM, twilight) are never chased on noise; (2) "recent
rate is merely positive" is too weak a trigger and burns budget on marginal
trades all season, leaving nothing for the rare, very hot windows. So a class is
only booked when its trailing 2-3 day rate is meaningfully above its own
lifetime baseline (hot), not just non-zero. That bar is relaxed for a class
when the fleet's full history (only fully-completed prior seasons) shows this
day-of-year has historically run far above that class's baseline -- a
seasonality tilt computed fresh from data each tick, not a fixed date range --
so we are quicker to swing during a recurring hot stretch and more patient
elsewhere. A dollar reserve is kept back from cheap-class trades at all times
so budget cannot run out early the way it did in season 1. Twilight is booked
(no PTO) only on its own rate; premium (overnight/1.5-day) and cheap
(three-quarter/half-day) classes are evaluated separately so a hot premium
class is not diluted by a cold cheap one. Weekday PTO 14 days out is funded
only by an actually-hot signal, with a bigger reserve kept than before. Every
booking is checked against the real sailing schedule and budget; among
scheduled boats we pick whichever has the best lifetime rate for that class.
"""
import pandas as pd
from arena.api.ctx import Strategy, Book, CommitPTO

CLASS_TRIPS_MAP = {
    "HD_AM": {"hd_am"},
    "HD_PM": {"hd_pm", "hd_unspecified"},
    "TWILIGHT": {"hd_twilight"},
    "THREE_QUARTER": {"three_quarter"},
    "FULL_DAY": {"full_day"},
    "OVERNIGHT": {"overnight"},
    "DAY_1_5": {"day_1_5"},
}
CHEAP_OFFER_CLASSES = ("HD_AM", "HD_PM", "THREE_QUARTER", "FULL_DAY")
PREMIUM_OFFER_CLASSES = ("OVERNIGHT", "DAY_1_5")
PTO_RESERVE = 2
BOAT_MIN_ANGLERS = 30
CLASS_MIN_ANGLERS = 200
CLASS_MIN_RATE = 0.05
HOT_MULTIPLIER = 1.5
HOT_MULTIPLIER_IN_SEASON = 0.8
SEASONAL_BOOST_FACTOR = 2.0
SEASONAL_WINDOW_DAYS = 15
MIN_ABS_RATE_COLD = 0.10
CHEAP_RESERVE_FLOOR = 700.0


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather. A class must first clear a lifetime "
            "yellowtail-per-angler bar (once enough samples exist) to be "
            "considered at all, excluding structurally weak classes (half-day "
            "AM/PM, twilight) regardless of short-term noise. Among classes "
            "that clear the bar, tracks yellowtail per angler over the last 2-3 "
            "days per class and only books when that rate is meaningfully above "
            "the class's own lifetime baseline (hot), not merely positive, since "
            "positive-only booking drained budget on marginal trades in season "
            "1. That hot bar is relaxed when fully-completed prior seasons show "
            "this day-of-year historically ran far above baseline for that "
            "class, a seasonality tilt recomputed from data each tick rather "
            "than a fixed date. A dollar reserve is always kept back from "
            "cheap-class trades so budget cannot run dry early. At 21:00 books "
            "tomorrow's best hot cheap-class offer; at 16:00 books twilight on "
            "its own rate (no PTO) and the better hot premium (overnight/1.5-"
            "day) class. Weekday PTO 14 days out, with a 2-day reserve, is "
            "committed only on an actually-hot signal. Bookings are checked "
            "against the real sailing schedule and budget; among scheduled "
            "boats picks the one with the best lifetime rate for that class."
        )

    def on_turn(self, ctx):
        pass

    def _trips_df(self, ctx):
        rows = ctx.observe("trips")
        if rows is None:
            return None
        df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
        if df.empty or "cls" not in df.columns:
            return None
        return df

    def _rate(self, ctx, classes, days_back):
        df = self._trips_df(ctx)
        if df is None:
            return 0.0
        df = df[df["cls"].isin(classes)]
        if df.empty:
            return 0.0
        season = ctx.today.season
        end_doy = ctx.today.doy
        doys = set(range(end_doy - days_back + 1, end_doy + 1))
        df = df[(df["fished_date_season"] == season) & (df["fished_date_doy"].isin(doys))]
        if df.empty:
            return 0.0
        anglers = df["anglers"].sum()
        if anglers <= 0:
            return 0.0
        return float(df["yt"].sum() / anglers)

    def _baseline_rate(self, ctx, classes):
        df = self._trips_df(ctx)
        if df is None:
            return 0.0, 0.0
        df = df[df["cls"].isin(classes)]
        if df.empty:
            return 0.0, 0.0
        anglers = df["anglers"].sum()
        if anglers <= 0:
            return 0.0, 0.0
        return float(df["yt"].sum() / anglers), float(anglers)

    def _class_viable(self, ctx, classes):
        rate, anglers = self._baseline_rate(ctx, classes)
        if anglers < CLASS_MIN_ANGLERS:
            return True
        return rate >= CLASS_MIN_RATE

    def _seasonal_factor(self, ctx, classes):
        df = self._trips_df(ctx)
        if df is None:
            return 1.0
        df = df[df["cls"].isin(classes) & (df["fished_date_season"] < ctx.today.season)]
        if df.empty:
            return 1.0
        anglers = df["anglers"].sum()
        if anglers < CLASS_MIN_ANGLERS:
            return 1.0
        baseline = float(df["yt"].sum() / anglers)
        if baseline <= 0:
            return 1.0
        today_doy = ctx.today.doy
        dist = (df["fished_date_doy"] - today_doy).abs()
        dist = dist.combine(365 - dist, min)
        window = df[dist <= SEASONAL_WINDOW_DAYS]
        wanglers = window["anglers"].sum()
        if wanglers < BOAT_MIN_ANGLERS:
            return 1.0
        wrate = float(window["yt"].sum() / wanglers)
        return wrate / baseline

    def _is_hot(self, ctx, classes, recent_rate):
        baseline, anglers = self._baseline_rate(ctx, classes)
        if anglers < CLASS_MIN_ANGLERS:
            return recent_rate > MIN_ABS_RATE_COLD
        seasonal = self._seasonal_factor(ctx, classes)
        mult = HOT_MULTIPLIER_IN_SEASON if seasonal >= SEASONAL_BOOST_FACTOR else HOT_MULTIPLIER
        bar = max(baseline * mult, MIN_ABS_RATE_COLD)
        return recent_rate > bar

    def _best_boat(self, ctx, offer_cls, fish_day, scheduled):
        default = ctx.pick_boat(offer_cls, fish_day)
        if not scheduled:
            return default
        fallback = default if default in scheduled else scheduled[0]
        df = self._trips_df(ctx)
        if df is None or "boat" not in df.columns:
            return fallback
        df = df[df["cls"].isin(CLASS_TRIPS_MAP[offer_cls])]
        df = df[df["boat"].isin(scheduled)]
        if df.empty:
            return fallback
        grp = df.groupby("boat").agg(anglers=("anglers", "sum"), yt=("yt", "sum"))
        grp = grp[grp["anglers"] >= BOAT_MIN_ANGLERS]
        if grp.empty:
            return fallback
        grp["rate"] = grp["yt"] / grp["anglers"]
        return grp["rate"].idxmax()

    def _book_if_bookable(self, ctx, actions, cls, reason, taken_ids, reserve=0.0):
        offer = ctx.offer(cls)
        if offer is None or not offer.bookable or offer.id in taken_ids:
            return None
        if offer.cost > ctx.budget_left - reserve:
            return None
        fdates = offer.fishing_dates
        if fdates:
            fish_day = fdates[0] if isinstance(fdates, (list, tuple)) else fdates
        else:
            fish_day = offer.departure
        boats = ctx.scheduled_boats(offer.cls, fish_day)
        if not boats:
            return None
        boat = self._best_boat(ctx, cls, fish_day, boats)
        actions.append(Book(offer.id, reason, boat=boat))
        taken_ids.add(offer.id)
        return offer

    def decide(self, ctx):
        actions = []
        taken_ids = set()

        cheap_classes = [oc for oc in CHEAP_OFFER_CLASSES if self._class_viable(ctx, CLASS_TRIPS_MAP[oc])]
        premium_classes = [oc for oc in PREMIUM_OFFER_CLASSES if self._class_viable(ctx, CLASS_TRIPS_MAP[oc])]

        if ctx.now.hour == 21:
            cheap_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in cheap_classes}
            hot_cheap = {oc: r for oc, r in cheap_rates.items() if self._is_hot(ctx, CLASS_TRIPS_MAP[oc], r)}
            best_overall_hot = False
            if hot_cheap:
                best_cheap = max(hot_cheap, key=hot_cheap.get)
                self._book_if_bookable(
                    ctx, actions, best_cheap,
                    f"hot {best_cheap} yt/angler={hot_cheap[best_cheap]:.2f}, best of {hot_cheap}",
                    taken_ids, reserve=CHEAP_RESERVE_FLOOR,
                )
                best_overall_hot = True

            premium_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in premium_classes}
            if any(self._is_hot(ctx, CLASS_TRIPS_MAP[oc], r) for oc, r in premium_rates.items()):
                best_overall_hot = True

            target = ctx.today.plus(14)
            if not target.is_weekend and not target.is_holiday:
                if best_overall_hot and ctx.pto_left > PTO_RESERVE:
                    actions.append(
                        CommitPTO(target, f"hot signal on {target}, funding weekday PTO")
                    )

        if ctx.now.hour == 16:
            if self._class_viable(ctx, CLASS_TRIPS_MAP["TWILIGHT"]):
                twilight_rate = self._rate(ctx, CLASS_TRIPS_MAP["TWILIGHT"], 3)
                if self._is_hot(ctx, CLASS_TRIPS_MAP["TWILIGHT"], twilight_rate):
                    self._book_if_bookable(
                        ctx, actions, "TWILIGHT",
                        f"twilight's own hot rate yt/angler={twilight_rate:.2f} (no PTO)", taken_ids
                    )

            if premium_classes:
                premium_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in premium_classes}
                hot_premium = {oc: r for oc, r in premium_rates.items() if self._is_hot(ctx, CLASS_TRIPS_MAP[oc], r)}
                if hot_premium:
                    best_premium = max(hot_premium, key=hot_premium.get)
                    self._book_if_bookable(
                        ctx, actions, best_premium,
                        f"hot {best_premium} yt/angler={hot_premium[best_premium]:.2f}, best of {hot_premium}",
                        taken_ids,
                    )

        return actions
