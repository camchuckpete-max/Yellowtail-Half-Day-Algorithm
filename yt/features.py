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
WT_CENTER = 63.0  # F; centring constant for the dense water-temperature features (D-C03)

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
    # Sentence-level evidence (D-022)
    for reg in ("local", "coronado", "north"):
        for k in ("catch", "sight", "neg"):
            f[f"fd_{reg}_{k}_d1"] = int(d1[f"yt_{reg}_{k}"].max()) if len(d1) else 0
    f["fd_local_catch_3"] = int(r3["yt_local_catch"].sum()) if len(r3) else 0
    f["fd_local_catchdays_3"] = int((r3.groupby("report_date")["yt_local_catch"].max() > 0).sum()) if len(r3) else 0
    f["fd_local_sight_3"] = int(r3["yt_local_sight"].sum()) if len(r3) else 0
    f["fd_coronado_catch_3"] = int(r3["yt_coronado_catch"].sum()) if len(r3) else 0
    f["audit_fd_max_available_at"] = fd_rep["available_at"].max() if len(fd_rep) else pd.NaT
    f["audit_fd_d1_src_id"] = int(d1["src_id"].iloc[-1]) if len(d1) else -1
    return f


MAIN_BOATS = {"New Seaforth": "ns", "Premier": "pr", "Dolphin": "dl", "Daily Double": "dd"}
SURFACE = ("bonito", "barracuda", "mackerel", "yt", "white_seabass")
BOTTOM = ("rockfish", "whitefish", "sheephead")


