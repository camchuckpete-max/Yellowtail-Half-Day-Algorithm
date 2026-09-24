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
from yt import dataset, events, features, source, tripmodel  # noqa: E402


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
        pt = _poison(trips, c, rng, ["yt", "bonito", "barracuda", "calico", "rockfish", "anglers",
                                          "mackerel", "sand_bass", "halibut", "white_seabass", "sheephead", "whitefish"])
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


def test_trip_model_features_use_only_public_trips(n_days: int = 5, seed: int = 11):
    """D-E01: the trip-level models are fit inside the feature. Poisoning (counts, anglers and boat
    names) or deleting every trip public after cutoff(D) must not change the day-D trip-model features,
    and the candidate-row inputs for D must equal those built from the truncated table."""
    trips, _, _, _ = _load()
    rng = np.random.default_rng(seed)
    all_days = pd.DatetimeIndex(sorted(trips.loc[trips["is_hd_fishing"], "fished_date"].unique()))
    all_days = all_days[(all_days >= pd.Timestamp("2011-01-01")) & (all_days < pd.Timestamp("2017-01-01"))]
    days = pd.DatetimeIndex(rng.choice(all_days, n_days, replace=False)).sort_values()
    names = trips["boat"].unique()
    for D in days:
        c = features.cutoff_for(D)
        kw = {"C": 0.1, "boats": True, "refit_days": 7, "ext": True, "halflife": 365.0, "mix": True}
        base = tripmodel.build(trips, pd.DatetimeIndex([D]), **kw)
        pt = _poison(trips, c, rng, ["yt", "bonito", "barracuda", "calico", "rockfish", "anglers", "mackerel",
                                     "sand_bass", "halibut", "white_seabass", "sheephead", "whitefish"])
        after = pt["available_at"] > c
        pt.loc[after, "boat"] = rng.choice(names, after.sum())
        poisoned = tripmodel.build(pt, pd.DatetimeIndex([D]), **kw)
        truncated = tripmodel.build(trips[trips["available_at"] <= c], pd.DatetimeIndex([D]), **kw)
        rows_t = tripmodel.candidate_rows(trips[trips["available_at"] <= c],
                                          tripmodel.all_days(trips[trips["available_at"] <= c], pd.DatetimeIndex([D])))
        rows_f = tripmodel.candidate_rows(trips, tripmodel.all_days(trips, pd.DatetimeIndex([D])))
        for kind_kw in ({"kind": "hgb", "boats": True, "ext": True},):  # boosted yt model (D-E03)
            pd.testing.assert_frame_equal(tripmodel.build(trips, pd.DatetimeIndex([D]), rows=rows_f, **kind_kw),
                                          tripmodel.build(trips[trips["available_at"] <= c], pd.DatetimeIndex([D]),
                                                          rows=rows_t, **kind_kw),
                                          check_dtype=False, obj=f"hgb trip model truncated {D.date()}")
        assert base["tm_p"].notna().all(), D
        pd.testing.assert_frame_equal(base, poisoned, check_dtype=False, obj=f"trip model poisoned {D.date()}")
        pd.testing.assert_frame_equal(base, truncated, check_dtype=False, obj=f"trip model truncated {D.date()}")
        assert base[f"audit_tm_label_at"].iloc[0] <= c
        # candidate-row inputs for D (labels excluded) from the full vs truncated table
        full = tripmodel.candidate_rows(trips, pd.DatetimeIndex([D]))
        trunc = tripmodel.candidate_rows(trips[trips["available_at"] <= c], pd.DatetimeIndex([D]))
        x = [k for k in full.columns if k not in ("sailed", "yt")]
        pd.testing.assert_frame_equal(full[x], trunc[x], check_dtype=False, obj=f"candidate rows {D.date()}")


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
                "audit_mf_available_at", *[f"audit_{k}_label_at" for k in dataset.TRIP_VARIANTS]):
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
    test_trip_model_features_use_only_public_trips()
    print("PIT tests passed")
