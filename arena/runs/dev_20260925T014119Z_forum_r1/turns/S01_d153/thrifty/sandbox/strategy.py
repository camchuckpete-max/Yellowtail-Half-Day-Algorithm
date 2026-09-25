"""Thrifty: Reactive hot-bite strategy, book what's catching now."""
from arena.api.ctx import Strategy, Book


class Strategy(Strategy):
    name = "Reactive Hot Bite"

    def describe(self) -> str:
        return (
            "Reactive strategy: observes last 3 days of fishing by class and books when "
            "yellowtail count is positive. Prioritizes cheap trips with no PTO needed "
            "(TWILIGHT $80, weekend half-days $80). Books the cheapest hot offer available, "
            "one per day. Uses $480 budget for 6+ trips if bite stays hot. "
            "Stops booking when budget drops below $80."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        if ctx.budget_left < 80:
            return actions

        try:
            trips = ctx.observe("trips")

            # Last 3 days of fishing
            recent_doy = ctx.today.doy - 3
            recent_trips = trips[
                (trips["fish_date_doy"] >= recent_doy)
                & (trips["fish_date_doy"] <= ctx.today.doy)
            ]

            # Count yt by class
            hot_classes = {}
            for cls in ["HD_AM", "HD_PM", "THREE_QUARTER", "FULL_DAY", "TWILIGHT", "OVERNIGHT", "DAY_1_5"]:
                cls_trips = recent_trips[recent_trips["cls"].str.lower() == cls.lower()]
                yt_count = cls_trips["yt"].sum()
                if yt_count > 0:
                    hot_classes[cls] = yt_count

            # Prices: cheaper first (TWILIGHT/HD=80, THREE_QUARTER=150, etc)
            class_prices = {
                "TWILIGHT": 80,
                "HD_AM": 80,
                "HD_PM": 80,
                "THREE_QUARTER": 150,
                "FULL_DAY": 275,
                "OVERNIGHT": 400,
                "DAY_1_5": 550,
            }

            # Book from cheapest hot class
            for cls in sorted(hot_classes.keys(), key=lambda c: class_prices[c]):
                if ctx.budget_left < class_prices[cls]:
                    continue

                offer = ctx.offer(cls)
                if offer is not None and offer.bookable:
                    boat = ctx.pick_boat(cls, ctx.tomorrow)
                    actions.append(
                        Book(
                            offer.id,
                            reason=f"{cls} hot (3d: {hot_classes[cls]:.0f} yt)",
                            boat=boat,
                        )
                    )
                    break

        except Exception:
            pass

        return actions
