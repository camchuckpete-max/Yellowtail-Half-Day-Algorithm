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
from yt import events, features, source  # noqa: E402


def _load():
    m = source.source_manifest()
    db = source.open_db(m)
    return events.load_trips(db), events.load_forecasts(db)


def _poison(df: pd.DataFrame, cutoff: pd.Timestamp, rng, cols) -> pd.DataFrame:
    df = df.copy()
    after = df["available_at"] > cutoff
    for c in cols:
        df.loc[after, c] = rng.integers(0, 500, after.sum())
    return df


def test_future_events_do_not_change_features(n_days: int = 60, seed: int = 7):
    trips, fc = _load()
    rng = np.random.default_rng(seed)
    all_days = pd.DatetimeIndex(sorted(trips.loc[trips["is_hd_fishing"], "fished_date"].unique()))
    all_days = all_days[all_days >= all_days[0] + pd.Timedelta(days=30)]
    days = pd.DatetimeIndex(rng.choice(all_days, n_days, replace=False)).sort_values()
    cols = [c for c in features.FEATURES]
    for D in days:
        c = features.cutoff_for(D)
        base = features.build(trips, fc, pd.DatetimeIndex([D]))[cols]
        # 1) poison every count/forecast value that is public only after the cutoff
        pt = _poison(trips, c, rng, ["yt", "bonito", "barracuda", "calico", "rockfish", "anglers"])
        pf = _poison(fc, c, rng, ["wind_kt", "swell_ft", "swell_s"])
        poisoned = features.build(pt, pf, pd.DatetimeIndex([D]))[cols]
        # 2) delete everything public after the cutoff
        tt = trips[trips["available_at"] <= c]
        ff = fc[fc["available_at"] <= c]
        truncated = features.build(tt, ff, pd.DatetimeIndex([D]))[cols]
        pd.testing.assert_frame_equal(base, poisoned, check_dtype=False, obj=f"poisoned {D.date()}")
        pd.testing.assert_frame_equal(base, truncated, check_dtype=False, obj=f"truncated {D.date()}")


def test_target_day_catch_is_never_visible():
    trips, _ = _load()
    for D in pd.DatetimeIndex(trips["fished_date"].unique()):
        c = features.cutoff_for(D)
        assert not ((trips["fished_date"] >= D) & (trips["available_at"] <= c)).any(), D


def test_twilight_d1_not_visible():
    trips, _ = _load()
    tw = trips[trips["cls"] == "hd_twilight"]
    assert (tw["available_at"] > tw["fished_date"] + pd.Timedelta(hours=21)).all()


if __name__ == "__main__":
    test_target_day_catch_is_never_visible()
    test_twilight_d1_not_visible()
    test_future_events_do_not_change_features()
    print("PIT tests passed")
