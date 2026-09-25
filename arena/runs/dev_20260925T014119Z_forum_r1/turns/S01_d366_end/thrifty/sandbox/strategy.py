"""Reactive Bite Tracker: 3-day rolling YT sum by class, book when hot."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "Reactive Bite Tracker"

    def describe(self) -> str:
        return (
            "Reactive booking based on fleet yellowtail signals. Sums yellowtail caught "
            "fleet-wide over last 3 fished days, by trip class; books the cheapest offer "
            "when its class sum is positive (hot). Reserves $800+ for fall offshore window "
            "(doy 250-318). Pre-commits PTO 14 days ahead only during historical peak periods "
            "(doy 150-170 spring, doy 250-318 fall) on Fridays. Boat selection uses default "
            "(best performer last 60 days). Principle: timing over volume; wait for fleet "
            "signals before booking."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        try:
            # Reserve $800+ for fall offshore window unless in fall window
            fall_reserve = 800
            usable_budget = ctx.budget_left - fall_reserve

            # In fall window (doy 250-318), use more budget
            if 250 <= ctx.today.doy <= 318:
                usable_budget = ctx.budget_left - 100

            if usable_budget < 80:
                return actions

            # Get fleet trips data for 3-day rolling sum by class
            trips = ctx.observe("trips")

            hot_classes = {}
            for cls in ["HD_AM", "HD_PM", "THREE_QUARTER", "TWILIGHT", "OVERNIGHT", "DAY_1_5"]:
                recent_trips = trips[
                    (trips["fish_date_doy"] >= ctx.today.doy - 3)
                    & (trips["fish_date_doy"] <= ctx.today.doy)
                    & (trips["cls"] == cls)
                ]
                yt_sum = recent_trips["yt"].sum()
                if yt_sum > 0:
                    hot_classes[cls] = yt_sum

            if not hot_classes:
                return actions

            # Get offers and filter to hot classes
            all_offers = ctx.offer()
            if not all_offers:
                return actions

            hot_offers = [o for o in all_offers if o.cls in hot_classes and o.bookable]
            if not hot_offers:
                return actions

            # Sort by cost (cheapest first)
            hot_offers.sort(key=lambda o: o.cost)

            # Book cheapest hot offer
            for offer in hot_offers:
                if offer.cost <= usable_budget:
                    boat = ctx.pick_boat(offer.cls, offer.departure)
                    actions.append(
                        Book(
                            offer.id,
                            reason=f"{offer.cls.lower()} hot (3d sum={hot_classes[offer.cls]:.0f}yt)",
                            boat=boat,
                        )
                    )
                    break

            # Pre-commit PTO 14 days ahead for historical peak windows
            future_day = ctx.today.plus(14)

            # Spring peak: doy 150-170, Fridays only
            if 150 <= future_day.doy <= 170 and future_day.weekday == 5:
                if ctx.pto_left >= 2:
                    actions.append(CommitPTO(future_day.doy, "Spring peak Friday"))
                    actions.append(CommitPTO(future_day.plus(3).doy, "Spring peak Monday"))

            # Fall peak: doy 250-318, Fridays only
            if 250 <= future_day.doy <= 318 and future_day.weekday == 5:
                if ctx.pto_left >= 2:
                    actions.append(CommitPTO(future_day.doy, "Fall peak Friday"))
                    actions.append(CommitPTO(future_day.plus(3).doy, "Fall peak Monday"))

        except Exception:
            pass

        return actions
