"""Trip classes and the offers an agent sees at a tick (SPEC §2 table, §3.2).

Departure date `d` is the day the boat leaves the dock. Two ticks a day (§2): at **21:00 on d-1**
the engine offers every class departing before 16:00 on d (HD_AM, HD_PM, THREE_QUARTER, FULL_DAY);
at **16:00 on d** it offers the evening departures (TWILIGHT, OVERNIGHT, DAY_1_5), so an evening
booking can react to that day's AM counts (public 14:00).

`return_pto_offset` is the calendar day the angler is back for PTO purposes; it differs from the
count-publication time for TWILIGHT and FULL_DAY, whose counts are conventionally public at 00:00
the next day (D-003) although the boat is back the same evening. TWILIGHT costs no PTO (D-049).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from . import calendar as cal


@dataclass(frozen=True)
class TripClass:
    name: str
    tick: str                 # "21:00" (offered the evening before departure) | "16:00" (departure day)
    fish_offset: int          # fishing date = d + fish_offset (single fishing date for every class offered)
    return_offset: int        # counts posted on d + return_offset ...
    return_time: time         # ... at this local time
    return_pto_offset: int    # angler back on d + return_pto_offset (PTO rule)
    needs_pto: bool
    half_day: bool
    source_cls: tuple[str, ...]


CLASSES: dict[str, TripClass] = {
    "HD_AM": TripClass("HD_AM", "21:00", 0, 0, time(14, 0), 0, True, True, ("hd_am",)),
    "HD_PM": TripClass("HD_PM", "21:00", 0, 0, time(19, 0), 0, True, True, ("hd_pm", "hd_unspecified")),
    "TWILIGHT": TripClass("TWILIGHT", "16:00", 0, 1, time(0, 0), 0, False, False, ("hd_twilight",)),
    "THREE_QUARTER": TripClass("THREE_QUARTER", "21:00", 0, 0, time(19, 30), 0, True, False, ("three_quarter",)),
    "FULL_DAY": TripClass("FULL_DAY", "21:00", 0, 1, time(0, 0), 0, True, False, ("full_day",)),
    "OVERNIGHT": TripClass("OVERNIGHT", "16:00", 1, 1, time(19, 0), 1, True, False, ("overnight",)),
    "DAY_1_5": TripClass("DAY_1_5", "16:00", 1, 2, time(6, 0), 2, True, False, ("day_1_5",)),
}
SOURCE_TO_CLASS = {s: c.name for c in CLASSES.values() for s in c.source_cls}


@dataclass
class Offer:
    id: str
    cls: str
    departure: date
    fishing_dates: list[date]
    return_at: datetime
    cost: int
    pto_need: dict[date, float]        # date -> PTO days required
    bookable: bool = True
    reason: str = ""
    extra: dict = field(default_factory=dict)


def pto_need(tc: TripClass, d: date, half_day_pto: float) -> dict[date, float]:
    if not tc.needs_pto:
        return {}
    days = {d + timedelta(days=tc.fish_offset), d + timedelta(days=tc.return_pto_offset)}
    per_day = half_day_pto if tc.half_day else 1.0
    return {x: per_day for x in sorted(days) if cal.is_weekday(x)}


def make_offer(tc: TripClass, d: date, prices: dict, half_day_pto: float) -> Offer:
    return Offer(
        id=f"{tc.name}:{cal.day_number(d)}", cls=tc.name, departure=d,   # masked id: day number, never a calendar date
        fishing_dates=[d + timedelta(days=tc.fish_offset)],
        return_at=datetime.combine(d + timedelta(days=tc.return_offset), tc.return_time),
        cost=int(prices[tc.name]), pto_need=pto_need(tc, d, half_day_pto))


def offers_at(today: date, tick: str, prices: dict, half_day_pto: float) -> list[Offer]:
    out = []
    for tc in CLASSES.values():
        if tc.tick != tick:
            continue
        d = today + timedelta(days=1) if tick == "21:00" else today
        out.append(make_offer(tc, d, prices, half_day_pto))
    return out


def offers_for_judgment(today: date, prices: dict, half_day_pto: float) -> list[Offer]:
    """D-058: the 21:00 judgment call sees every class departing tomorrow, evening departures included
    (an overnight or 1.5-day for tomorrow evening is booked tonight, a day before its 16:00 cutoff)."""
    d = today + timedelta(days=1)
    return [make_offer(tc, d, prices, half_day_pto) for tc in CLASSES.values()]
