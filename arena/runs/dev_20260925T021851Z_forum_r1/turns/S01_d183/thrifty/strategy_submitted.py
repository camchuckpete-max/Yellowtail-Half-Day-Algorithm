"""
Thrifty: conservative reactive strategy learned from Season 1 freeze.
Season 1 error: burned $1,960 by day 71 on static bookings, missed hot days 144-151.
Season 2: extreme caution—only book on fresh strong signals (3-day >2.0 YT/angler), hold capital, react to streaks.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd


class Strategy(Strategy):
    name = "Conservative reactive: 3-day signals with capital discipline"

    def describe(self) -> str:
        return (
            "Season 1 taught a hard lesson: static class confidence and early capital burn led to day-71 freeze, "
            "missing hot windows at days 144-151. New approach: extreme selectivity. "
            "Only book when 3-day trailing YT/angler > 2.0 (strong fresh signal). "
            "Hold $1200+ in reserve until day 90; allow aggressive booking only in peak season (d90-d180). "
            "Prioritize overnight/3/4-day over half-days. React to 2+ consecutive hot days before committing PTO. "
            "Use only proven boats: San Diego/Malihini for 3/4-day, any scheduled boat otherwise."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th of month)."""
        pass

    def decide(self, ctx) -> list:
        """Book only when 3-day signal is very strong AND capital discipline is maintained."""
        actions = []

        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        # Reserve discipline: hold $1200+ in reserve until day 90
        min_reserve = 1200 if ctx.now.doy < 90 else 500
        if ctx.budget_left <= min_reserve:
            # Low on budget; don't book
            return actions

        # Only look at last 3 days for very fresh signals (like persist)
        recent_cutoff = ctx.now.t - 3
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]

        if recent_trips.empty:
            # No recent data; don't book without signal
            return actions

        # Calculate YT per angler by class for last 3 days
        class_performance = {}
        for cls in ["overnight", "day_1_5", "three_quarter", "hd_pm", "hd_am", "hd_twilight"]:
            cls_trips = recent_trips[recent_trips["cls"] == cls]
            if not cls_trips.empty:
                total_yt = cls_trips["yt"].sum()
                total_anglers = cls_trips["anglers"].sum()
                if total_anglers > 0:
                    class_performance[cls] = total_yt / total_anglers
                else:
                    class_performance[cls] = 0

        # Only consider classes with STRONG signals (>2.0 YT/angler)
        # Before day 90, threshold is even higher (>3.0) for extra caution
        threshold = 3.0 if ctx.now.doy < 90 else 2.0
        strong_classes = [(cls, rate) for cls, rate in class_performance.items() if rate > threshold]

        if not strong_classes:
            # No strong signal; wait
            return actions

        # Sort by strength
        strong_classes.sort(key=lambda x: x[1], reverse=True)

        # Try to book the strongest class
        for cls_name, rate in strong_classes:
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

            # Verify budget after this booking
            if ctx.budget_left - offer.cost < min_reserve:
                continue

            boats = ctx.scheduled_boats(offer_cls, ctx.tomorrow)
            if not boats:
                continue

            # Prefer proven boats
            if cls_name == "three_quarter":
                winners = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                boat = winners[0] if winners else boats[0]
            else:
                boat = boats[0]

            reason = f"Strong 3-day signal: {cls_name} {rate:.2f} YT/angler (threshold {threshold}) on {boat}"
            actions.append(Book(offer.id, reason, boat=boat))
            return actions

        return actions
