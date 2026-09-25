"""Thrifty: volume + value mix of 1.5-day and three-quarter day trips."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "Volume + value"

    def describe(self) -> str:
        return (
            "High-value trip mix: 1.5-day Friday departures (avg 16 yt, $34/fish, 0 PTO) "
            "and three-quarter days (avg 4 yt, $40/fish). Commit PTO for weekday trips 14+ days ahead. "
            "Target ~50+ fish on $2000 budget with 10 PTO days."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        # Book 1.5-day Friday trips (highest priority: avg 16 yt, $34/fish, 0 PTO)
        offer = ctx.offer("DAY_1_5")
        if offer and offer.bookable and ctx.budget_left >= offer.cost:
            boat = ctx.pick_boat("day_1_5", offer.departure)
            actions.append(Book(offer.id, "1.5-day Friday weekend", boat=boat))

        # Book three-quarter day trips (avg 4 yt, $40/fish, needs PTO)
        offer = ctx.offer("THREE_QUARTER")
        if offer and offer.bookable and ctx.budget_left >= offer.cost and ctx.pto_left > 1:
            boat = ctx.pick_boat("three_quarter", offer.departure)
            actions.append(Book(offer.id, "three-quarter day value", boat=boat))

        # Commit PTO for upcoming weekday trips (14+ days ahead)
        if ctx.pto_left > 3:
            today = ctx.today
            committed = set(ctx.calendar.get("committed_pto", []) or [])
            for offset in [16, 23, 30, 37]:
                if ctx.pto_left <= 3:
                    break
                day = today.plus(offset)
                if not day.is_weekend and not day.is_holiday and day not in committed:
                    actions.append(CommitPTO(day, "three-quarter trip reserve"))

        return actions
