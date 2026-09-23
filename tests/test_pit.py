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
from yt import dataset, events, features, source  # noqa: E402


def _load():
    m = source.source_manifest()
    db = source.open_db(m)
    return (events.load_trips(db), events.load_forecasts(db), events.load_fishdope(db)[0],
            events.load_marine_forecasts(db))


def _poison(df: pd.DataFrame, cutoff: pd.Timestamp, rng, cols) -> pd.DataFrame:
    df = df.copy()
    after = df["available_at"] > cutoff
    for c in cols:
        df.loc[after, c] = rng.integers(0, 500, after.sum())
    return df


def test_future_events_do_not_change_features(n_days: int = 60, seed: int = 7):
    trips, fc, fd, mf = _load()
    rng = np.random.default_rng(seed)
    all_days = pd.DatetimeIndex(sorted(trips.loc[trips["is_hd_fishing"], "fished_date"].unique()))
    all_days = all_days[all_days >= all_days[0] + pd.Timedelta(days=30)]
    days = pd.DatetimeIndex(rng.choice(all_days, n_days, replace=False)).sort_values()
    cols = [c for c in features.FEATURES]
    for D in days:
        c = features.cutoff_for(D)
        base = features.build(trips, fc, pd.DatetimeIndex([D]), fd, mf)[cols]
        # 1) poison every count/forecast value that is public only after the cutoff
        pt = _poison(trips, c, rng, ["yt", "bonito", "barracuda", "calico", "rockfish", "anglers"])
        pf = _poison(fc, c, rng, ["wind_kt", "swell_ft", "swell_s"])
        pd_ = _poison(fd, c, rng, [k for k in fd.columns if k.startswith(("yt_", "wt_", "bait_"))])
        pm = _poison(mf, c, rng, [k for k in mf.columns if k.startswith("mf_")])
        poisoned = features.build(pt, pf, pd.DatetimeIndex([D]), pd_, pm)[cols]
        # 2) delete everything public after the cutoff
        tt = trips[trips["available_at"] <= c]
        ff = fc[fc["available_at"] <= c]
        truncated = features.build(tt, ff, pd.DatetimeIndex([D]), fd[fd["available_at"] <= c],
                                   mf[mf["available_at"] <= c])[cols]
        pd.testing.assert_frame_equal(base, poisoned, check_dtype=False, obj=f"poisoned {D.date()}")
        pd.testing.assert_frame_equal(base, truncated, check_dtype=False, obj=f"truncated {D.date()}")


def test_target_day_catch_is_never_visible():
    trips, _, _, _ = _load()
    for D in pd.DatetimeIndex(trips["fished_date"].unique()):
        c = features.cutoff_for(D)
        assert not ((trips["fished_date"] >= D) & (trips["available_at"] <= c)).any(), D


def test_fishdope_same_day_report_never_visible():
    _, _, fd, _ = _load()
    # A report about day D (or later) can never be visible at D-1 21:00.
    assert (fd["available_at"] > fd["report_date"] - pd.Timedelta(hours=3)).all()


def test_dataset_audit_columns_respect_cutoff():
    df, _ = dataset.build()
    for col in ("audit_max_trip_available_at", "audit_fc_available_at", "audit_fd_max_available_at",
                "audit_mf_available_at"):
        ok = df[col].isna() | (df[col] <= df["cutoff"])
        assert ok.all(), col


def test_twilight_d1_not_visible():
    trips, _, _, _ = _load()
    tw = trips[trips["cls"] == "hd_twilight"]
    assert (tw["available_at"] > tw["fished_date"] + pd.Timedelta(hours=21)).all()


def test_marine_forecast_not_before_issue():
    # Sanity on the issue-time stamping (D-C02): every daytime period is valid 0-7 days after
    # the day its product became available (one 2010-11-25 product archived the next day is -1).
    _, _, _, mf = _load()
    lead = (mf["target_date"] - mf["available_at"].dt.normalize()).dt.days
    assert lead.between(-1, 7).all() and (lead < 0).sum() <= 5
    assert mf["available_at"].is_monotonic_increasing


def test_env_columns_poisoned_are_real():
    # Guard against the poison test silently skipping new columns.
    _, _, fd, mf = _load()
    assert {"wt_all", "wt_local", "bait_local_squid"} <= set(fd.columns)
    assert {"mf_wind_max", "mf_swell_south"} <= set(mf.columns)
    assert fd["wt_all"].notna().sum() > 300 and len(mf) > 10000


if __name__ == "__main__":
    test_marine_forecast_not_before_issue()
    test_env_columns_poisoned_are_real()
    test_target_day_catch_is_never_visible()
    test_twilight_d1_not_visible()
    test_fishdope_same_day_report_never_visible()
    test_dataset_audit_columns_respect_cutoff()
    test_future_events_do_not_change_features()
    print("PIT tests passed")
