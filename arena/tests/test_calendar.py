"""PTO and calendar rules (SPEC §2 examples)."""
from datetime import date

from arena.engine import calendar as cal, offers as off

P = {k: 1 for k in off.CLASSES}


def pto(cls, d, half=1.0):
    return sorted(x.strftime("%a") for x in off.make_offer(off.CLASSES[cls], d, P, half).pto_need)


def test_spec_examples():
    assert pto("OVERNIGHT", date(2023, 7, 7)) == []              # Fri -> fishes Sat -> 0
    assert pto("OVERNIGHT", date(2023, 7, 9)) == ["Mon"]         # Sun -> fishes Mon -> 1
    assert pto("DAY_1_5", date(2023, 7, 7)) == []                # Fri -> Sat, back Sun 06:00 -> 0
    assert pto("DAY_1_5", date(2023, 7, 8)) == ["Mon"]           # Sat -> back Mon 06:00 -> 1
    assert pto("DAY_1_5", date(2023, 7, 9)) == ["Mon", "Tue"]    # Sun -> fishes Mon, back Tue -> 2
    assert pto("HD_PM", date(2023, 7, 5)) == ["Wed"]             # Wed -> 1
    assert pto("TWILIGHT", date(2023, 7, 5)) == []               # twilight never costs PTO (D-049)


def test_federal_holiday_costs_nothing():
    assert not cal.is_weekday(date(2023, 7, 4))
    assert pto("HD_PM", date(2023, 7, 4)) == []
    # Mon Jul 3 evening departure fishes Tue Jul 4 (holiday) and returns Tue: no PTO
    assert pto("OVERNIGHT", date(2023, 7, 3)) == []


def test_half_day_pto_option():
    o = off.make_offer(off.CLASSES["HD_PM"], date(2023, 7, 5), P, 0.5)
    assert list(o.pto_need.values()) == [0.5]
    o = off.make_offer(off.CLASSES["THREE_QUARTER"], date(2023, 7, 5), P, 0.5)
    assert list(o.pto_need.values()) == [1.0]


def test_offer_ticks_and_returns():
    o21 = {o.cls for o in off.offers_at(date(2023, 7, 6), "21:00", P, 1.0)}
    o16 = {o.cls for o in off.offers_at(date(2023, 7, 7), "16:00", P, 1.0)}
    assert o21 == {"HD_AM", "HD_PM", "THREE_QUARTER", "FULL_DAY"} and o16 == {"TWILIGHT", "OVERNIGHT", "DAY_1_5"}
    for o in off.offers_at(date(2023, 7, 6), "21:00", P, 1.0):
        assert o.departure == date(2023, 7, 7)
    ov = off.make_offer(off.CLASSES["OVERNIGHT"], date(2023, 7, 7), P, 1.0)
    assert ov.fishing_dates == [date(2023, 7, 8)] and ov.return_at.isoformat() == "2023-07-08T19:00:00"
    d15 = off.make_offer(off.CLASSES["DAY_1_5"], date(2023, 7, 7), P, 1.0)
    assert d15.fishing_dates == [date(2023, 7, 8)] and d15.return_at.isoformat() == "2023-07-09T06:00:00"


def test_masked_timeline():
    n = cal.day_number(date(2012, 2, 29))
    assert cal.from_day_number(n) == date(2012, 2, 29)
    assert cal.season_index(date(2012, 2, 29), 2010) == 3
    assert cal.days_in_year(2012) == 366 and cal.days_in_year(2013) == 365


def test_offer_ids_carry_no_calendar_date():
    for o in off.offers_at(date(2023, 7, 6), "21:00", P, 1.0) + off.offers_at(date(2023, 7, 6), "16:00", P, 1.0):
        assert "2023" not in o.id and o.id.split(":")[1].isdigit()
