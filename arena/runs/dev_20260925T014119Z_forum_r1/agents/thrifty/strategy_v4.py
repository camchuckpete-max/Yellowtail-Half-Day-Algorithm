"""Thrifty: reactive yellowtail strategy, book hot classes only."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "React to bite"

    def describe(self) -> str:
        return (
            "Reactive strategy: sums yellowtail caught fleet-wide over last 3 fished days per class. "
            "Books any available trip (HD_PM, THREE_QUARTER, OVERNIGHT, DAY_1_5) when its class is hot "
            "(sum > 0 in recent days). Prioritizes classes with more recent catch. Fits bookings within "
            "remaining budget and PTO. No pre-committed PTO; twilight and weekends are free."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        try:
            trips = ctx.observe("trips")
            if trips is None or len(trips) == 0:
                return actions

            now_t = ctx.now.t
            three_days_back_t = now_t - 3

            trip_classes = [
                ("HD_PM", "hd_pm"),
                ("THREE_QUARTER", "three_quarter"),
                ("OVERNIGHT", "overnight"),
                ("DAY_1_5", "day_1_5"),
                ("HD_AM", "hd_am"),
                ("TWILIGHT", "hd_twilight"),
            ]

            hot_classes = {}
            for offer_cls, db_cls in trip_classes:
                recent = trips[
                    (trips["fish_date_t"] >= three_days_back_t)
                    & (trips["cls"] == db_cls)
                ]
                if len(recent) > 0:
                    yt_sum = recent["yt"].sum()
                    if yt_sum > 0:
                        hot_classes[offer_cls] = yt_sum

            if not hot_classes:
                return actions

            sorted_hot = sorted(hot_classes.items(), key=lambda x: x[1], reverse=True)

            for offer_cls, _ in sorted_hot:
                if ctx.budget_left < 80 or not ctx.offers:
                    break

                offer = ctx.offer(offer_cls)
                if not offer or not offer.bookable or ctx.budget_left < offer.cost:
                    continue

                try:
                    boat = ctx.pick_boat(offer.cls, offer.departure)
                    if boat:
                        actions.append(Book(offer.id, f"{offer_cls} hot", boat=boat))
                except Exception:
                    pass

        except Exception:
            pass

        return actions
