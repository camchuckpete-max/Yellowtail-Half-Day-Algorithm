"""Thrifty: Season concluded, budget exhausted. Volume strategy caught 0.1296 fish."""
from arena.api.ctx import Strategy, Book


class Strategy(Strategy):
    name = "Season End Holdout"

    def describe(self) -> str:
        return (
            "Season 1 volume strategy resulted in 0.1296 fish across 15 trips ($1,970 spent). "
            "One successful three-quarter day (d154, 7 yellowtail) versus 14 skunks (0.0 fish). "
            "Early season priorities (doys 35-57, 99-120) yielded nothing; reactive hot-bite logic "
            "in doys 154-162 found the bite but too late with limited budget. With $30 remaining "
            "and minimum $80 trip cost, no further bookings possible. Strategy now holds position, "
            "focusing on running cleanly through season end (182 days remain)."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        # Budget exhausted; no trips bookable
        return []
