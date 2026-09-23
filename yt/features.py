"""Point-in-time (PIT) feature builder.

For target day D the prediction is made at CUTOFF = D-1 21:00 PT. The ONLY
data a feature may read is `visible = events[available_at <= CUTOFF]`,
obtained through `_visible()`. No other code path touches the event tables.
tests/test_pit.py proves this by poisoning every event after the cutoff and
checking that features do not change.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

CUTOFF_HOUR = 21  # 9pm PT, per requirement 2
SYNODIC = 29.530588853
REF_NEW_MOON = pd.Timestamp("2000-01-06 18:14")  # astronomical constant (UTC)

HD_FISH_CLASSES = ("hd_am", "hd_pm", "hd_unspecified", "hd_twilight")
OTHER_CLASSES = ("three_quarter", "full_day", "overnight", "multi_day")


def cutoff_for(day: pd.Timestamp) -> pd.Timestamp:
    return day - pd.Timedelta(days=1) + pd.Timedelta(hours=CUTOFF_HOUR)


def _visible(df: pd.DataFrame, avail: np.ndarray, cutoff: pd.Timestamp) -> pd.DataFrame:
    """Events are sorted by available_at; return the prefix visible at cutoff."""
    i = np.searchsorted(avail, np.datetime64(cutoff), side="right")
    return df.iloc[:i]


def moon(day: pd.Timestamp) -> tuple[float, float]:
    """(illuminated fraction, phase in [0,1)) at local noon; pure calendar math."""
    age = ((day + pd.Timedelta(hours=19) - REF_NEW_MOON).total_seconds() / 86400.0) % SYNODIC
    phase = age / SYNODIC
    return (1 - math.cos(2 * math.pi * phase)) / 2, phase


def _fd_features(D: pd.Timestamp, fd_rep: pd.DataFrame) -> dict:
    """FishDope yellowtail mentions from reports visible at the cutoff (D-020)."""
    f: dict = {}
    rd = fd_rep["report_date"]
    def rep(k, start=1):
        return fd_rep[(rd >= D - pd.Timedelta(days=k)) & (rd <= D - pd.Timedelta(days=start))]
    d1 = rep(1)
    f["fd_visible_d1"] = int(len(d1) > 0)
    for reg in ("local", "coronado", "north", "all"):
        f[f"fd_yt_{reg}_d1"] = math.log1p(float(d1[f"yt_{reg}"].max())) if len(d1) else 0.0
    r3 = rep(3)
    f["fd_yt_local_3"] = math.log1p(float(r3["yt_local"].sum()))
    f["fd_yt_local_days_3"] = int((r3.groupby("report_date")["yt_local"].max() > 0).sum()) if len(r3) else 0
    f["fd_yt_local_prev4_7"] = math.log1p(float(rep(7, 4)["yt_local"].sum()))
    f["fd_yt_coronado_3"] = math.log1p(float(r3["yt_coronado"].sum()))
    f["audit_fd_max_available_at"] = fd_rep["available_at"].max() if len(fd_rep) else pd.NaT
    f["audit_fd_d1_src_id"] = int(d1["src_id"].iloc[-1]) if len(d1) else -1
    return f


def _day_features(D: pd.Timestamp, trips: pd.DataFrame, fc: pd.DataFrame) -> dict:
    cutoff = cutoff_for(D)
    f: dict = {"date": D, "cutoff": cutoff}
    f["audit_n_visible_trips"] = len(trips)
    f["audit_max_trip_available_at"] = trips["available_at"].max() if len(trips) else pd.NaT

    fd = trips["fished_date"].to_numpy()
    cls = trips["cls"].to_numpy()
    yt = trips["yt"].to_numpy()
    is_hd = np.isin(cls, HD_FISH_CLASSES)
    is_oth = np.isin(cls, OTHER_CLASSES)

    def win(k: int, start: int = 1) -> np.ndarray:
        lo = np.datetime64(D - pd.Timedelta(days=k))
        hi = np.datetime64(D - pd.Timedelta(days=start))
        return (fd >= lo) & (fd <= hi)

    hd_yt_days = lambda m: len(np.unique(fd[m & is_hd & (yt > 0)]))
    hd_cov_days = lambda m: len(np.unique(fd[m & is_hd]))

    w1, w3, w7, w14, w30 = win(1), win(3), win(7), win(14), win(30)
    f["hd_cov_d1"] = int((w1 & is_hd).sum())
    f["hd_yt_d1"] = int(hd_yt_days(w1) > 0)
    # Most recent day with any visible half-day report (== D-1 normally; D-2 under
    # --strict or when D-1 had no public AM/PM trips). Baseline B1 input (D-016).
    hd_dates = fd[is_hd]
    if len(hd_dates):
        lastday = hd_dates.max()
        f["hd_yt_lastday"] = int(((fd == lastday) & is_hd & (yt > 0)).any())
        f["hd_lastday_age"] = int((np.datetime64(D) - lastday) / np.timedelta64(1, "D"))
    else:
        f["hd_yt_lastday"], f["hd_lastday_age"] = 0, 999
    for k, w in ((3, w3), (7, w7), (14, w14), (30, w30)):
        f[f"hd_ytdays_{k}"] = hd_yt_days(w)
    f["hd_covdays_7"] = hd_cov_days(w7)
    f["hd_covdays_30"] = hd_cov_days(w30)
    f["hd_ytrate_7"] = f["hd_ytdays_7"] / f["hd_covdays_7"] if f["hd_covdays_7"] else 0.0
    f["hd_ytrate_30"] = f["hd_ytdays_30"] / f["hd_covdays_30"] if f["hd_covdays_30"] else 0.0
    f["hd_ytdays_prev7"] = hd_yt_days(win(14, 8))
    # D-1 intensity (only D-1 trips already public at the cutoff: AM/PM/unspecified).
    d1 = w1 & is_hd
    f["hd_yt_trip_frac_d1"] = float((yt[d1] > 0).mean()) if d1.any() else 0.0
    f["hd_log_ytfish_d1"] = math.log1p(float(yt[d1].sum()))
    f["hd_yt_landings_d1"] = len(set(trips["landing"].to_numpy()[d1 & (yt > 0)]))
    f["hd_yt_am_d1"] = int((w1 & (cls == "hd_am") & (yt > 0)).any())
    f["hd_yt_pm_d1"] = int((w1 & np.isin(cls, ("hd_pm", "hd_unspecified")) & (yt > 0)).any())
    boats = trips["boat"].to_numpy()
    f["hd_yt_boats_3"] = len(set(boats[w3 & is_hd & (yt > 0)]))
    f["hd_yt_boats_7"] = len(set(boats[w7 & is_hd & (yt > 0)]))
    lands = trips["landing"].to_numpy()
    for ln in ("seaforth", "fishermans", "hm", "point_loma"):
        f[f"hd_yt_{ln}_3"] = int((w3 & is_hd & (yt > 0) & (lands == ln)).any())
    w2 = win(2, 2)
    f["hd_yt_d2"] = int(((w2 & is_hd) & (yt > 0)).any())  # D-2 incl. twilight
    f["tq_yt_d1"] = int(((w1 & (cls == "three_quarter")) & (yt > 0)).any())
    streak = 0
    ytd = set(pd.DatetimeIndex(fd[is_hd & (yt > 0)]).normalize())
    while (D - pd.Timedelta(days=streak + 1)) in ytd:
        streak += 1
    f["hd_yt_streak"] = streak
    n7 = int((w7 & is_hd).sum())
    f["hd_ntrips_7"] = n7
    f["hd_ytfish_7"] = int(yt[w7 & is_hd].sum())
    f["hd_ytfish_per_trip_7"] = f["hd_ytfish_7"] / n7 if n7 else 0.0
    f["hd_log_ytfish_7"] = math.log1p(f["hd_ytfish_7"])
    for sp in ("bonito", "barracuda", "calico", "rockfish"):
        v = trips[sp].to_numpy()
        f[f"hd_{sp}_per_trip_7"] = float(v[w7 & is_hd].sum()) / n7 if n7 else 0.0
    last = fd[is_hd & (yt > 0)]
    f["hd_days_since_yt"] = min(365, int((np.datetime64(D) - last.max()) / np.timedelta64(1, "D"))) if len(last) else 365

    no7 = int((w7 & is_oth).sum())
    f["oth_ntrips_7"] = no7
    f["oth_yt_per_trip_7"] = float(yt[w7 & is_oth].sum()) / no7 if no7 else 0.0
    f["oth_log_yt_3"] = math.log1p(float(yt[w3 & is_oth].sum()))
    f["oth_log_yt_7"] = math.log1p(float(yt[w7 & is_oth].sum()))
    tq = w7 & (cls == "three_quarter")
    f["tq_log_yt_7"] = math.log1p(float(yt[tq].sum()))
    ov = w7 & np.isin(cls, ("overnight", "multi_day"))
    f["ov_log_yt_7"] = math.log1p(float(yt[ov].sum()))

    # Climatology from PRIOR years only (same +-15 day-of-year window).
    doy = D.dayofyear
    prior = is_hd & (fd < np.datetime64(pd.Timestamp(D.year, 1, 1)))
    if prior.any():
        pdates = pd.DatetimeIndex(fd[prior])
        d = np.abs(pdates.dayofyear.to_numpy() - doy)
        d = np.minimum(d, 365 - d)
        sel = d <= 15
        sub = pd.DataFrame({"d": pdates[sel], "yt": yt[prior][sel]}).groupby("d")["yt"].sum()
        f["clim_n"] = len(sub)
        f["clim_rate"] = float((sub > 0).mean()) if len(sub) else float("nan")
    else:
        f["clim_n"], f["clim_rate"] = 0, float("nan")

    f["doy_sin"] = math.sin(2 * math.pi * doy / 365.25)
    f["doy_cos"] = math.cos(2 * math.pi * doy / 365.25)
    f["weekend"] = int(D.dayofweek >= 5)
    f["moon_illum"], ph = moon(D)
    f["moon_sin"], f["moon_cos"] = math.sin(2 * math.pi * ph), math.cos(2 * math.pi * ph)

    # Latest forecast for D issued at or before the cutoff.
    cand = fc[fc["target_date"] == D]
    if len(cand):
        r = cand.iloc[-1]
        f["fc_wind_kt"], f["fc_swell_ft"], f["fc_swell_s"] = r["wind_kt"], r["swell_ft"], r["swell_s"]
        f["audit_fc_src_id"], f["audit_fc_available_at"] = int(r["src_id"]), r["available_at"]
    else:
        f["fc_wind_kt"] = f["fc_swell_ft"] = f["fc_swell_s"] = float("nan")
        f["audit_fc_src_id"], f["audit_fc_available_at"] = -1, pd.NaT
    return f


def build(trips: pd.DataFrame, fc: pd.DataFrame, days: pd.DatetimeIndex,
          fd_rep: pd.DataFrame | None = None) -> pd.DataFrame:
    t_av = trips["available_at"].to_numpy()
    f_av = fc["available_at"].to_numpy()
    d_av = fd_rep["available_at"].to_numpy() if fd_rep is not None else None
    out = []
    for D in days:
        c = cutoff_for(D)
        vt = _visible(trips, t_av, c)
        vf = _visible(fc, f_av, c)
        row = _day_features(D, vt, vf)
        if fd_rep is not None:
            row.update(_fd_features(D, _visible(fd_rep, d_av, c)))
            assert pd.isna(row["audit_fd_max_available_at"]) or row["audit_fd_max_available_at"] <= c
        # Hard guard: nothing used may postdate the cutoff.
        assert pd.isna(row["audit_max_trip_available_at"]) or row["audit_max_trip_available_at"] <= c
        assert pd.isna(row["audit_fc_available_at"]) or row["audit_fc_available_at"] <= c
        out.append(row)
    return pd.DataFrame(out)


FEATURES = [
    "hd_yt_d1", "hd_yt_lastday", "hd_lastday_age", "hd_cov_d1", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_14", "hd_ytdays_30",
    "hd_covdays_7", "hd_covdays_30", "hd_ytrate_7", "hd_ytrate_30", "hd_ytdays_prev7",
    "hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak",
    "hd_yt_am_d1", "hd_yt_pm_d1", "hd_yt_boats_3", "hd_yt_boats_7",
    "hd_yt_seaforth_3", "hd_yt_fishermans_3", "hd_yt_hm_3", "hd_yt_point_loma_3",
    "hd_ntrips_7", "hd_ytfish_per_trip_7", "hd_log_ytfish_7",
    "hd_bonito_per_trip_7", "hd_barracuda_per_trip_7", "hd_calico_per_trip_7", "hd_rockfish_per_trip_7",
    "hd_days_since_yt", "oth_ntrips_7", "oth_yt_per_trip_7", "oth_log_yt_3", "oth_log_yt_7",
    "tq_log_yt_7", "ov_log_yt_7", "clim_rate", "doy_sin", "doy_cos", "weekend",
    "moon_illum", "moon_sin", "moon_cos", "fc_wind_kt", "fc_swell_ft", "fc_swell_s",
    "fd_visible_d1", "fd_yt_local_d1", "fd_yt_coronado_d1", "fd_yt_north_d1", "fd_yt_all_d1",
    "fd_yt_local_3", "fd_yt_local_days_3", "fd_yt_local_prev4_7", "fd_yt_coronado_3",
]
