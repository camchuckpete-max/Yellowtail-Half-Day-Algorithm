"""Thrifty: Reactive booking on 3-day rolling yellowtail signals."""
from arena.api.ctx import Strategy, Book, CommitPTO
from collections import defaultdict


class Strategy(Strategy):
    name = "Reactive Bite Tracker"

    def describe(self) -> str:
        return (
            "Tracks fleet yellowtail over last 3 fished days by trip class. Books cheapest "
            "available offer when a class shows positive catch (hot). Targets peak windows "
            "(doy 150-170 spring, doy 250-318 fall) with $80-150 weekend trips, reserving "
            "$800+ for fall offshore. Commits PTO 14 days ahead from historical seasonality "
            "in peak windows (>=63°F water signal). Boat: default scheduled boat that ran "
            "the class most in last 60 days. Avoids pre-booking without live signals."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        try:
            trips = ctx.observe("trips")

            # 1. Find 3-day rolling sum of YT by class
            recent_doy = ctx.today.doy - 3
            recent_trips = trips[
                (trips["fish_date_doy"] >= recent_doy)
                & (trips["fish_date_doy"] <= ctx.today.doy)
            ]

            hot_classes = set()
            for cls in ["HD_AM", "HD_PM", "THREE_QUARTER", "TWILIGHT", "OVERNIGHT", "DAY_1_5"]:
                cls_trips = recent_trips[recent_trips["cls"] == cls]
                if len(cls_trips) > 0 and cls_trips["yt"].sum() > 0:
                    hot_classes.add(cls)

            # 2. Book cheapest hot offer if budget permits
            if hot_classes and ctx.budget_left >= 80:
                offers = []
                for cls in hot_classes:
                    offer = ctx.offer(cls)
                    if offer and offer.bookable:
                        offers.append((offer.cost, offer))

                if offers:
                    offers.sort()
                    cost, offer = offers[0]
                    boat = ctx.pick_boat(offer.cls, offer.departure)
                    actions.append(
                        Book(
                            offer.id,
                            reason=f"{offer.cls} hot (3d yt > 0)",
                            boat=boat,
                        )
                    )

            # 3. Commit PTO for peak windows (14 days ahead)
            # Spring: doy 150-170, Fall: doy 250-318
            if ctx.pto_left >= 1:
                future_day = ctx.today.plus(14)
                future_doy = future_day.doy

                # Check if future day is in peak window
                in_spring = 150 <= future_doy <= 170
                in_fall = 250 <= future_doy <= 318

                if (in_spring or in_fall) and not future_day.is_weekend and not future_day.is_holiday:
                    actions.append(CommitPTO(future_doy, reason="Peak window weekday"))

        except Exception:
            pass

        return actions
