"""No-lookahead proof: poisoning or deleting every event that becomes public
after the D-1 21:00 PT cutoff must not change any feature for day D.

Run: python3 -m pytest -q tests/   (or: python3 tests/test_pit.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yt import dataset, events, features, hourly, source  # noqa: E402


def _load():
    m = source.source_manifest()
    db = source.open_db(m)
    return (events.load_trips(db), events.load_forecasts(db), events.load_fishdope(db)[0],
            events.load_marine_forecasts(db), events.load_tides(db), events.load_ocean(db))


def _poison(df: pd.DataFrame, cutoff: pd.Timestamp, rng, cols) -> pd.DataFrame:
    df = df.copy()
    after = df["available_at"] > cutoff
    for c in cols:
        df.loc[after, c] = rng.integers(0, 500, after.sum())
    return df


def test_future_events_do_not_change_features(n_days: int = 60, seed: int = 7):
    trips, fc, fd, mf, td, oc = _load()
    rng = np.random.default_rng(seed)
    all_days = pd.DatetimeIndex(sorted(trips.loc[trips["is_hd_fishing"], "fished_date"].unique()))
    all_days = all_days[all_days >= all_days[0] + pd.Timedelta(days=30)]
    days = pd.DatetimeIndex(rng.choice(all_days, n_days, replace=False)).sort_values()
    days = days.union(pd.DatetimeIndex(rng.choice(all_days[all_days >= "2020-02-01"], 20, replace=False)))
    cols = [c for c in features.FEATURES]
    for D in days:
        c = features.cutoff_for(D)
        base = features.build(trips, fc, pd.DatetimeIndex([D]), fd, mf, td, oc)[cols]
        # 1) poison every count/forecast value that is public only after the cutoff
        pt = _poison(trips, c, rng, ["yt", "bonito", "barracuda", "calico", "rockfish", "anglers",
                                          "mackerel", "sand_bass", "halibut", "white_seabass", "sheephead", "whitefish"])
        pf = _poison(fc, c, rng, ["wind_kt", "swell_ft", "swell_s", "wind_dir", "swell_dir"])
        pd_ = _poison(fd, c, rng, [k for k in fd.columns if k.startswith(("yt_", "wt_", "bait_"))])
        pm = _poison(mf, c, rng, [k for k in mf.columns if k.startswith("mf_")])
        ptd = _poison(td, c, rng, ["tide_high_ft", "tide_low_ft"])
        poc = _poison(oc, c, rng, ["sst_f", "chl", "cur_kt", "cur_dir"])
        poisoned = features.build(pt, pf, pd.DatetimeIndex([D]), pd_, pm, ptd, poc)[cols]
        # 2) delete everything public after the cutoff
        tt = trips[trips["available_at"] <= c]
        ff = fc[fc["available_at"] <= c]
        truncated = features.build(tt, ff, pd.DatetimeIndex([D]), fd[fd["available_at"] <= c],
                                   mf[mf["available_at"] <= c], td[td["available_at"] <= c],
                                   oc[oc["available_at"] <= c])[cols]
        pd.testing.assert_frame_equal(base, poisoned, check_dtype=False, obj=f"poisoned {D.date()}")
        pd.testing.assert_frame_equal(base, truncated, check_dtype=False, obj=f"truncated {D.date()}")


def test_target_day_catch_is_never_visible():
    trips, _, _, _, _, _ = _load()
    for D in pd.DatetimeIndex(trips["fished_date"].unique()):
        c = features.cutoff_for(D)
        assert not ((trips["fished_date"] >= D) & (trips["available_at"] <= c)).any(), D


def test_fishdope_same_day_report_never_visible():
    _, _, fd, _, _, _ = _load()
    # A report about day D (or later) can never be visible at D-1 21:00.
    assert (fd["available_at"] > fd["report_date"] - pd.Timedelta(hours=3)).all()


def test_dataset_audit_columns_respect_cutoff():
    df, _ = dataset.build()
    for col in ("audit_max_trip_available_at", "audit_fc_available_at", "audit_fd_max_available_at",
                "audit_mf_available_at", "audit_tide_available_at", "audit_ocean_available_at"):
        ok = df[col].isna() | (df[col] <= df["cutoff"])
        assert ok.all(), col


def test_twilight_d1_not_visible():
    trips, _, _, _, _, _ = _load()
    tw = trips[trips["cls"] == "hd_twilight"]
    assert (tw["available_at"] > tw["fished_date"] + pd.Timedelta(hours=21)).all()


def test_marine_forecast_not_before_issue():
    # Sanity on the issue-time stamping (D-C02): every daytime period is valid 0-7 days after
    # the day its product became available (one 2010-11-25 product archived the next day is -1).
    _, _, _, mf, _, _ = _load()
    lead = (mf["target_date"] - mf["available_at"].dt.normalize()).dt.days
    assert lead.between(-1, 7).all() and (lead < 0).sum() <= 5
    assert mf["available_at"].is_monotonic_increasing


def test_env_columns_poisoned_are_real():
    # Guard against the poison test silently skipping new columns.
    _, _, fd, mf, _, _ = _load()
    assert {"wt_all", "wt_local", "bait_local_squid"} <= set(fd.columns)
    assert {"mf_wind_max", "mf_swell_south"} <= set(mf.columns)
    assert fd["wt_all"].notna().sum() > 300 and len(mf) > 10000


def test_ocean_present_and_lagged():
    *_, oc = _load()
    # SST starts 2020-01-01, or 2010-01-01 once the request-0001 backfill is present (D-042).
    assert oc["sst_f"].notna().sum() > 20000 and oc["target_date"].min() <= pd.Timestamp("2020-01-01")
    # Data dated D-1 must never be visible at the D-1 21:00 cutoff; D-2 SST may be.
    assert ((oc["available_at"] - oc["target_date"]) >= pd.Timedelta(days=1, hours=20)).all()
    for D in pd.DatetimeIndex(["2021-07-15", "2023-03-02"]):
        vis = oc[oc["available_at"] <= features.cutoff_for(D)]
        assert vis["target_date"].max() <= D - pd.Timedelta(days=2)


def test_tides_present():
    *_, td, _ = _load()
    assert td["tide_high_ft"].notna().sum() > 5000 and td["target_date"].min() <= pd.Timestamp("2010-01-01")


def test_conditions_guard():
    features.assert_conditions_only(["doy_sin", "cd_upw_14", "tide_range_d*moon_cos", "!weekend"])
    for bad in ("hd_yt_lastday", "fd_local_catch_d1", "wt_c", "clim_rate", "cd_upw_7*hd_ytdays_7"):
        try:
            features.assert_conditions_only([bad])
        except ValueError:
            continue
        raise AssertionError(f"guard let {bad} through")


def test_hourly_trip_features_pit(n: int = 25, seed: int = 11):
    """Goal D hc_* features: poisoning / deleting every observation after the D-1 21:00 cutoff
    (and every index value not yet published) must not change them. Tide predictions are exempt
    by design (published years ahead) and are left intact."""
    db = source.open_db(source.source_manifest())
    data = hourly.load(db)
    rng = np.random.default_rng(seed)
    days = pd.DatetimeIndex(rng.choice(pd.date_range("2012-01-01", "2023-12-31"), n, replace=False))
    for D in days:
        for cls in ("hd_am", "hd_pm", "hd_twilight"):
            c = D - pd.Timedelta(days=1) + pd.Timedelta(hours=21)
            base = hourly.trip_features(D, cls, data, c)
            pois = {"tides": data["tides"]}
            p = data["pier"].copy(); m = p["ts"] > c
            p.loc[m, ["wtmp_c", "atmp_c"]] = rng.uniform(0, 40, (m.sum(), 2)); pois["pier"] = p
            pois["buoy"] = {}
            for s, g in data["buoy"].items():
                g = g.copy(); m = g["ts"] > c
                for col in ("wtmp_c", "wspd_ms", "wvht_m", "dpd_s"):
                    g.loc[m, col] = rng.uniform(0, 30, m.sum())
                pois["buoy"][s] = g
            g = data["metar"].copy(); m = g["ts"] > c
            for col in ("drct", "sknt", "mslp", "relh", "vsby_sm", "onshore"):
                g.loc[m, col] = rng.uniform(0, 999, m.sum())
            pois["metar"] = g
            g = data["chl"].copy()  # D-048: rows for days after D-1 are not visible
            m = g["date"] > (c - pd.Timedelta(hours=21)).normalize() - pd.Timedelta(days=hourly.CHL_LAG_DAYS - 1)
            g.loc[m, "logchl"] = rng.uniform(-9, 9, m.sum()); pois["chl"] = g
            for k, cols in (("upw", ("cuti", "beuti")), ("climate", ("value",)), ("glider", ("temp_c",)),
                            ("sla", ("sla_m",)), ("kelp", ("kelp_area_ha",))):
                g = data[k].copy(); m = g["available_at"] > c
                for col in cols:
                    g.loc[m, col] = rng.uniform(-9, 9, m.sum())
                pois[k] = g
            got = hourly.trip_features(D, cls, pois, c)
            for k in hourly.HC_FEATURES:
                a, b = base[k], got[k]
                assert (np.isnan(a) and np.isnan(b)) or a == b, (D, cls, k, a, b)


def test_explanatory_features_blocked_from_predictive():
    from yt import trips
    df = pd.DataFrame({"date": pd.to_datetime(["2015-01-01"]), "y": [0], "ex_wind_trip_mean": [1.0]})
    try:
        trips.walk_forward(df, ["ex_wind_trip_mean"], [2015], track="P")
    except AssertionError:
        return
    raise AssertionError("ex_ feature accepted in a predictive run")


if __name__ == "__main__":
    test_explanatory_features_blocked_from_predictive()
    test_hourly_trip_features_pit()
    test_conditions_guard()
    test_tides_present()
    test_ocean_present_and_lagged()
    test_marine_forecast_not_before_issue()
    test_env_columns_poisoned_are_real()
    test_target_day_catch_is_never_visible()
    test_twilight_d1_not_visible()
    test_fishdope_same_day_report_never_visible()
    test_dataset_audit_columns_respect_cutoff()
    test_future_events_do_not_change_features()
    print("PIT tests passed")
