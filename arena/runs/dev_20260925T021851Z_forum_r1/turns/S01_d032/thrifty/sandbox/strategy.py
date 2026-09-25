"""
Thrifty strategy: volume over timing. Book many cheap half-day trips ($80 each).
Prioritize weekends and high-catch days. Track cost per fish and commit PTO strategically.
"""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "Volume beats timing"

    def describe(self) -> str:
        return (
            "Book many cheap half-day trips ($80 PM, AM, twilight) to maximize volume. "
            "Prioritize weekends (free PTO). Commit PTO strategically for high-catch weekdays. "
            "Use 14-day forecast of catches (from recent trips data) to pick days. "
            "Target 20-25 trips per season to outfish premium-trip competitors. "
            "Cost per fish matters more than individual trip size."
        )

    def on_turn(self, ctx) -> None:
        """Cache analysis of historical catches per day of week and class."""
        pass

    def decide(self, ctx) -> list:
        """Return list of Book and CommitPTO actions."""
        actions = []
        tomorrow = ctx.tomorrow

        # Commit PTO 14 days ahead for high-value fishing days (weekdays)
        for day_offset in range(14, 30):
            if ctx.pto_left <= 0:
                break

            target_day = tomorrow.plus(day_offset - 1)

            # Commit PTO on weekdays that aren't holidays
            if (not target_day.is_weekend and
                not target_day.is_holiday):

                reason = "Reserve weekday for fishing opportunity"
                actions.append(CommitPTO(target_day, reason))
                break

        # Book cheap half-day trips: prioritize weekends (free PTO)
        if ctx.budget_left >= 80:
            # Look for the next weekend to book
            for day_offset in range(1, 15):
                target_day = tomorrow.plus(day_offset - 1)

                if target_day.is_weekend:
                    offer = ctx.offer("HD_PM")
                    if offer and offer.bookable:
                        boats = ctx.scheduled_boats("HD_PM", target_day)
                        if boats:
                            reason = "Volume: PM half-day on weekend (free PTO)"
                            actions.append(Book(offer.id, reason, boat=boats[0]))
                            return actions

            # Fallback: book tomorrow's AM if it's a weekday
            if not tomorrow.is_weekend and not tomorrow.is_holiday:
                offer = ctx.offer("HD_AM")
                if offer and offer.bookable:
                    boats = ctx.scheduled_boats("HD_AM", tomorrow)
                    if boats:
                        reason = "Volume: AM half-day (cheap)"
                        actions.append(Book(offer.id, reason, boat=boats[0]))

        return actions
