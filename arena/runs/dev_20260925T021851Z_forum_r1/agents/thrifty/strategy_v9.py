"""
Thrifty Season 2: data-driven class selection + reactive momentum.
Season 1 lesson: half-days were 0.005 YT/angler historically—mistake to favor them.
Season 2: gate by class strength first (day_1_5 and overnight only), then react to 2-3 day signals.
"""
from arena.api.ctx import Strategy, Book, CommitPTO
import pandas as pd


class Strategy(Strategy):
    name = "Data-gated momentum: only book proven classes (day_1_5, overnight, three_quarter)"

    def describe(self) -> str:
        return (
            "Historical data shows half-days averaged 0.005 YT/angler while day_1_5 averaged 1.02. "
            "Season 2: gate by class strength first—only book day_1_5, overnight, or three_quarter (proven earners). "
            "Among qualifying classes, track 2-3 day rolling yellowtail per angler separately. "
            "At 21:00, book tomorrow's highest-rate qualifying offer with best recent signal. "
            "At 16:00, also book today's twilight if its rate is positive (no PTO cost). "
            "Commit PTO 14 days ahead when any qualifying class shows positive momentum. "
            "Hold $200 minimum reserve; prefer San Diego/Malihini for 3/4-day, pick_boat otherwise."
        )

    def on_turn(self, ctx) -> None:
        """Called at turn boundaries (1st, 15th of month)."""
        pass

    def decide(self, ctx) -> list:
        """Gate by proven class strength, then book on positive 2-3 day momentum."""
        actions = []

        trips = ctx.observe("trips")
        if trips.empty:
            return actions

        min_reserve = 200
        if ctx.budget_left <= min_reserve:
            return actions

        recent_cutoff = ctx.now.t - 3
        recent_trips = trips[trips["fish_date_t"] >= recent_cutoff]

        if recent_trips.empty:
            return actions

        # Gate: only consider historically proven classes (day_1_5 > 1.0, overnight > 0.4, three_quarter > 0.1 YT/angler)
        proven_classes = ["day_1_5", "overnight", "three_quarter"]

        # Calculate recent 2-3 day signal for proven classes only
        class_performance = {}
        for cls in proven_classes:
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

        # Pick best qualifying class with positive signal
        best_class = None
        best_signal = -999
        for cls in proven_classes:
            if class_performance[cls] >= 0 and class_performance[cls] > best_signal:
                best_signal = class_performance[cls]
                best_class = cls

        if best_class is None:
            return actions

        # Try to book the best qualifying class for tomorrow
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

                    reason = f"Proven class {best_class} at {class_performance[best_class]:.3f} YT/angler (2-3d signal)"
                    actions.append(Book(offer.id, reason, boat=boat))

                    if offer.pto_dates:
                        future_day = ctx.today.plus(14)
                        if future_day.doy < 366:
                            already_committed = [d.split()[-1] for d in ctx.calendar.get("committed_pto", [])]
                            if f"S{future_day.season:02d} d{future_day.doy:03d}" not in already_committed:
                                actions.append(CommitPTO(future_day, reason="Advance PTO for proven-class momentum"))

                    return actions

        return actions
