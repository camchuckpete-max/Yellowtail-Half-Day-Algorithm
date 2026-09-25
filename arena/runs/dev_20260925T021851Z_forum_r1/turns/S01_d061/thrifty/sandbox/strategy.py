"""
Thrifty strategy: pivot from volume half-days (failed) to premium multi-day trips.
Data shows 1.5-day and overnight trips catch 98% of fish.
Late season: book any bookable overnight/1.5-day trip while budget remains.
"""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "Pivot to premium trips (late pivot)"

    def describe(self) -> str:
        return (
            "Early season half-day strategy failed (411 YT total vs 33k on premium trips). "
            "Pivoting to overnight and 1.5-day trips for late season. "
            "Book overnight/1.5-day whenever available and budget permits. "
            "Weekend trips preferred (no PTO cost). "
            "Priority: 1.5-day Friday trips (proven effective), then overnight weekend trips."
        )

    def on_turn(self, ctx) -> None:
        """Cache analysis if needed."""
        pass

    def decide(self, ctx) -> list:
        """Return list of Book and CommitPTO actions."""
        actions = []
        tomorrow = ctx.tomorrow

        # Try to book premium trips: 1.5-day preferred, then overnight
        # Look ahead 14 days for any bookable opportunity
        for day_offset in range(1, 15):
            target_day = tomorrow.plus(day_offset - 1)

            # Prefer 1.5-day (highest catch rate: 14k fish/season)
            offer_1_5 = ctx.offer("DAY_1_5")
            if offer_1_5 and offer_1_5.bookable and ctx.budget_left >= 550:
                boats = ctx.scheduled_boats("DAY_1_5", target_day)
                if boats:
                    reason = "Premium: 1.5-day trip (proven 14k+ YT/season)"
                    actions.append(Book(offer_1_5.id, reason, boat=boats[0]))
                    return actions

            # Fallback to overnight (5.8k fish/season)
            if ctx.budget_left >= 400:
                offer_overnight = ctx.offer("OVERNIGHT")
                if offer_overnight and offer_overnight.bookable:
                    boats = ctx.scheduled_boats("OVERNIGHT", target_day)
                    if boats:
                        reason = "Premium: overnight trip (5.8k YT/season)"
                        actions.append(Book(offer_overnight.id, reason, boat=boats[0]))
                        return actions

            # Fallback to three-quarter (6.2k fish/season)
            if ctx.budget_left >= 150:
                offer_3q = ctx.offer("THREE_QUARTER")
                if offer_3q and offer_3q.bookable:
                    boats = ctx.scheduled_boats("THREE_QUARTER", target_day)
                    if boats:
                        reason = "Premium: 3/4-day trip (6.2k YT/season)"
                        actions.append(Book(offer_3q.id, reason, boat=boats[0]))
                        return actions

        # Fallback: book any remaining half-day to use remaining budget
        if ctx.budget_left >= 80:
            for day_offset in range(1, 8):
                target_day = tomorrow.plus(day_offset - 1)
                for cls in ["HD_PM", "HD_AM"]:
                    offer = ctx.offer(cls)
                    if offer and offer.bookable:
                        boats = ctx.scheduled_boats(cls, target_day)
                        if boats:
                            reason = f"Fallback: {cls} half-day (last resort)"
                            actions.append(Book(offer.id, reason, boat=boats[0]))
                            return actions

        return actions
