"""
Season 2: fix early-season capital bleed. Deploy only on proven seasonal windows with strict discipline.
Season 1 root cause: submitted seasonal-window strategy too late, after wasting $1,960 (d35-71, dead zone).
Fix: start Season 2 with correct gates from day 1. Never touch d1-71. Hold $600 until d240 then deploy.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd


class Strategy(Strategy):
    name = "Seasonal discipline: no dead zone, deploy d240+."

    def describe(self) -> str:
        return (
            "Season 1 revealed: d35-71 (dead zone) averaged 0.001 YT/angler; d240-310 (fall peak) averaged 1.2 YT/angler. "
            "Primary gate: never book d1-71. Secondary gate: proven classes only (day_1_5, overnight, three_quarter). "
            "Early season (d72-239): hold $600 reserve; book only if 3-day momentum > 0.1 YT/angler. "
            "Fall peak (d240-310): hold $200 reserve; book aggressively on momentum > 0.2 YT/angler. "
            "Commit PTO 14 days ahead in fall window (d226 onwards). "
            "Boat selection: three_quarter prefers San Diego/Malihini; others use pick_boat."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th). Cache or refit as needed."""
        pass

    def decide(self, ctx) -> list:
        """Strict seasonal discipline: no dead zone, proven classes only, momentum-driven within gates."""
        actions = []

        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        doy = ctx.tomorrow.doy

        # PRIMARY GATE: dead zone d1-71 is forbidden. Never book it.
        if doy < 72:
            return actions

        # Reserve strategy: high early, drop in peak season
        if doy < 240:
            min_reserve = 600
        else:
            min_reserve = 200

        # If reserve would go negative, don't book
        if ctx.budget_left <= min_reserve:
            return actions

        # Secondary gate: proven classes (d72+ is too early for overnight/day_1_5 historically; use all three)
        proven_classes = ["day_1_5", "overnight", "three_quarter"]

        # Momentum lookback: 3-day early season, 7-day in peak (to avoid noise)
        if doy < 240:
            lookback_days = 3
            momentum_threshold = 0.1  # Low bar early season (d72-239)
        else:
            lookback_days = 7
            momentum_threshold = 0.2  # Stricter in peak season (d240+)

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

        # Map class to offer code
        offer_map = {
            "three_quarter": "THREE_QUARTER",
            "overnight": "OVERNIGHT",
            "day_1_5": "DAY_1_5",
        }

        offer_cls = offer_map[best_class]
        offer = ctx.offer(offer_cls)

        if offer and offer.bookable:
            # Double-check budget after booking
            if ctx.budget_left - offer.cost >= min_reserve:
                boats = ctx.scheduled_boats(offer_cls, ctx.tomorrow)
                if boats:
                    # Prefer specific boats for three_quarter
                    if best_class == "three_quarter":
                        preferred = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                        boat = preferred[0] if preferred else boats[0]
                    else:
                        boat = ctx.pick_boat(offer_cls, ctx.tomorrow)

                    reason = f"d{doy:03d}: {best_class} momentum {best_signal:.3f} YT/angler (seasonal d72+)"
                    actions.append(Book(offer.id, reason, boat=boat))

                    # Commit PTO 14 days ahead if in fall peak window (d226-310)
                    # This ensures we have PTO available for fall trips when they become bookable
                    if offer.pto_dates and ctx.pto_left > 0 and doy >= 226:
                        future_day = ctx.today.plus(14)
                        # Only commit if the future day is within the fall window and not yet committed
                        if 240 <= future_day.doy <= 310 and future_day.doy < 366:
                            already_committed = [d for d in ctx.calendar.get("committed_pto", [])]
                            future_str = f"S{future_day.season:02d} d{future_day.doy:03d}"
                            if future_str not in already_committed:
                                actions.append(CommitPTO(future_day, reason=f"Fall peak PTO, d{doy:03d} booking"))

                    return actions

        return actions
