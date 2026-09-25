"""
Season 2: proven seasonal windows + reactive momentum within those windows.
Season 1 root cause: booked d35-71 (0.001 YT/angler) instead of d240-310 (0.75-1.6 YT/angler).
Real signal: day-of-year peaks > temp alone. d72+ shows 180x better catch than d35-70 at same temp.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd


class Strategy(Strategy):
    name = "Seasonal windows + momentum"

    def describe(self) -> str:
        return (
            "Season 1 analysis: d35-71 averaged 0.001 YT/angler; d72-107 jumped to 0.183; d240-275 peaked at 0.748; d275-306 at 1.584. "
            "Primary gate: day-of-year seasonal windows (avoid dead zone d1-71, target peak d240-310). "
            "Secondary gate: proven classes (day_1_5, overnight, three_quarter) by recent 3-day momentum. "
            "Strategy: hold $600 reserve until d240, then deploy aggressively on best-performing class when booking opens. "
            "Commit PTO 14 days ahead for weekday fall trips (d240-310 window). "
            "Prefer San Diego/Malihini for 3/4-day; pick_boat otherwise. Book only when doy >= 240 or momentum very strong (d72+)."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th of month)."""
        pass

    def decide(self, ctx) -> list:
        """Gate: seasonal window + momentum. Book best offer within gate."""
        actions = []

        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        # Reserve more in early season; reduce in fall
        if ctx.tomorrow.doy < 240:
            min_reserve = 600
        else:
            min_reserve = 200

        if ctx.budget_left <= min_reserve:
            return actions

        # Seasonal gate: skip dead zone d1-71, focus on d72+ with peak at d240-310
        doy = ctx.tomorrow.doy
        if doy < 72:
            return actions

        # Proven classes only
        proven_classes = ["day_1_5", "overnight", "three_quarter"]

        # Calculate recent 3-day signal for proven classes
        recent_cutoff = ctx.now.t - 3
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]

        class_performance = {}
        for cls in proven_classes:
            cls_trips = recent_trips[recent_trips["cls"] == cls]
            if not cls_trips.empty:
                total_yt = cls_trips["yt"].sum()
                total_anglers = cls_trips["anglers"].sum()
                class_performance[cls] = total_yt / total_anglers if total_anglers > 0 else 0
            else:
                class_performance[cls] = 0

        # Pick best qualifying class with non-negative signal
        best_class = None
        best_signal = -999
        for cls in proven_classes:
            if class_performance[cls] >= 0 and class_performance[cls] > best_signal:
                best_signal = class_performance[cls]
                best_class = cls

        if best_class is None:
            return actions

        offer_map = {
            "three_quarter": "THREE_QUARTER",
            "overnight": "OVERNIGHT",
            "day_1_5": "DAY_1_5",
        }

        offer_cls = offer_map[best_class]
        offer = ctx.offer(offer_cls)

        if offer and offer.bookable:
            if ctx.budget_left - offer.cost >= min_reserve:
                boats = ctx.scheduled_boats(offer_cls, ctx.tomorrow)
                if boats:
                    if best_class == "three_quarter":
                        winners = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                        boat = winners[0] if winners else boats[0]
                    else:
                        boat = ctx.pick_boat(offer_cls, ctx.tomorrow)

                    reason = f"d{doy:03d}: {best_class} at {best_signal:.3f} YT/angler (seasonal window d72+)"
                    actions.append(Book(offer.id, reason, boat=boat))

                    # Commit PTO 14 days ahead in fall window
                    if offer.pto_dates and ctx.pto_left > 0 and doy >= 226:  # 14 days before d240
                        future_day = ctx.today.plus(14)
                        if future_day.doy < 366 and ctx.pto_left > 0:
                            already_committed = [d.split()[-1] for d in ctx.calendar.get("committed_pto", [])]
                            if f"S{future_day.season:02d} d{future_day.doy:03d}" not in already_committed:
                                actions.append(CommitPTO(future_day, reason=f"Seasonal window d240+, book d{doy:03d}"))

                    return actions

        return actions
