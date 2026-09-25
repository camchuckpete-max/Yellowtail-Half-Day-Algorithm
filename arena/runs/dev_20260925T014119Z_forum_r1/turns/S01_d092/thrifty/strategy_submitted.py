"""Thrifty: weekend warrior, preserve for fall bite."""
from arena.api.ctx import Strategy, Book


class Strategy(Strategy):
    name = "Weekend Warrior"

    def describe(self) -> str:
        return (
            "Volume over timing: books cheap HD_PM half-day trips ($80) on weekends and holidays "
            "(no PTO cost) whenever possible, building low-cost inventory. Skips weekdays to preserve "
            "the 2 PTO days for the fall bite window (doy 250-318) when water warms and offshore bite "
            "activates. Current season is cold (13.9°C, 57°F); historical data shows productive season "
            "in fall. Continues booking weekend trips through summer at baseline rate, ready to pivot "
            "to higher-value trips in October."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        try:
            # Only book weekend/holiday HD_PM trips in current dead season
            # Save PTO and budget for fall window
            if not ctx.today.is_weekend and not ctx.today.is_holiday:
                return actions

            if ctx.budget_left < 80:
                return actions

            # Check if HD_PM is available tomorrow
            offer = ctx.offer("HD_PM")
            if not offer or not offer.bookable or offer.cost > ctx.budget_left:
                return actions

            # Book it
            try:
                boat = ctx.pick_boat(offer.cls, offer.departure)
                if boat:
                    actions.append(Book(offer.id, "weekend HD_PM", boat=boat))
            except Exception:
                pass

        except Exception:
            pass

        return actions