def _fleet_features(D: pd.Timestamp, trips: pd.DataFrame, fd: np.ndarray, cls: np.ndarray, yt: np.ndarray,
                    is_hd: np.ndarray, win) -> dict:
    """Boat-level state, sailing proxies, species mix and other-fleet trend (D-B02).
    Reads only the visible prefix passed in by build()."""
    f: dict = {}
    boats = trips["boat"].to_numpy()
    w1, w2, w3 = win(1), win(2, 2), win(3)
    d1 = w1 & is_hd
    # Boat state: for each boat with a visible half-day trip in D-3..D-1, did its most
    # recent visible trip have yellowtail? Did it (any trip) have yt in D-3..D-1? Did it sail D-1?
    hd3 = w3 & is_hd
    sub = pd.DataFrame({"boat": boats[hd3], "fd": fd[hd3], "yt": yt[hd3]})
    hot_last = hot_any = hot_sailed = 0
    last_state: dict = {}
    if len(sub):
        g = sub.groupby(["boat", "fd"])["yt"].sum().reset_index().sort_values("fd")
        last = g.groupby("boat").tail(1).set_index("boat")
        anyyt = g.groupby("boat")["yt"].sum() > 0
        sailed_d1 = set(boats[d1])
        hot_last = int((last["yt"] > 0).sum())
        hot_any = int(anyyt.sum())
        hot_sailed = int(sum(1 for b, v in anyyt.items() if v and b in sailed_d1))
        last_state = (last["yt"] > 0).to_dict()
    f["bt_hot_last"] = hot_last          # boats whose latest visible trip (<=3d) had yt
    f["bt_hot_any3"] = hot_any           # boats with yt on any trip D-3..D-1
    f["bt_hot_sailed_d1"] = hot_sailed   # ... of those, boats that also reported a trip on D-1
    for b, k in MAIN_BOATS.items():
        f[f"bt_{k}_yt_last"] = int(bool(last_state.get(b, False)))
        f[f"bt_{k}_sailed_d1"] = int(b in set(boats[d1]))
    f["bt_yt_boats_d1"] = len(set(boats[d1 & (yt > 0)]))
    f["bt_boats_d1"] = len(set(boats[d1]))
    f["hd_yt_trips_d1"] = int((d1 & (yt > 0)).sum())
    f["hd_yt_tw_d2"] = int((w2 & (cls == "hd_twilight") & (yt > 0)).any())
    # Sailing proxy for D: half-day trips on the same weekday over the previous 4 weeks.
    n_same = []
    for k in (7, 14, 21, 28):
        n_same.append(int((win(k, k) & is_hd).sum()))
    f["hd_trips_dow_4w"] = float(np.mean(n_same))
    # D-1 species mix (per trip, D-1 AM/PM only).
    n1 = int(d1.sum())
    for sp in ("bonito", "barracuda", "calico", "mackerel", "sand_bass", "halibut", "white_seabass", "rockfish"):
        v = trips[sp].to_numpy()
        f[f"d1_{sp}_per_trip"] = float(v[d1].sum()) / n1 if n1 else 0.0
    surf = sum(trips[sp].to_numpy() if sp != "yt" else yt for sp in SURFACE)
    bott = sum(trips[sp].to_numpy() for sp in BOTTOM)
    f["d1_surface_frac"] = float((surf[d1] > 0).mean()) if n1 else 0.0
    f["d1_bottom_only_frac"] = float(((bott[d1] > 0) & (surf[d1] == 0) & (trips["calico"].to_numpy()[d1] == 0)).mean()) if n1 else 0.0
    w7 = win(7)
    n7 = int((w7 & is_hd).sum())
    f["hd_surface_frac_7"] = float((surf[w7 & is_hd] > 0).mean()) if n7 else 0.0
    # Other fleet (3/4-day, overnight) yellowtail by fished date, and trend.
    tq = cls == "three_quarter"
    ov = np.isin(cls, ("overnight",))
    f["tq_log_yt_d1"] = math.log1p(float(yt[w1 & tq].sum()))
    f["tq_yt_trip_frac_3"] = float((yt[w3 & tq] > 0).mean()) if (w3 & tq).any() else 0.0
    f["ov_log_yt_3"] = math.log1p(float(yt[w3 & ov].sum()))
    for k in (7, 30):
        m = win(k) & tq
        f[f"tq_yt_trip_frac_{k}"] = float((yt[m] > 0).mean()) if m.any() else 0.0
    w60 = win(60) & is_hd
    cov60 = len(np.unique(fd[w60]))
    f["hd_ytrate_60"] = len(np.unique(fd[w60 & (yt > 0)])) / cov60 if cov60 else 0.0
    f["tq_log_yt_trend"] = math.log1p(float(yt[w3 & tq].sum())) - math.log1p(float(yt[win(7, 4) & tq].sum()))
    # Exponentially weighted half-day yt-day indicator (half-life 2 days) over D-14..D-1.
    ytdays = set(pd.DatetimeIndex(fd[is_hd & (yt > 0)]).normalize())
    covdays = set(pd.DatetimeIndex(fd[is_hd]).normalize())
    num = den = 0.0
    for k in range(1, 15):
        d = D - pd.Timedelta(days=k)
        if d in covdays:
            wgt = 0.5 ** ((k - 1) / 2)
            num += wgt * (d in ytdays); den += wgt
    f["hd_yt_ewm"] = num / den if den else 0.0
    return f


