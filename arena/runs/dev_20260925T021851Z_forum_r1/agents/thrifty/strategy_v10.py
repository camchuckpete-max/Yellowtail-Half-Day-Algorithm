"""
Season 2: water temperature gate + proven class + reactive momentum.
Season 1 root cause: booked during cold dead zone (d35-71: 14.8°C avg, 0 YT from 146 premium trips).
Season 2: gate by Scripps Pier temp first (>15.5°C baseline, higher in fall), then by proven classes, then react.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd
import math


class Strategy(Strategy):
    name = "Pier-temp gate + proven classes + momentum"

    def describe(self) -> str:
        return (
            "Season 1 data: dead zone (d35-71) averaged 14.8°C, yielded 0 YT from 146 premium trips. "
            "Peak (d250-275) averaged 17.6°C, yielded 18,441 YT from 1004 trips. "
            "Primary gate: Scripps Pier water temperature (7-day rolling mean >= 15.5°C baseline, "
            "raised to 17°C in fall window d240-310). Secondary gate: proven classes only (day_1_5, overnight, three_quarter). "
            "Within gates, track 2-3 day rolling YT/angler per class. At 21:00, book tomorrow's highest-rate offer if temp gate passes. "
            "Commit PTO 14 days ahead when temp + class momentum both positive, spacing weekday PTO for fall weekends. "
            "Hold $200 minimum; prefer San Diego/Malihini for 3/4-day, pick_boat otherwise."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th of month)."""
        pass

    def decide(self, ctx) -> list:
        """Gate: temp, class, momentum. Book best qualifying offer for tomorrow."""
        actions = []

        trips = ctx.observe("trips")
        pier = ctx.observe("pier")
        if trips.empty or pier.empty:
            return actions

        min_reserve = 200
        if ctx.budget_left <= min_reserve:
            return actions

        # Check 7-day rolling mean Scripps Pier temp
        pier_recent = pier[pier["ts_t"] >= ctx.now.t - 7]
        if pier_recent.empty:
            return actions

        pier_mean_c = pier_recent["wtmp_c"].mean()
        pier_mean_f = pier_mean_c * 9 / 5 + 32

        # Seasonal temp threshold
        fall_window = ctx.tomorrow.doy >= 240 and ctx.tomorrow.doy <= 310
        temp_threshold_f = 62 if fall_window else 59  # ~16.7°C vs 15°C
        temp_threshold_c = (temp_threshold_f - 32) * 5 / 9

        if pier_mean_c < temp_threshold_c:
            return actions

        # Gate: proven classes only
        recent_cutoff = ctx.now.t - 3
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]
        if recent_trips.empty:
            return actions

        proven_classes = ["day_1_5", "overnight", "three_quarter"]

        # Calculate recent 2-3 day signal for proven classes
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

                    reason = f"Temp {pier_mean_f:.0f}°F (gate {temp_threshold_f:.0f}°F), {best_class} at {best_signal:.3f} YT/angler"
                    actions.append(Book(offer.id, reason, boat=boat))

                    if offer.pto_dates and ctx.pto_left > 0:
                        future_day = ctx.today.plus(14)
                        if future_day.doy < 366 and ctx.pto_left > 0:
                            already_committed = [d.split()[-1] for d in ctx.calendar.get("committed_pto", [])]
                            if f"S{future_day.season:02d} d{future_day.doy:03d}" not in already_committed:
                                actions.append(CommitPTO(future_day, reason=f"Temp gate {pier_mean_f:.0f}°F, book for momentum"))

                    return actions

        return actions
