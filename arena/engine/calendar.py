"""Calendar rules: seasons, weekdays, federal holidays, PTO cost, ticks, masked dates (SPEC §2, §4.2)."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from functools import lru_cache

import holidays

EPOCH = date(2010, 1, 1)  # day 0 of the masked timeline (season 1 = first configured season)


@lru_cache(maxsize=None)
def _us_holidays(year: int):
    return holidays.US(years=year, observed=True)


def is_holiday(d: date) -> bool:
    return d in _us_holidays(d.year)


def is_weekday(d: date) -> bool:
    """Mon-Fri that is not a US federal holiday (observed date)."""
    return d.weekday() < 5 and not is_holiday(d)


def season_bounds(year: int, first_year: int, first_start: date) -> tuple[date, date]:
    start = date(year, 1, 1)
    if year == first_year and first_start.year == year:
        start = first_start
    return start, date(year, 12, 31)


def days_in_year(year: int) -> int:
    return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365


def day_number(d: date) -> int:
    """Days since EPOCH (masked timeline)."""
    return (d - EPOCH).days


def t_of(dt: datetime) -> float:
    """Fractional days since EPOCH for a naive PT datetime."""
    return (dt - datetime.combine(EPOCH, time())).total_seconds() / 86400.0


def from_day_number(n: int) -> date:
    return EPOCH + timedelta(days=n)


def season_index(d: date, first_year: int) -> int:
    return d.year - first_year + 1


def parse_tick(s: str) -> time:
    h, m = map(int, s.split(":"))
    return time(h, m)


def ticks_of_season(year: int, first_year: int, first_start: date, tick_times: list[time]):
    """Yield (date, tick_time) in order for one season."""
    start, end = season_bounds(year, first_year, first_start)
    d = start
    while d <= end:
        for t in tick_times:
            yield d, t
        d += timedelta(days=1)
