"""Pooling, dilution, climatology, season metrics, bootstrap (SPEC §3.3, §3.4)."""
import pandas as pd

from arena.engine import scoring


def _trips():
    rows = []
    for y in (2011, 2012, 2013):
        for doy in (200, 205, 210):
            d = pd.Timestamp(y, 1, 1) + pd.Timedelta(days=doy - 1)
            rows += [{"landing": "seaforth", "boat": "New Seaforth", "cls": "hd_pm", "fish_date": d, "anglers": 20, "yt": 2 if y < 2013 else 6},
                     {"landing": "hm", "boat": "Premier", "cls": "hd_unspecified", "fish_date": d, "anglers": 30, "yt": 3},
                     {"landing": "hm", "boat": "Ghost", "cls": "hd_pm", "fish_date": d, "anglers": None, "yt": 99},   # null anglers: dropped
                     {"landing": "oceanside", "boat": "X", "cls": "hd_pm", "fish_date": d, "anglers": 10, "yt": 50},   # excluded landing
                     {"landing": "seaforth", "boat": "Y", "cls": "multi_day", "fish_date": d, "anglers": 10, "yt": 50}]  # not an arena class
    return pd.DataFrame(rows)


def test_pooled_outcome_and_share():
    o = scoring.Outcomes(_trips(), ["seaforth", "fishermans", "hm", "point_loma"], "all")
    yt, ang, n = o.pooled_outcome("HD_PM", pd.Timestamp(2013, 1, 1).date() + pd.Timedelta(days=199))
    assert (yt, ang, n) == (9.0, 50.0, 2)
    assert o.pooled_outcome("OVERNIGHT", pd.Timestamp(2013, 7, 19).date()) is None
    assert scoring.share(9, 50, 0, 1.0) == 0.18
    assert scoring.share(9, 50, 2, 1.0) == 9 / 52 and scoring.share(9, 50, 2, 0.5) == 9 / 51


def test_pooled_boats_option():
    o = scoring.Outcomes(_trips(), ["seaforth", "fishermans", "hm", "point_loma"], ["New Seaforth", "Sea Watch"])
    assert o.pooled_outcome("HD_PM", pd.Timestamp(2013, 7, 19).date()) == (6.0, 20.0, 1)


def test_climatology_prior_seasons_only():
    o = scoring.Outcomes(_trips(), ["seaforth", "fishermans", "hm", "point_loma"], "all")
    d = pd.Timestamp(2013, 7, 19).date()          # doy 200; prior seasons 2011-2012: (2+3)*3*2 yt over 50*3*2 anglers
    assert abs(o.climatology("HD_PM", d) - 30 / 300) < 1e-9
    assert o.climatology("HD_PM", pd.Timestamp(2011, 7, 19).date()) is None   # nothing before the first season
    assert o.climatology("HD_PM", pd.Timestamp(2013, 3, 1).date()) is None    # outside the +-15 day window


def test_season_metrics_and_bootstrap():
    b = [{"settled": True, "ran": True, "share": 0.5, "yt": 5, "anglers": 10, "cls": "HD_PM", "fishing_dates": ["2013-07-19"], "cost": 80},
         {"settled": True, "ran": True, "share": 0.0, "yt": 0, "anglers": 10, "cls": "HD_PM", "fishing_dates": ["2013-07-20"], "cost": 80},
         {"settled": True, "ran": False, "share": None, "yt": None, "anglers": None, "cls": "DAY_1_5", "fishing_dates": ["2013-07-21"], "cost": 550},
         {"settled": False, "ran": None, "share": None, "yt": None, "anglers": None, "cls": "HD_PM", "fishing_dates": ["2013-07-22"], "cost": 80}]
    m = scoring.season_metrics(b, lambda c, d: 0.1, 2000, 10)
    assert m["fish"] == 0.5 and m["undiluted"] == 0.5 and abs(m["excess"] - 0.3) < 1e-9
    assert m["skunk_rate"] == 0.5 and m["trips"] == 2 and m["cancelled"] == 1 and m["usd_per_fish"] == 320.0
    ci = scoring.bootstrap_diff_ci([3, 4, 5, 6], [1, 1, 1, 1], seed=1)
    assert ci["mean"] == 3.5 and ci["lo95"] > 2 and ci["hi95"] < 5
    f = scoring.field_metrics({"a": {("HD_PM", "d1"), ("HD_PM", "d2")}, "b": {("HD_PM", "d1")}, "c": set()}, {("HD_PM", "d1"): 2, ("HD_PM", "d2"): 1})
    assert abs(f["diversity_jaccard"] - (0.5 + 0 + 0) / 3) < 1e-4 and abs(f["herding"] - 2 / 3) < 1e-4
