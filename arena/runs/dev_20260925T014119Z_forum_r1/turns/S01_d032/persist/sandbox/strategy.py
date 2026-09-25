"""Reactive yellowtail strategy: follow recent fleet catches by trip class.

PTO must be committed 14 days ahead, before any bite signal for that date can exist, so PTO
commitment is driven by historical day-of-year seasonality from public past trips, while actual
trip booking reacts to the last few days of real catches once an offer is inside its booking
window.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import numpy as np

LOOKBACK_DAYS = 3
PTO_LEAD = 14
HIST_HALF_WINDOW = 10
PTO_RESERVE = 2
SEASON_YT_RATE = 0.05
MIN_HIST_TRIPS = 10

CLASS_TRIP_COLS = {
    "HD_AM": ("hd_am",),
    "HD_PM": ("hd_pm", "hd_unspecified"),
    "TWILIGHT": ("hd_twilight",),
    "THREE_QUARTER": ("three_quarter",),
    "FULL_DAY": ("full_day",),
    "OVERNIGHT": ("overnight",),
    "DAY_1_5": ("day_1_5",),
}


class Strategy(Strategy):
    name = "yesterday-tells-tomorrow"

    def describe(self):
        return (
            "Reactive yellowtail strategy. Each tick sums yellowtail (yt) caught fleet-wide over "
            "the last 3 fished days, by trip class; a class counts as hot only when that sum is "
            "positive, so it cools off within a few skunk days. Offers are booked when their class "
            "is hot and the offer is already marked bookable (which itself reflects budget, PTO "
            "and schedule rules), using the boat that has run that class most in the last 60 days. "
            "Because PTO must be committed 14 days before a trip, before any bite signal for that "
            "date can exist, PTO for a weekday 14 days out is pre-committed instead from historical "
            "day-of-year seasonality: only when trips fished within 10 days of that day-of-year in "
            "past seasons averaged more than 0.05 yellowtail per trip over at least 10 trips, and "
            "only while a small PTO reserve is kept aside. Weekend, holiday and twilight trips never "
            "need PTO and are booked whenever hot. All actions are skipped quietly on missing data."
        )

    def _hot_offer_classes(self, ctx):
        try:
            trips = ctx.observe("trips")
            if trips is None or len(trips) == 0:
                return set()
            cutoff = ctx.now.t - LOOKBACK_DAYS
            recent = trips[trips["fish_date_t"] > cutoff]
            if len(recent) == 0:
                return set()
            sums = recent.groupby("cls")["yt"].sum()
            hot_trip_cls = set(sums[sums > 0].index)
            return {
                oc for oc, tcs in CLASS_TRIP_COLS.items() if any(tc in hot_trip_cls for tc in tcs)
            }
        except Exception:
            return set()

    def _seasonal_pto_worth_it(self, ctx, target_doy):
        try:
            trips = ctx.observe("trips")
            if trips is None or len(trips) == 0:
                return False
            raw = (trips["fish_date_doy"] - target_doy).abs()
            circ = np.minimum(raw, 365 - raw)
            window = trips[circ <= HIST_HALF_WINDOW]
            if len(window) < MIN_HIST_TRIPS:
                return False
            return (window["yt"].sum() / len(window)) > SEASON_YT_RATE
        except Exception:
            return False

    def decide(self, ctx):
        actions = []

        try:
            if ctx.now.hour == 16:
                target = ctx.today.plus(PTO_LEAD)
                if not target.is_weekend and not target.is_holiday:
                    if ctx.pto_left > PTO_RESERVE and self._seasonal_pto_worth_it(ctx, target.doy):
                        actions.append(
                            CommitPTO(target, "day-of-year historically productive for yellowtail")
                        )
        except Exception:
            pass

        hot_offer_classes = self._hot_offer_classes(ctx)
        if not hot_offer_classes:
            return actions

        remaining_budget = ctx.budget_left
        for offer in ctx.offers:
            try:
                if offer.cls not in hot_offer_classes:
                    continue
                if not offer.bookable:
                    continue
                if offer.cost > remaining_budget:
                    continue
                boat = ctx.pick_boat(offer.cls, offer.departure)
                if not boat:
                    continue
                actions.append(Book(offer.id, "recent fleet catch nonzero for this class", boat=boat))
                remaining_budget -= offer.cost
            except Exception:
                continue

        return actions
