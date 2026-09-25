"""
Thrifty Season 2: reactive momentum with volume discipline.
Season 1 lesson: extreme caution (>2.0 threshold) never triggered. New: book any positive 2-3 day signal.
Persona: favor cheap half-days for volume, but pick hot dates using recent data (like persist).
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd


class Strategy(Strategy):
    name = "Momentum volume: book positive 2-3 day signals, favor half-days"

    def describe(self) -> str:
        return (
            "Season 1 over-conservatism never triggered bookings. Switching to reactive momentum: "
            "track yellowtail per angler separately by class over last 2-3 days. "
            "Book tomorrow's cheapest offer with best positive rate (half-day first, then premium). "
            "At 16:00 also book today's twilight (no PTO cost) on any positive signal. "
            "Commit PTO 14 days ahead when any class shows positive momentum. "
            "Hold $200 minimum reserve; prefer San Diego/Malihini for 3/4-day, pick_boat otherwise. "
            "No fixed thresholds—react to all data-driven signals."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th of month)."""
        pass

    def decide(self, ctx) -> list:
        """Book on any positive 2-3 day signal; favor cheap classes."""
        actions = []

        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        # Minimal reserve: stay flexible to capitalize on hot windows
        min_reserve = 200
        if ctx.budget_left <= min_reserve:
            return actions

        # Calculate signals over last 2-3 days (like persist)
        recent_cutoff = ctx.now.t - 3
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]

        if recent_trips.empty:
            # No data yet; don't book
            return actions

        # Calculate YT per angler by class
        class_performance = {}
        for cls in ["hd_pm", "hd_am", "three_quarter", "overnight", "day_1_5", "hd_twilight"]:
            cls_trips = recent_trips[recent_trips["cls"] == cls]
            if not cls_trips.empty:
                total_yt = cls_trips["yt"].sum()
                total_anglers = cls_trips["anglers"].sum()
                if total_anglers > 0:
                    class_performance[cls] = total_yt / total_anglers
                else:
                    class_performance[cls] = 0
            else:
                class_performance[cls] = 0

        # Sort by performance (any positive or zero)
        sorted_classes = sorted(
            class_performance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Priority: cheap half-days first (favor volume), then premium
        priority_order = ["hd_pm", "hd_am", "three_quarter", "overnight", "day_1_5", "hd_twilight"]
        best_class = None
        for cls_name in priority_order:
            if class_performance[cls_name] >= 0:  # Any non-negative signal
                best_class = cls_name
                break

        if best_class is None:
            # All classes have negative signal; wait
            return actions

        # Try to book the best class for tomorrow
        offer_map = {
            "three_quarter": "THREE_QUARTER",
            "overnight": "OVERNIGHT",
            "day_1_5": "DAY_1_5",
            "hd_pm": "HD_PM",
            "hd_am": "HD_AM",
            "hd_twilight": "TWILIGHT",
        }

        offer_cls = offer_map[best_class]
        offer = ctx.offer(offer_cls)

        if offer and offer.bookable:
            # Verify budget
            if ctx.budget_left - offer.cost >= min_reserve:
                boats = ctx.scheduled_boats(offer_cls, ctx.tomorrow)
                if boats:
                    # Prefer proven boats for 3/4-day
                    if best_class == "three_quarter":
                        winners = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                        boat = winners[0] if winners else boats[0]
                    else:
                        boat = ctx.pick_boat(offer_cls, ctx.tomorrow)

                    reason = f"Momentum: {best_class} at {class_performance[best_class]:.3f} YT/angler (2-3d avg)"
                    actions.append(Book(offer.id, reason, boat=boat))

                    # Commit PTO 14 days ahead if signal is positive
                    if offer.pto_dates:
                        future_day = ctx.today.plus(14)
                        if future_day.doy < 366:  # Stay in-season
                            already_committed = [d.split()[-1] for d in ctx.calendar.get("committed_pto", [])]
                            if f"S{future_day.season:02d} d{future_day.doy:03d}" not in already_committed:
                                actions.append(CommitPTO(future_day, reason="Advance PTO for momentum bookings"))

                    return actions

        return actions
