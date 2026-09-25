"""Thrifty: high-value trip mix prioritizing day_1_5 (16 yt avg) and three_quarter (3.7 yt avg)."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "Volume + value"

    def describe(self) -> str:
        return (
            "Prioritizes high-value trips: 1.5-day departures average 16 yellowtail at $34/fish "
            "with zero PTO cost; three-quarter days average 3.7 yellowtail at $40/fish. "
            "Commits PTO for weekday trips 14+ days ahead to enable bookings. "
            "Targets 50+ fish per season with available budget and PTO days."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        # Book 1.5-day trips (highest value: 16 yt avg, $34/fish, 0 PTO)
        offer = ctx.offer("DAY_1_5")
        if offer and offer.bookable and ctx.budget_left >= offer.cost:
            try:
                boat = ctx.pick_boat(offer.cls, offer.departure)
                actions.append(Book(offer.id, "1.5-day high-value", boat=boat))
            except Exception:
                pass

        # Book three-quarter day trips (secondary: 3.7 yt avg, $40/fish)
        offer = ctx.offer("THREE_QUARTER")
        if offer and offer.bookable and ctx.budget_left >= offer.cost and ctx.pto_left >= 1:
            try:
                boat = ctx.pick_boat(offer.cls, offer.departure)
                actions.append(Book(offer.id, "three-quarter value", boat=boat))
            except Exception:
                pass

        # Commit PTO for upcoming weekday trips (14+ days ahead)
        if ctx.pto_left > 2:
            today = ctx.today
            for offset in [16, 23, 30, 37, 44]:
                if ctx.pto_left <= 2:
                    break
                try:
                    day = today.plus(offset)
                    if not day.is_weekend and not day.is_holiday:
                        actions.append(CommitPTO(day, "reserve for three-quarter"))
                except Exception:
                    pass

        return actions
