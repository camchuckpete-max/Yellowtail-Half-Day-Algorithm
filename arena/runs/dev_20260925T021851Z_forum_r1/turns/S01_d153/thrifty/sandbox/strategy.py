"""
Thrifty: reactive volume strategy tracking recent class performance.
Season 1 lesson: 3/4-day was best class (1055 YT) but booking on skunked dates (d64, d71) yields zero.
Season 2: track trailing 7-day YT/angler by class, book the hot class, focus on proven boats (San Diego, Malihini).
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd


class Strategy(Strategy):
    name = "Reactive volume: track 7-day class performance"

    def describe(self) -> str:
        return (
            "Season 1 showed 3/4-day dominated (1055 YT) and overnight was surprisingly good per-trip (4.7 YT/trip). "
            "But date selection matters: days 64 and 71 were skunks despite booking the best class. "
            "Strategy: at each tick, calculate recent 7-day YT per angler for each trip class. "
            "Book tomorrow's offer for the hottest class if trailing average is positive. "
            "Prefer San Diego/Malihini for 3/4-day, any scheduled boat otherwise. "
            "Use half-days only if premium classes dead. Commit PTO on weekdays when signals warrant."
        )

    def on_turn(self, ctx) -> None:
        """Pre-compute recent class performance (called at turn boundaries)."""
        pass

    def decide(self, ctx) -> list:
        """Book tomorrow's best-performing class based on recent history."""
        actions = []

        # Get last 7 days of trip data to calculate recent performance by class
        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        # Filter for recent trips (last 7 days), aggregate by class
        recent_cutoff = ctx.now.t - 7
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]

        if recent_trips.empty:
            # Fall back to all-season data if no recent trips
            recent_trips = trips[trips["fish_date_season"] == ctx.now.season]

        # Calculate YT per angler by class (accounting for multiple boats on same day)
        class_performance = {}
        for cls in ["three_quarter", "overnight", "day_1_5", "hd_pm", "hd_am", "hd_twilight"]:
            cls_trips = recent_trips[recent_trips["cls"] == cls]
            if not cls_trips.empty:
                total_yt = cls_trips["yt"].sum()
                total_anglers = cls_trips["anglers"].sum()
                if total_anglers > 0:
                    class_performance[cls] = total_yt / total_anglers
                else:
                    class_performance[cls] = 0

        # Sort classes by recent performance
        sorted_classes = sorted(class_performance.items(), key=lambda x: x[1], reverse=True)

        # Try to book the best-performing class first, then fallback to next best
        for cls_name, recent_rate in sorted_classes:
            if recent_rate <= 0:
                # Skip classes with zero or negative recent rate
                continue

            # Map class name to offer class string
            offer_map = {
                "three_quarter": "THREE_QUARTER",
                "overnight": "OVERNIGHT",
                "day_1_5": "DAY_1_5",
                "hd_pm": "HD_PM",
                "hd_am": "HD_AM",
                "hd_twilight": "TWILIGHT",
            }

            offer_cls = offer_map[cls_name]
            offer = ctx.offer(offer_cls)

            if not offer or not offer.bookable:
                continue

            # Check budget
            if ctx.budget_left < offer.cost:
                continue

            # Get scheduled boats for this class tomorrow
            boats = ctx.scheduled_boats(offer_cls, ctx.tomorrow)
            if not boats:
                continue

            # Prefer proven high-volume boats (San Diego, Malihini for 3/4-day)
            if cls_name == "three_quarter":
                winners = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                boat = winners[0] if winners else boats[0]
            else:
                boat = boats[0]

            reason = f"7-day {cls_name} rate {recent_rate:.2f} YT/angler > 0 on {boat}"
            actions.append(Book(offer.id, reason, boat=boat))
            return actions

        # If all premium classes cold, try half-day as safety
        if ctx.budget_left >= 80:
            offer_pm = ctx.offer("HD_PM")
            if offer_pm and offer_pm.bookable:
                boats = ctx.scheduled_boats("HD_PM", ctx.tomorrow)
                if boats:
                    reason = "All premium classes cold, booking half-day"
                    actions.append(Book(offer_pm.id, reason, boat=boats[0]))
                    return actions

        return actions
