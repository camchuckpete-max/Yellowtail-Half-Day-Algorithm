"""Momentum strategy: react to what the fleet caught in the last one to few days.

Persona: "yesterday tells you tomorrow." No weather, no oceanography. A class
must first clear a minimum all-time yellowtail-per-angler bar (once enough
samples exist) to even be considered, so structurally weak classes are not
chased on noise; among classes that clear the bar, recent (2-3 day) rate is
tracked separately per class so a hot class is not diluted by dead ones. A
rate computed from too few observed anglers is treated as unproven (0), so a
single lucky boatload never reads as a real signal. Twilight trips never cost
PTO, so they are booked on their own signal alone. Premium classes
(overnight/1.5-day) earn far more fish per PTO day and per dollar than cheap
classes, so PTO is committed only on a real premium signal (never spent on
cheap-class noise), and both budget and PTO carry a reserve - large early in
the season, easing off only as the season winds down (a slower, sqrt-shaped
taper, not linear) - that cheap-class spending and even premium spending must
respect, so the whole budget/PTO stock can't be gone before a real signal
ever shows up. Every booking is checked against the actual sailing schedule
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
SEASON_LENGTH_DAYS = 365
BOAT_MIN_ANGLERS = 30
CLASS_MIN_ANGLERS = 150
CLASS_MIN_RATE = 0.05
MIN_SAMPLE_ANGLERS = 15
MIN_PREMIUM_RATE = 0.15
PTO_RESERVE_BASE = 7.0
BUDGET_RESERVE_BASE = 900.0


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather. A class must clear an all-time "
            "pooled yellowtail-per-angler bar (once enough samples exist) "
            "before being considered at all, excluding structurally weak "
            "classes regardless of short-term noise. A trailing rate built "
            "from too few observed anglers is treated as unproven (0), so a "
            "single lucky trip never passes for a real signal. At 21:00, "
            "books tomorrow's bookable qualifying cheap-class offer with "
            "the best positive trailing rate, but only if enough budget "
            "stays reserved for premium (overnight/1.5-day) trips, which "
            "pay far more fish per PTO day and per dollar. At 16:00, books "
            "today's twilight on its own recent rate (never costs PTO), "
            "and books the better of overnight/1.5-day when its trailing "
            "rate clears a real bar (not any positive noise), respecting "
            "the same budget reserve. Weekday PTO 14 days out is committed "
            "only on that same premium signal - never on cheap-class "
            "exploration - so PTO is not gone before a real opportunity "
            "appears. Budget and PTO reserves are large early and taper "
            "off slowly (not linearly) as the season winds down, so the "
            "stock can't be spent before a real signal shows up. Boats are "
            "chosen, among those scheduled, by best historical rate."
        )

    def on_turn(self, ctx):
        pass

    def _season_frac_left(self, ctx):
        return max(0.0, 1.0 - ctx.today.doy / SEASON_LENGTH_DAYS)

    def _budget_reserve(self, ctx):
        return BUDGET_RESERVE_BASE * (self._season_frac_left(ctx) ** 0.5)

    def _pto_reserve(self, ctx):
        return PTO_RESERVE_BASE * (self._season_frac_left(ctx) ** 0.5)

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
        if anglers < MIN_SAMPLE_ANGLERS:
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

    def _book_if_bookable(self, ctx, actions, cls, reason, taken_ids, min_leftover=0.0):
        offer = ctx.offer(cls)
        if offer is None or not offer.bookable or offer.id in taken_ids:
            return None
        if offer.cost > ctx.budget_left:
            return None
        if ctx.budget_left - offer.cost < min_leftover:
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
        budget_reserve = self._budget_reserve(ctx)

        if ctx.now.hour == 21:
            cheap_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in cheap_classes}
            premium_rates = {oc: self._rate(ctx, CLASS_TRIPS_MAP[oc], 3) for oc in premium_classes}
            if cheap_rates:
                best_cheap = max(cheap_rates, key=cheap_rates.get)
                if cheap_rates[best_cheap] > 0:
                    self._book_if_bookable(
                        ctx, actions, best_cheap,
                        f"recent {best_cheap} yt/angler={cheap_rates[best_cheap]:.2f}, best of {cheap_rates}",
                        taken_ids, min_leftover=budget_reserve,
                    )

            premium_best = max(premium_rates.values()) if premium_rates else 0.0
            target = ctx.today.plus(14)
            if not target.is_weekend and not target.is_holiday:
                pto_reserve = self._pto_reserve(ctx)
                if premium_best >= MIN_PREMIUM_RATE and ctx.pto_left - 1 >= pto_reserve:
                    actions.append(
                        CommitPTO(
                            target,
                            f"premium best={premium_best:.2f} clears bar {MIN_PREMIUM_RATE}, "
                            f"funding weekday PTO for {target} (reserve={pto_reserve:.1f})",
                        )
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
                if premium_rates[best_premium] >= MIN_PREMIUM_RATE:
                    self._book_if_bookable(
                        ctx, actions, best_premium,
                        f"recent {best_premium} yt/angler={premium_rates[best_premium]:.2f} clears bar, best of {premium_rates}",
                        taken_ids, min_leftover=budget_reserve,
                    )

        return actions
