"""The strategy-facing world (SPEC §5.2). This is the ONLY thing a strategy sees.

Dates are masked (§4.2): a `Day` is (season index, day of year) with calendar arithmetic; the
calendar year is never exposed when `mask_years` is on. Tables come back as pandas frames whose
date columns are already masked (see `arena/api/snapshot.py`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Callable

import numpy as np
import pandas as pd

from arena.engine import calendar as cal


@dataclass(frozen=True, order=True)
class Day:
    """A masked calendar day. `n` is the day number on the arena timeline (days since day 0);
    `season` and `doy` are what an agent reasons with."""
    n: int
    season: int
    doy: int

    def plus(self, days: int) -> "Day":
        return _mk(self.n + days)

    def minus(self, days: int) -> "Day":
        return _mk(self.n - days)

    def __sub__(self, other: "Day") -> int:
        return self.n - other.n

    @property
    def weekday(self) -> int:  # 0 = Monday
        return cal.from_day_number(self.n).weekday()

    @property
    def is_weekend(self) -> bool:
        return self.weekday >= 5

    @property
    def is_holiday(self) -> bool:
        return cal.is_holiday(cal.from_day_number(self.n))

    @property
    def is_weekday(self) -> bool:
        return cal.is_weekday(cal.from_day_number(self.n))

    def __str__(self) -> str:
        return f"S{self.season:02d} d{self.doy:03d}"


_FIRST_YEAR = 2010  # set by the engine via configure()
_MASK = True


def configure(first_year: int, mask_years: bool) -> None:
    global _FIRST_YEAR, _MASK
    _FIRST_YEAR, _MASK = first_year, mask_years


def _mk(n: int) -> Day:
    d = cal.from_day_number(n)
    return Day(n, d.year - _FIRST_YEAR + 1, d.timetuple().tm_yday)


def day_of(d: date) -> Day:
    return _mk(cal.day_number(d))


def to_date(day: Day) -> date:
    return cal.from_day_number(day.n)


@dataclass(frozen=True)
class Now:
    day: Day
    hour: int          # 16 or 21
    t: float           # fractional days on the arena timeline (for comparing with *_t columns)

    @property
    def season(self) -> int:
        return self.day.season

    @property
    def doy(self) -> int:
        return self.day.doy


@dataclass(frozen=True)
class Offer:
    id: str
    cls: str
    departure: Day
    fishing_dates: tuple[Day, ...]
    return_day: Day
    return_hour: float
    cost: int
    pto_dates: tuple[Day, ...]         # dates for which PTO must be committed (weekdays only)
    pto_need: float                    # PTO days per date in pto_dates
    bookable: bool
    reason: str                        # why not bookable (empty if bookable)


@dataclass(frozen=True)
class Booking:
    offer_id: str
    cls: str
    departure: Day
    fishing_dates: tuple[Day, ...]
    cost: int
    settled: bool = False
    ran: bool | None = None
    yt: float | None = None
    anglers: float | None = None
    n_agents: int | None = None
    share: float | None = None


@dataclass(frozen=True)
class Book:
    offer_id: str
    reason: str = ""


@dataclass(frozen=True)
class CommitPTO:
    day: Day
    reason: str = ""
    amount: float = 1.0


Action = Book | CommitPTO


@dataclass
class Calendar:
    pto_committed: dict[Day, float] = field(default_factory=dict)
    booked: list[Booking] = field(default_factory=list)      # this season, settled or not

    @property
    def results(self) -> list[Booking]:
        return [b for b in self.booked if b.settled]


class Ctx:
    """Built by the engine (or the worker) for every `decide` / `on_turn` call."""

    def __init__(self, now: Now, offers: list[Offer], budget_left: float, pto_left: float,
                 calendar: Calendar, observe: Callable[[str], pd.DataFrame],
                 features_day: Callable[[Day], dict], forum: Callable[[int], list[dict]],
                 leaderboard: list[dict], my_results: list[dict], rng: np.random.Generator,
                 tables: tuple[str, ...], budget_total: float, pto_total: float):
        self.now = now
        self.season = now.season
        self.doy = now.doy
        self.today = now.day
        self.tomorrow = now.day.plus(1)
        self.weekday = now.day.weekday
        self.offers = offers
        self.budget_left = budget_left
        self.pto_left = pto_left
        self.budget_total = budget_total
        self.pto_total = pto_total
        self.calendar = calendar
        self._observe = observe
        self._features_day = features_day
        self._forum = forum
        self.leaderboard = leaderboard
        self.my_results = my_results
        self.rng = rng
        self.tables = tables

    def is_holiday(self, day: Day) -> bool:
        return day.is_holiday

    def observe(self, table: str) -> pd.DataFrame:
        """Rows of `table` with available_at <= now (masked columns)."""
        if table not in self.tables:
            raise KeyError(f"unknown table {table!r}; tables: {self.tables}")
        return self._observe(table)

    def features_day(self, day: Day) -> dict:
        """The repo's day-level PIT features for `day`; only tomorrow at a 21:00 tick."""
        if self.now.hour != 21 or day != self.tomorrow:
            raise ValueError("features_day is only available for tomorrow at a 21:00 tick")
        return self._features_day(day)

    def forum(self, limit: int = 50) -> list[dict]:
        return self._forum(limit)

    def offer(self, cls: str) -> Offer | None:
        for o in self.offers:
            if o.cls == cls:
                return o
        return None


class Strategy:
    """Contract (SPEC §5.2). Subclass in strategy.py; the engine instantiates `STRATEGY`."""
    name: str = "unnamed"

    def describe(self) -> str:
        return ""

    def on_turn(self, ctx: Ctx) -> None:
        return None

    def decide(self, ctx: Ctx) -> list[Action]:
        return []
