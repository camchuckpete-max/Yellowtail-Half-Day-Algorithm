"""Momentum strategy: react to what the fleet caught in the last one to few days.

Persona: "yesterday tells you tomorrow." No weather, no oceanography, just recent
pooled yellowtail-per-angler. React fast, stop after skunks. Twilight trips never
cost PTO, so they are booked on signal alone; weekday half/full-day trips need PTO
committed 14 days ahead, funded selectively from a recent-momentum proxy so as not
to burn the season's 10 PTO days on speculation before the likely peak window.
"""
import pandas as pd
from arena.api.ctx import Strategy, Book, CommitPTO

CHEAP_CLASSES = {"hd_am", "hd_pm", "hd_unspecified", "hd_twilight", "three_quarter", "full_day"}
PREMIUM_CLASSES = {"day_1_5", "overnight"}
HOT_RATE = 0.3
PEAK_DOY_START = 160
PEAK_DOY_END = 305
PTO_RESERVE_OUTSIDE_PEAK = 5
OUTSIDE_PEAK_HOT_RATE = 0.12
CHEAP_PRIORITY = ("HD_PM", "HD_AM", "THREE_QUARTER", "FULL_DAY")
BIG_TRIP_BONUS_PRIORITY = ("THREE_QUARTER", "FULL_DAY")
PREMIUM_PRIORITY = ("DAY_1_5", "OVERNIGHT")


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather. Pools yellowtail kept+released per angler "
            "over the last 2 days on half-day/twilight/three-quarter/full-day trips, "
            "and separately over the last 3 days on overnight/1.5-day trips. A positive "
            "cheap-trip rate books the next bookable offer, in order HD_PM, HD_AM, "
            "THREE_QUARTER, FULL_DAY; a hot rate (>=0.3) on a weekend/holiday adds a "
            "three-quarter or full-day trip too, at no extra PTO cost. Twilight is "
            "booked on the same signal whenever bookable, since it never costs PTO. "
            "A positive premium rate books the next bookable 1.5-day or overnight "
            "trip. Weekday PTO for the date 14 days out is committed when the pooled "
            "3-day rate at commit time is positive inside day-of-year 160-305 (the "
            "presumed local peak), or hot (>=0.12) outside it while keeping a 5-day "
            "reserve for that peak window. Every booking checks affordability and "
            "uses the default scheduled-boat picker. A run of skunks stops booking "
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

    def _book_if_bookable(self, ctx, actions, cls, reason, taken_ids):
        offer = ctx.offer(cls)
        if offer is None or not offer.bookable or offer.id in taken_ids:
            return None
        if offer.cost > ctx.budget_left:
            return None
        boat = ctx.pick_boat(offer.cls, offer.departure)
        actions.append(Book(offer.id, reason, boat=boat))
        taken_ids.add(offer.id)
        return offer

    def decide(self, ctx):
        actions = []
        taken_ids = set()

        if ctx.now.hour == 21:
            target = ctx.today.plus(14)
            if not target.is_weekend and not target.is_holiday:
                trend = self._rate(ctx, CHEAP_CLASSES | PREMIUM_CLASSES, 3)
                in_peak = PEAK_DOY_START <= target.doy <= PEAK_DOY_END
                ok = (trend > 0) if in_peak else (
                    trend >= OUTSIDE_PEAK_HOT_RATE and ctx.pto_left > PTO_RESERVE_OUTSIDE_PEAK
                )
                if ok and ctx.pto_left > 0:
                    actions.append(
                        CommitPTO(target, f"recent rate {trend:.2f}, funding weekday PTO for {target}")
                    )

            rate = self._rate(ctx, CHEAP_CLASSES, 2)
            if rate > 0:
                booked = None
                for cls in CHEAP_PRIORITY:
                    booked = self._book_if_bookable(
                        ctx, actions, cls, f"pooled recent yt/angler={rate:.2f} on {cls}", taken_ids
                    )
                    if booked:
                        break
                if rate >= HOT_RATE:
                    for cls in BIG_TRIP_BONUS_PRIORITY:
                        offer = ctx.offer(cls)
                        if (
                            offer is not None
                            and offer.bookable
                            and offer.id not in taken_ids
                            and offer.cost <= ctx.budget_left
                            and (offer.departure.is_weekend or offer.departure.is_holiday)
                        ):
                            boat = ctx.pick_boat(offer.cls, offer.departure)
                            actions.append(
                                Book(offer.id, f"hot rate {rate:.2f}, no-PTO day, add {cls}", boat=boat)
                            )
                            taken_ids.add(offer.id)
                            break

        if ctx.now.hour == 16:
            cheap_rate_today = self._rate(ctx, CHEAP_CLASSES, 2)
            if cheap_rate_today > 0:
                self._book_if_bookable(
                    ctx, actions, "TWILIGHT",
                    f"pooled recent yt/angler={cheap_rate_today:.2f}, twilight (no PTO)", taken_ids
                )

            premium_rate = self._rate(ctx, PREMIUM_CLASSES, 3)
            if premium_rate > 0:
                for cls in PREMIUM_PRIORITY:
                    if self._book_if_bookable(
                        ctx, actions, cls,
                        f"pooled recent premium yt/angler={premium_rate:.2f} on {cls}", taken_ids
                    ):
                        break

        return actions
