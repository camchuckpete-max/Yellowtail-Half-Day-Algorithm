"""Season 1 End: Budget-locked. Season 2 will use reactive bite tracking (persist strategy)."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "Season 1 Holdout"

    def describe(self) -> str:
        return (
            "Season 1 ended with $30 budget (locked; $80 minimum trip cost). "
            "Analysis: pre-booked 8 three-quarter trips in cold season (d35-57, 0 fish for $1,200) "
            "before any bite signals. Won only 0.1296 fish vs winner B_BIG (7.89). "
            "Season 2 will switch to persist's strategy: track 3-day rolling YT sum by class, "
            "book cheapest offer when class sum > 0, pre-commit PTO only for peak windows (doy 150-170, 250-318). "
            "Key insight: wait for fleet signals, don't pre-book. Cheap half-days to test, expensive trips only on hot bites."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        # Season 1 is locked out (budget < $80 minimum trip cost)
        return []
