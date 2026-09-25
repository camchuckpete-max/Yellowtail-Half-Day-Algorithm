"""Thrifty: Season end holdout. Budget exhausted at day 245."""
from arena.api.ctx import Strategy


class Strategy(Strategy):
    name = "Season End Holdout"

    def describe(self) -> str:
        return (
            "Season 1 final phase: budget exhausted ($30 < $80 minimum trip cost). "
            "Strategy learned that timing beats volume—early-season three-quarter-day bookings caught 0 fish; "
            "only the hot-bite window at doy 154-162 scored (1 trip, 0.1296 fish). "
            "Leaders use 3-day rolling yellowtail tracking (persist: 1.38 fish) or offshore bite signals "
            "(temp_first: 2.55 fish). Next season: track recent fleet YT by class; delay first trip 60+ days "
            "to historical peak bite (doy 150+); reserve budget for proven windows. "
            "This final run holds without booking."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        return []
