"""Momentum strategy: react to what the fleet caught in the last one to two days.

Persona: "yesterday tells you tomorrow." No weather, no oceanography, just recent
pooled yellowtail-per-angler on cheap half-day classes. React fast, stop after skunks.
"""
import pandas as pd
from arena.api.ctx import Strategy, Book, CommitPTO

PEAK_DOY_START = 150
PEAK_DOY_END = 300
PTO_RESERVE = 2  # never pre-commit below this many PTO days left
SIGNAL_CLASSES = {"hd_am", "hd_pm", "hd_unspecified", "hd_twilight", "three_quarter"}
HOT_RATE = 0.3
HALF_DAY_PRIORITY = ("HD_PM", "HD_AM", "THREE_QUARTER")
BIG_TRIP_PRIORITY = ("THREE_QUARTER", "FULL_DAY")


class Strategy(Strategy):
    name = "yesterday tells tomorrow"

    def describe(self):
        return (
            "Reactive momentum, no weather inputs. Each tick, pool yellowtail "
            "kept+released and anglers across half-day, twilight and three-quarter "
            "trips fished today and yesterday. If the pooled rate is above zero, book "
            "the next bookable offer from HD_PM, HD_AM, THREE_QUARTER (in that order). "
            "If the rate is hot (>=0.3 fish/angler) and the offer's departure is a "
            "weekend or holiday, also book a three-quarter or full-day offer if "
            "bookable, since it costs no extra PTO. A run of zero-catch days naturally "
            "stops all booking since the signal only looks back two days. Weekday PTO "
            "is pre-committed one day at a time, 14 days ahead, only for weekdays "
            "inside day-of-year 150-300 (the local peak season) and only while more "
            "than 2 PTO days remain, so weekday offers in that window have a chance to "
            "be bookable when a bite is confirmed, without spending PTO speculatively "
            "outside the season or down to zero. Boat choice always uses the default "
            "scheduled-boat picker (most recent boat to run that class)."
        )

    def on_turn(self, ctx):
        pass

    def _recent_rate(self, ctx):
        rows = ctx.observe("trips")
        if rows is None:
            return 0.0
        df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
        if df.empty or "cls" not in df.columns:
            return 0.0
        df = df[df["cls"].isin(SIGNAL_CLASSES)]
        if df.empty:
            return 0.0
        today_doy = ctx.today.doy
        today_season = ctx.today.season
        mask = (df["fished_date_season"] == today_season) & (
            df["fished_date_doy"].isin([today_doy, today_doy - 1])
        )
        df = df[mask]
        if df.empty:
            return 0.0
        anglers = df["anglers"].sum()
        if anglers <= 0:
            return 0.0
        return float(df["yt"].sum() / anglers)

    def decide(self, ctx):
        actions = []

        if ctx.now.hour == 21:
            target = ctx.today.plus(14)
            if (
                not target.is_weekend
                and not target.is_holiday
                and PEAK_DOY_START <= target.doy <= PEAK_DOY_END
                and ctx.pto_left > PTO_RESERVE
            ):
                actions.append(
                    CommitPTO(target, "pre-commit weekday PTO inside peak window for reactive booking")
                )

        rate = self._recent_rate(ctx)
        if rate > 0:
            booked_offer = None
            for cls in HALF_DAY_PRIORITY:
                offer = ctx.offer(cls)
                if offer is not None and offer.bookable:
                    boat = ctx.pick_boat(offer.cls, offer.departure)
                    actions.append(Book(offer.id, f"pooled recent yt/angler={rate:.2f} on {cls}", boat=boat))
                    booked_offer = offer
                    break

            if rate >= HOT_RATE:
                for cls in BIG_TRIP_PRIORITY:
                    offer = ctx.offer(cls)
                    if (
                        offer is not None
                        and offer.bookable
                        and (booked_offer is None or offer.id != booked_offer.id)
                        and (offer.departure.is_weekend or offer.departure.is_holiday)
                    ):
                        boat = ctx.pick_boat(offer.cls, offer.departure)
                        actions.append(
                            Book(offer.id, f"hot pooled rate {rate:.2f}, no-PTO day, add {cls}", boat=boat)
                        )
                        break

        return actions
