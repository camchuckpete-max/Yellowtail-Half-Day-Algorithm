"""Momentum strategy: react to what the fleet caught in the last one to few days.

Persona: "yesterday tells you tomorrow." No weather, no oceanography. A class
must first clear a minimum all-time yellowtail-per-angler bar (once enough
samples exist) to even be considered, so structurally weak classes are not
chased on noise; among classes that clear the bar, recent (2-3 day) rate is
tracked separately per class so a hot class is not diluted by dead ones.
Twilight trips never cost PTO, so they are booked on their own signal alone;
weekday trips need PTO committed 14 days ahead, funded from the same recent-
momentum proxy. Every booking is checked against the actual sailing schedule
so we never try to book a boat that is not running that class that day, and
among the boats actually scheduled we pick the one with the best historical
yellowtail-per-angler rate for that class (computed fresh from observed trip
data each time, not a hardcoded name).
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
PTO_RESERVE = 1
BOAT_MIN_ANGLERS = 30
CLASS_MIN_ANGLERS = 200
CLASS_MIN_RATE = 0.05


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather. Before a class is even considered, "
            "its all-time pooled yellowtail-per-angler rate (once enough samples "
            "exist) must clear a minimum bar, so structurally weak classes are "
            "excluded regardless of short-term noise; data so far shows half-day "
            "AM/PM and twilight trips near zero all season while three-quarter, "
            "overnight and 1.5-day are real earners. Among classes clearing the "
            "bar, tracks yellowtail per angler over the last 2-3 days separately "
            "per class, so a hot class is not diluted by dead ones. At 21:00, "
            "books tomorrow's bookable qualifying cheap-class offer with the best "
            "positive trailing rate. At 16:00, books today's twilight trip only "
            "on twilight's own recent rate (twilight never costs PTO either way), "
            "and books the better of overnight/1.5-day when its trailing rate is "
            "positive. Weekday PTO 14 days out is committed whenever the best "
            "trailing rate across qualifying classes is positive, keeping a 1-day "
            "reserve. Every booking is checked against the real sailing schedule "
            "and against budget. Among boats actually scheduled, picks whichever "
            "has the best all-time yellowtail-per-angler rate for that class "
            "(recomputed from observed trips each tick, minimum sample required), "
            "falling back to the most-recently-active scheduled boat otherwise."
        )

    def on_turn(self, ctx):
        pass

    def _rate(self, ctx, classes, days_back):
        rows = ctx.observe("trips")
        if rows is None:
            return 0.0
        df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
        if df.empty or "cls" not in df.columns:
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

    def _class_viable(self, ctx, classes):
        rows = ctx.observe("trips")
        if rows is None:
            return True
        df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
        if df.empty or "cls" not in df.columns:
            return True
        df = df[df["cls"].isin(classes)]
        if df.empty:
            return True
        anglers = df["anglers"].sum()
        if anglers < CLASS_MIN_ANGLERS:
            return True
        return float(df["yt"].sum() / anglers) >= CLASS_MIN_RATE

    def _best_boat(self, ctx, offer_cls, fish_day, scheduled):
        default = ctx.pick_boat(offer_cls, fish_day)
        if not scheduled:
            return default
        fallback = default if default in scheduled else scheduled[0]
        rows = ctx.observe("trips")
        if rows is None:
            return fallback
        df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
        if df.empty or "cls" not in df.columns or "boat" not in df.columns:
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

    def _book_if_bookable(self, ctx, actions, cls, reason, taken_ids):
        offer = ctx.offer(cls)
        if offer is None or not offer.bookable or offer.id in taken_ids:
            return None
        if offer.cost > ctx.budget_left:
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
            premium_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in premium_classes}
            best_overall = 0.0
            if cheap_rates:
                best_cheap = max(cheap_rates, key=cheap_rates.get)
                if cheap_rates[best_cheap] > 0:
                    self._book_if_bookable(
                        ctx, actions, best_cheap,
                        f"recent {best_cheap} yt/angler={cheap_rates[best_cheap]:.2f}, best of {cheap_rates}",
                        taken_ids,
                    )
                best_overall = max(best_overall, max(cheap_rates.values()))
            if premium_rates:
                best_overall = max(best_overall, max(premium_rates.values()))

            target = ctx.today.plus(14)
            if not target.is_weekend and not target.is_holiday:
                if best_overall > 0 and ctx.pto_left > PTO_RESERVE:
                    actions.append(
                        CommitPTO(target, f"best recent trailing rate {best_overall:.2f}, funding weekday PTO for {target}")
                    )

        if ctx.now.hour == 16:
            if self._class_viable(ctx, CLASS_TRIPS_MAP["TWILIGHT"]):
                twilight_rate = self._rate(ctx, CLASS_TRIPS_MAP["TWILIGHT"], 3)
                if twilight_rate > 0:
                    self._book_if_bookable(
                        ctx, actions, "TWILIGHT",
                        f"twilight's own recent yt/angler={twilight_rate:.2f} (no PTO)", taken_ids
                    )

            if premium_classes:
                premium_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in premium_classes}
                best_premium = max(premium_rates, key=premium_rates.get)
                if premium_rates[best_premium] > 0:
                    self._book_if_bookable(
                        ctx, actions, best_premium,
                        f"recent {best_premium} yt/angler={premium_rates[best_premium]:.2f}, best of {premium_rates}",
                        taken_ids,
                    )

        return actions
