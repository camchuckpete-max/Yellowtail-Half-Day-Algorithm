"""Thrifty: Reactive hot-bite strategy. Book cheap trips when classes show positive catch."""
from arena.api.ctx import Strategy, Book, CommitPTO
from collections import defaultdict


class Strategy(Strategy):
    name = "Reactive Hot Bite"

    def describe(self) -> str:
        return (
            "Reactive strategy: tracks 3-day yellowtail totals by trip class fleet-wide. "
            "Books when a class shows positive catch (>0 yt in last 3 fished days). "
            "Prioritizes cheap options: TWILIGHT $80 (no PTO), weekend half-days $80, then "
            "other budget permitting. One trip per departure date. Avoids PTO pre-commits "
            "unless strong seasonal window identified. Boat: default scheduled for class. "
            "Simple, reactive logic beats prediction. Targets 0.13+ fish/trip average."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        # Budget exhausted or too low for any trip
        if ctx.budget_left < 80:
            return actions

        try:
            # Observe recent catch by class (last 3 fished days)
            trips = ctx.observe("trips")

            # Get yesterday's fish counts by class
            recent_doy = ctx.today.doy - 3
            recent_trips = trips[
                (trips["fish_date_doy"] >= recent_doy)
                & (trips["fish_date_doy"] <= ctx.today.doy)
            ]

            # Count yellowtail per class
            yt_by_class = defaultdict(int)
            for _, row in recent_trips.iterrows():
                cls = row.get("cls", "").lower()
                yt_by_class[cls] += row.get("yt", 0)

            # Prefer cheap, no-PTO trips: TWILIGHT first
            class_priority = ["twilight", "hd_pm", "hd_am", "three_quarter", "full_day", "day_1_5", "overnight"]

            for trip_class in class_priority:
                # Check if this class had positive catch in last 3 days
                if yt_by_class.get(trip_class, 0) > 0:
                    # Get tomorrow's offer for this class
                    offer = ctx.offer(trip_class.upper())

                    if offer and offer.bookable and ctx.budget_left >= offer.cost:
                        # Use default boat (best in last 60 days for this class/day)
                        boat = ctx.pick_boat(trip_class.upper(), ctx.tomorrow)
                        actions.append(
                            Book(
                                offer.id,
                                reason=f"{trip_class} hot ({yt_by_class[trip_class]:.0f} yt in 3d)",
                                boat=boat,
                            )
                        )
                        return actions  # One per tick

        except Exception:
            pass

        return actions
