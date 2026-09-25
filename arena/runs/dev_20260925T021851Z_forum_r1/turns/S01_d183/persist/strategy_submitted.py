"""Momentum strategy: react to what the fleet caught in the last one to few days.

Persona: "yesterday tells you tomorrow." No weather, no oceanography, just recent
pooled yellowtail-per-angler, tracked separately per trip class so a hot class
is not diluted by dead ones. Twilight trips never cost PTO, so they are booked
on signal alone; weekday half/full-day trips need PTO committed 14 days ahead,
funded from the same recent-momentum proxy. Every booking is checked against
the actual sailing schedule so we never try to book a boat that is not
running that class that day, and among the boats actually scheduled we pick
the one with the best historical yellowtail-per-angler rate for that class
(computed fresh from observed trip data each time, not a hardcoded name).
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
ALL_CHEAP_TRIPS_CLASSES = set().union(*(CLASS_TRIPS_MAP[c] for c in CHEAP_OFFER_CLASSES))
ALL_PREMIUM_TRIPS_CLASSES = set().union(*(CLASS_TRIPS_MAP[c] for c in PREMIUM_OFFER_CLASSES))
PTO_RESERVE = 1
BOAT_MIN_ANGLERS = 30


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather. Tracks yellowtail kept+released per "
            "angler over the last 2-3 days separately for each trip class (half "
            "day AM/PM, three-quarter, full day, twilight, overnight, 1.5-day), "
            "so a hot class is not diluted by dead ones. At 21:00, books tomorrow's "
            "bookable cheap-class offer with the best positive trailing rate. At "
            "16:00, books today's twilight trip whenever any cheap class shows a "
            "positive rate (twilight never costs PTO), and books the better of "
            "overnight/1.5-day when the premium trailing rate is positive. Weekday "
            "PTO for the date 14 days out is committed whenever the best trailing "
            "rate across all classes is positive, keeping a 1-day reserve. Every "
            "booking is checked against the actual sailing schedule for that class "
            "and fishing day and against budget. Among the boats actually scheduled, "
            "picks whichever has the best all-time yellowtail-per-angler rate for "
            "that class (recomputed from observed trips each tick, minimum sample "
            "size required), falling back to the most-recently-active scheduled "
            "boat if no boat has enough data. A run of skunks stops booking "
            "naturally since every signal only looks a few days back."
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

        if ctx.now.hour == 21:
            cheap_rates = {
                oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in CHEAP_OFFER_CLASSES
            }
            premium_rates = {
                oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in PREMIUM_OFFER_CLASSES
            }
            best_cheap = max(cheap_rates, key=cheap_rates.get)
            if cheap_rates[best_cheap] > 0:
                self._book_if_bookable(
                    ctx, actions, best_cheap,
                    f"recent {best_cheap} yt/angler={cheap_rates[best_cheap]:.2f}, best of {cheap_rates}",
                    taken_ids,
                )

            target = ctx.today.plus(14)
            if not target.is_weekend and not target.is_holiday:
                best_overall = max(max(cheap_rates.values()), max(premium_rates.values()))
                if best_overall > 0 and ctx.pto_left > PTO_RESERVE:
                    actions.append(
                        CommitPTO(target, f"best recent trailing rate {best_overall:.2f}, funding weekday PTO for {target}")
                    )

        if ctx.now.hour == 16:
            cheap_rate_today = self._rate(ctx, ALL_CHEAP_TRIPS_CLASSES, 2)
            if cheap_rate_today > 0:
                self._book_if_bookable(
                    ctx, actions, "TWILIGHT",
                    f"pooled recent yt/angler={cheap_rate_today:.2f}, twilight (no PTO)", taken_ids
                )

            premium_rates = {
                oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in PREMIUM_OFFER_CLASSES
            }
            best_premium = max(premium_rates, key=premium_rates.get)
            if premium_rates[best_premium] > 0:
                self._book_if_bookable(
                    ctx, actions, best_premium,
                    f"recent {best_premium} yt/angler={premium_rates[best_premium]:.2f}, best of {premium_rates}",
                    taken_ids,
                )

        return actions