def _env_features(D: pd.Timestamp, fd_rep: pd.DataFrame) -> dict:
    """Water temperature and local bait stated in FishDope reports visible at the cutoff (D-C01)."""
    f: dict = {}
    rd = fd_rep["report_date"]
    def rep(k, start=1):
        return fd_rep[(rd >= D - pd.Timedelta(days=k)) & (rd <= D - pd.Timedelta(days=start))]
    mean = lambda s: float(s.mean()) if s.notna().any() else float("nan")
    r3, r7, r8_21 = rep(3), rep(7), rep(21, 8)
    f["wt_all_3"], f["wt_all_7"] = mean(r3["wt_all"]), mean(r7["wt_all"])
    f["wt_local_7"], f["wt_local_14"] = mean(r7["wt_local"]), mean(rep(14)["wt_local"])
    f["wt_trend"] = f["wt_all_7"] - mean(r8_21["wt_all"])
    f["wt_max_7"] = float(r7["wt_all"].max()) if r7["wt_all"].notna().any() else float("nan")
    f["wt_n_7"] = int(r7["wt_all_n"].sum())
    # Anomaly vs the same +-15 day-of-year window in PRIOR years' visible reports.
    prior = fd_rep[rd < pd.Timestamp(D.year, 1, 1)]
    if len(prior):
        d = np.abs(prior["report_date"].dt.dayofyear.to_numpy() - D.dayofyear)
        clim = mean(prior["wt_all"][np.minimum(d, 365 - d) <= 15])
    else:
        clim = float("nan")
    f["wt_anom_7"] = f["wt_all_7"] - clim
    # Dense version: mean of the latest (up to 5) reports stating a temperature in D-21..D-1,
    # centred on 63 F (typical SD surface temp); 0 = unknown/typical. Local variant likewise.
    r21 = rep(21)
    for src, name in (("wt_all", "wt_c"), ("wt_local", "wt_c_local")):
        v = r21[src].dropna().tail(5)
        f[name] = float(v.mean()) - WT_CENTER if len(v) else 0.0
    for b in ("sardine", "squid", "anchovy", "mackerel"):
        f[f"bait_{b}_7"] = int((r7.groupby("report_date")[f"bait_local_{b}"].max() > 0).sum()) if len(r7) else 0
    return f


def _mf_features(D: pd.Timestamp, mf: pd.DataFrame) -> dict:
    """Latest NWS coastal-waters daytime forecast for D issued at or before the cutoff (D-C02)."""
    cand = mf[mf["target_date"] == D]
    cols = ("mf_wind_max", "mf_gust", "mf_seas", "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west")
    if len(cand):
        r = cand.iloc[-1]
        f = {c: float(r[c]) if r[c] is not None else float("nan") for c in cols}
        f["audit_mf_src_id"], f["audit_mf_available_at"] = int(r["src_id"]), r["available_at"]
    else:
        f = {c: float("nan") for c in cols}
        f["audit_mf_src_id"], f["audit_mf_available_at"] = -1, pd.NaT
    return f


LAT_L = 60  # days of history the latent-state filter reads (D-F01)
LAT_OBS = ("nhd", "khd", "ntq", "ktq", "fdv", "fdc", "fdn")
LAT_COLS = [f"lat_{o}_{k}" for o in LAT_OBS for k in range(1, LAT_L + 1)] + ["lat_doy"]


