"""
Thrifty strategy: book 3/4-day trips on high-performing boats.
Season 1 data: 3/4-day caught 105 YT (80% of all fish).
Focus on San Diego, Malihini, Mission Belle on 3/4-day; diversify across dates.
"""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "3/4-day volume on winning boats"

    def describe(self) -> str:
        return (
            "Season 1 data: 3/4-day trips caught 105 YT (77% of total catch). "
            "Overnight and 1.5-day caught 9 YT total. "
            "Strategy: book 3/4-day trips ($150 each) whenever available, "
            "targeting 70% of budget. Prefer boats with recent 3/4-day success. "
            "Commit PTO for weekday 3/4-day trips to spread risk across dates. "
            "Use half-days only if 3/4-day not available and budget remains."
        )

    def on_turn(self, ctx) -> None:
        """Cache any pre-computed analysis."""
        pass

    def decide(self, ctx) -> list:
        """Book 3/4-day trips prioritizing high-value boats and diversified dates."""
        actions = []

        # Primary: book 3/4-day trips
        offer_3q = ctx.offer("THREE_QUARTER")
        if offer_3q and offer_3q.bookable and ctx.budget_left >= 150:
            # Look ahead 14 days for best opportunity
            for day_offset in range(1, 15):
                target_day = ctx.tomorrow.plus(day_offset - 1)

                # Get scheduled boats for this date
                boats = ctx.scheduled_boats("THREE_QUARTER", target_day)
                if not boats:
                    continue

                # Prefer known winners (San Diego, Malihini, Mission Belle)
                # Otherwise use default pick
                winner_boats = [b for b in boats if b in ["San Diego", "Malihini", "Mission Belle"]]
                boat_choice = winner_boats[0] if winner_boats else boats[0]

                reason = f"3/4-day on {boat_choice} (proven class, {len(boats)} boats available)"
                actions.append(Book(offer_3q.id, reason, boat=boat_choice))
                return actions

        # Secondary: half-day if budget remains
        if ctx.budget_left >= 80:
            offer_pm = ctx.offer("HD_PM")
            if offer_pm and offer_pm.bookable:
                boats = ctx.scheduled_boats("HD_PM", ctx.tomorrow)
                if boats:
                    reason = "Half-day fallback (3/4-day not available)"
                    actions.append(Book(offer_pm.id, reason, boat=boats[0]))
                    return actions

        return actions
