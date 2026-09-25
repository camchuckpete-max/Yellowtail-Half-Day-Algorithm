"""
Season 2: fix early-season capital bleed + add water temperature gate from temp_first's strategy.
Season 1 root cause: wasted $1,960 on d35-71 dead zone with zero volume-based recovery.
Fix: (1) seasonal gate (skip d1-71), (2) water-temp gate (Scripps >= 59°F), (3) momentum-driven d72+.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd
import numpy as np


class Strategy(Strategy):
    name = "Thermal + seasonal gates: water temp >= 59°F, avoid dead zone, deploy d240+ on momentum."

    def describe(self) -> str:
        return (
            "Two gates prevent dead-zone capital bleed. (1) Seasonal: never book d1-71. "
            "(2) Thermal: 7-day mean Scripps Pier water temp must be >= 59°F (colder water has shown ~0 yellowtail). "
            "Within gates, deploy momentum-driven: proven classes only (day_1_5, overnight, three_quarter). "
            "Early season (d72-239): hold $600, book if 3-day momentum >= 0.1 YT/angler. "
            "Fall peak (d240-310): hold $200, book aggressively if momentum >= 0.2 YT/angler. "
            "PTO committed 14 days ahead in fall peak window (d226+). "
            "Boat selection: pick_boat default, except three_quarter prefers San Diego/Malihini if scheduled."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th). Cache or refit as needed."""
        pass

    def decide(self, ctx) -> list:
        """Gates: (1) seasonal d1-71, (2) water temp >= 59°F, then momentum-driven within proven classes."""
        actions = []

        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        doy = ctx.tomorrow.doy

        # GATE 1: Seasonal dead zone d1-71 is forbidden
        if doy < 72:
            return actions

        # GATE 2: Water temperature. Scripps Pier 7-day mean must be >= 59°F (~15°C)
        pier = ctx.observe("pier")
        if not pier.empty:
            # Pier data is hourly. Get last 7 days of Scripps Pier water temps (wtmp_c)
            recent_pier = pier[pier["ts_t"] >= (ctx.now.t - 7)]
            if not recent_pier.empty:
                mean_temp_c = recent_pier["wtmp_c"].mean()
                mean_temp_f = (mean_temp_c * 9/5) + 32
                # temp_first uses 59°F as gate; respect that signal
                if mean_temp_f < 59:
                    return actions  # Water too cold, skip
            # If no recent pier data, proceed (assume bookable)

        # Reserve strategy: high early, drop in peak season
        if doy < 240:
            min_reserve = 600
        else:
            min_reserve = 200

        # Budget gate
        if ctx.budget_left <= min_reserve:
            return actions

        # Classes: day_1_5, overnight, three_quarter (proven high per-angler yields)
        proven_classes = ["day_1_5", "overnight", "three_quarter"]

        # Momentum lookback: 3-day early, 7-day in peak
        if doy < 240:
            lookback_days = 3
            momentum_threshold = 0.1
        else:
            lookback_days = 7
            momentum_threshold = 0.2

        recent_cutoff = ctx.now.t - lookback_days
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]

        # Calculate YT per angler per class
        class_performance = {}
        for cls in proven_classes:
            cls_trips = recent_trips[recent_trips["cls"] == cls]
            if not cls_trips.empty:
                total_yt = cls_trips["yt"].sum()
                total_anglers = cls_trips["anglers"].sum()
                class_performance[cls] = total_yt / total_anglers if total_anglers > 0 else 0
            else:
                class_performance[cls] = 0

        # Pick best class that meets threshold
        best_class = None
        best_signal = -999
        for cls in proven_classes:
            if class_performance[cls] >= momentum_threshold and class_performance[cls] > best_signal:
                best_signal = class_performance[cls]
                best_class = cls

        if best_class is None:
            return actions

        # Map to offer code
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
                    # Boat selection: prefer San Diego/Malihini for three_quarter, else pick_boat
                    if best_class == "three_quarter":
                        preferred = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                        boat = preferred[0] if preferred else boats[0]
                    else:
                        boat = ctx.pick_boat(offer_cls, ctx.tomorrow)

                    reason = f"d{doy:03d}: {best_class} {best_signal:.3f} YT/angler (temp+seasonal gates)"
                    actions.append(Book(offer.id, reason, boat=boat))

                    # Commit PTO 14 days ahead in fall peak window (d226-310)
                    if offer.pto_dates and ctx.pto_left > 0 and doy >= 226:
                        future_day = ctx.today.plus(14)
                        if 240 <= future_day.doy <= 310 and future_day.doy < 366:
                            already_committed = [d for d in ctx.calendar.get("committed_pto", [])]
                            future_str = f"S{future_day.season:02d} d{future_day.doy:03d}"
                            if future_str not in already_committed:
                                actions.append(CommitPTO(future_day, reason=f"Fall peak PTO, d{doy:03d} booking"))

                    return actions

        return actions