def _latent_obs(D: pd.Timestamp, trips: pd.DataFrame, fd_rep: pd.DataFrame | None) -> dict:
    """Per-day evidence for the latent-state filter (D-F01), lag k = 1..LAT_L days before D, as
    visible at the cutoff: half-day fishing trips and trips with yt (nhd/khd), 3/4-day trips and
    trips with yt (ntq/ktq), and whether a FishDope report for that date is visible (fdv), has a
    local yt catch sentence (fdc) or a local yt negation (fdn). Reads only the visible prefix."""
    f: dict = {"lat_doy": D.dayofyear}
    lag = ((np.datetime64(D) - trips["fished_date"].to_numpy()) / np.timedelta64(1, "D")).astype(int)
    cls = trips["cls"].to_numpy()
    yt = trips["yt"].to_numpy() > 0
    ok = (lag >= 1) & (lag <= LAT_L)
    cnt = lambda m: np.bincount(lag[ok & m], minlength=LAT_L + 1)
    hd, tq = np.isin(cls, HD_FISH_CLASSES), cls == "three_quarter"
    obs = {"nhd": cnt(hd), "khd": cnt(hd & yt), "ntq": cnt(tq), "ktq": cnt(tq & yt)}
    if fd_rep is not None and len(fd_rep):
        rl = ((np.datetime64(D) - fd_rep["report_date"].to_numpy()) / np.timedelta64(1, "D")).astype(int)
        rok = (rl >= 1) & (rl <= LAT_L)
        mx = lambda v: np.bincount(rl[rok & v], minlength=LAT_L + 1).clip(max=1)
        obs["fdv"] = mx(np.ones(len(rl), bool))
        obs["fdc"] = mx(fd_rep["yt_local_catch"].to_numpy() > 0)
        obs["fdn"] = mx(fd_rep["yt_local_neg"].to_numpy() > 0)
    else:
        obs.update({o: np.zeros(LAT_L + 1, int) for o in ("fdv", "fdc", "fdn")})
    for o in LAT_OBS:
        for k in range(1, LAT_L + 1):
            f[f"lat_{o}_{k}"] = int(obs[o][k])
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

    f.update(_fleet_features(D, trips, fd, cls, yt, is_hd, win))

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
          fd_rep: pd.DataFrame | None = None, mf: pd.DataFrame | None = None) -> pd.DataFrame:
    t_av = trips["available_at"].to_numpy()
    m_av = mf["available_at"].to_numpy() if mf is not None else None
    f_av = fc["available_at"].to_numpy()
    d_av = fd_rep["available_at"].to_numpy() if fd_rep is not None else None
    out = []
    for D in days:
        c = cutoff_for(D)
        vt = _visible(trips, t_av, c)
        vf = _visible(fc, f_av, c)
        row = _day_features(D, vt, vf)
        vd = _visible(fd_rep, d_av, c) if fd_rep is not None else None
        row.update(_latent_obs(D, vt, vd))
        if fd_rep is not None:
            row.update(_fd_features(D, vd))
            row.update(_env_features(D, vd))
            assert pd.isna(row["audit_fd_max_available_at"]) or row["audit_fd_max_available_at"] <= c
        if mf is not None:
            row.update(_mf_features(D, _visible(mf, m_av, c)))
            assert pd.isna(row["audit_mf_available_at"]) or row["audit_mf_available_at"] <= c
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
    "fd_local_catch_d1", "fd_local_sight_d1", "fd_local_neg_d1", "fd_coronado_catch_d1", "fd_coronado_sight_d1",
    "fd_coronado_neg_d1", "fd_north_catch_d1", "fd_north_sight_d1", "fd_north_neg_d1",
    "fd_local_catch_3", "fd_local_catchdays_3", "fd_local_sight_3", "fd_coronado_catch_3",
    # D-B02 fleet / boat-level / species-mix features
    "bt_hot_last", "bt_hot_any3", "bt_hot_sailed_d1",
    "bt_ns_yt_last", "bt_ns_sailed_d1", "bt_pr_yt_last", "bt_pr_sailed_d1",
    "bt_dl_yt_last", "bt_dl_sailed_d1", "bt_dd_yt_last", "bt_dd_sailed_d1",
    "bt_yt_boats_d1", "bt_boats_d1", "hd_yt_trips_d1", "hd_yt_tw_d2", "hd_trips_dow_4w",
    "d1_bonito_per_trip", "d1_barracuda_per_trip", "d1_calico_per_trip", "d1_mackerel_per_trip",
    "d1_sand_bass_per_trip", "d1_halibut_per_trip", "d1_white_seabass_per_trip", "d1_rockfish_per_trip",
    "d1_surface_frac", "d1_bottom_only_frac", "hd_surface_frac_7",
    "tq_log_yt_d1", "tq_yt_trip_frac_3", "ov_log_yt_3", "tq_log_yt_trend", "hd_yt_ewm",
    "tq_yt_trip_frac_7", "tq_yt_trip_frac_30", "hd_ytrate_60",


    # D-C01 / D-C02: environment
    "wt_all_3", "wt_all_7", "wt_local_7", "wt_local_14", "wt_trend", "wt_max_7", "wt_n_7", "wt_anom_7", "wt_c", "wt_c_local",
    "bait_sardine_7", "bait_squid_7", "bait_anchovy_7", "bait_mackerel_7",
    "mf_wind_max", "mf_gust", "mf_seas", "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west",
]
