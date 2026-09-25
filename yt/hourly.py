"""Goal D trip-window conditions from hourly/sub-daily source tables (D-041).

Two strictly separated feature families:
  hc_*  PREDICTIVE — only information public at the 21:00 PT D-1 cutoff (observations
        time-stamped at or before the cutoff; tide *predictions*, published years ahead;
        daily indices with their documented publication lag).
  ex_*  EXPLANATORY — conditions observed during the trip window itself. Never used for
        forecast skill; reported separately.
No catch data and no FishDope-derived data enter either family.
"""
from __future__ import annotations

import sqlite3
from datetime import timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

PT = ZoneInfo("America/Los_Angeles")
UTC = ZoneInfo("UTC")
BUOYS = ("46225", "46232", "46254", "46266", "LJPC1")
UPWELLING_LAG_DAYS = 14   # Muse: ~13-day publication lag observed; rounded up
GLIDER_LAG_DAYS = 3       # D-045: daily glider means treated as public 3 days after the described day
KELP_LAG_DAYS = 365      # D-045/D-046: no documented Kelpwatch release lag; PIT-safe bound after quarter end
CHL_LAG_DAYS = 1          # D-048 (owner's decision): chlorophyll for day D-1 is usable at the D-1 21:00 cutoff
CHL_SOURCES = ("noaacwNPPVIIRSSQchlaDaily", "noaacwN20VIIRSchlaDaily")
CHL_ZONES = {"t_sd_coast": "sd", "t_north_county": "nc", "t_43_butterfly": "bf", "la_jolla": "lj", "point_loma_kelp": "pl"}  # kelp boxes: D-052
SAT_SST_LAG_DAYS = 2      # D-049: same rule as Goal C SST (events.OCEAN_LAG_DAYS, D-034)
SAT_SST_ZONES = {"la_jolla": "lj", "point_loma_kelp": "pl", "t_sd_coast": "sd", "t_north_county": "nc"}
SLA_LAG_DAYS = 2          # D-045: blended SSH daily product, same latency convention as SST
# Trip windows (PT). New Seaforth times per Muse's 0002 notes; Sea Watch AM/PM UNCONFIRMED (same slots assumed).
WINDOWS = {"hd_am": ("06:00", "11:30"), "hd_pm": ("12:30", "17:30"), "hd_unspecified": ("12:30", "17:30"),
           "hd_twilight": ("18:00", "22:30")}


def _pt(ts_utc: pd.Series) -> pd.Series:
    """Naive UTC strings -> naive local PT timestamps."""
    t = pd.to_datetime(ts_utc).dt.tz_localize(UTC).dt.tz_convert(PT).dt.tz_localize(None)
    return t


def load(db: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    tides = pd.read_sql("SELECT ts_utc, height_ft FROM coops_tide_predictions WHERE station_id='9410230' "
                        "AND kind='prediction'", db)
    tides["ts"] = _pt(tides["ts_utc"])
    out["tides"] = tides.drop(columns="ts_utc").sort_values("ts").reset_index(drop=True)
    pier = pd.read_sql("SELECT ts_utc, wtmp_c, atmp_c FROM shore_station_temps WHERE station_id='9410230'", db)
    pier["ts"] = _pt(pier["ts_utc"])
    out["pier"] = pier.drop(columns="ts_utc").sort_values("ts").reset_index(drop=True)
    q = f"""SELECT station_id, ts_utc, wtmp_c, wspd_ms, wdir_deg, gst_ms, wvht_m, dpd_s
            FROM buoy_observations WHERE station_id IN ({",".join("?" * len(BUOYS))})"""
    b = pd.read_sql(q, db, params=BUOYS)
    b["ts"] = _pt(b["ts_utc"])
    out["buoy"] = {s: g.drop(columns=["ts_utc", "station_id"]).sort_values("ts").reset_index(drop=True)
                   for s, g in b.groupby("station_id")}
    up = pd.read_sql("SELECT obs_date, location, cuti, beuti FROM upwelling_daily", db)
    up["date"] = pd.to_datetime(up["obs_date"])
    up["available_at"] = up["date"] + pd.Timedelta(days=UPWELLING_LAG_DAYS)
    out["upw"] = up.drop(columns="obs_date").sort_values("available_at").reset_index(drop=True)
    ci = pd.read_sql("SELECT index_id, month, value, release_lag_days FROM climate_indices", db)
    month_end = pd.to_datetime(ci["month"] + "-01") + pd.offsets.MonthEnd(0)
    ci["available_at"] = month_end + pd.to_timedelta(ci["release_lag_days"].fillna(45), unit="D")
    out["climate"] = ci.sort_values("available_at").reset_index(drop=True)
    g = pd.read_sql("SELECT obs_date, depth_m, temp_c FROM subsurface_temp_daily WHERE temp_c IS NOT NULL", db)
    g["date"] = pd.to_datetime(g["obs_date"])
    g["available_at"] = g["date"] + pd.Timedelta(days=GLIDER_LAG_DAYS)
    out["glider"] = g.drop(columns="obs_date").sort_values("available_at").reset_index(drop=True)
    s = pd.read_sql("SELECT condition_date, sla_m FROM sea_level_anomaly WHERE zone_id='la_jolla'", db)
    s["date"] = pd.to_datetime(s["condition_date"])
    s["available_at"] = s["date"] + pd.Timedelta(days=SLA_LAG_DAYS)
    out["sla"] = s.drop(columns=["condition_date"]).sort_values("available_at").reset_index(drop=True)
    k = pd.read_sql("SELECT quarter_start, quarter, sub_zone_id, kelp_area_ha FROM kelp_canopy_quarterly", db)
    k["qstart"] = pd.to_datetime(k["quarter_start"])
    k["available_at"] = k["qstart"] + pd.offsets.QuarterEnd(0) + pd.Timedelta(days=KELP_LAG_DAYS)
    out["kelp"] = k.drop(columns="quarter_start").sort_values("available_at").reset_index(drop=True)
    m = pd.read_sql("SELECT ts_utc, drct, sknt, mslp, relh, vsby_sm FROM metar_obs WHERE station_id='SAN'", db)
    m["ts"] = _pt(m["ts_utc"])  # METAR is public at observation time
    rad = np.deg2rad(m["drct"] - 270.0)
    m["onshore"] = m["sknt"] * np.cos(rad)  # + = from the west (onshore at La Jolla)
    out["metar"] = m.drop(columns="ts_utc").sort_values("ts").reset_index(drop=True)
    c = pd.read_sql(f"""SELECT condition_date, zone_id, chl FROM conditions_daily WHERE chl > 0
                        AND source IN ({",".join("?" * len(CHL_SOURCES))})""", db, params=CHL_SOURCES)
    c["date"] = pd.to_datetime(c["condition_date"])
    c["logchl"] = np.log(c["chl"])
    out["chl"] = c.drop(columns=["condition_date", "chl"]).sort_values("date").reset_index(drop=True)
    t = pd.read_sql(f"""SELECT condition_date, zone_id, sst_f FROM conditions_daily WHERE sst_f IS NOT NULL
                        AND source='noaacwBLENDEDsstDaily' AND zone_id IN ({",".join("?" * len(SAT_SST_ZONES))})""",
                    db, params=tuple(SAT_SST_ZONES))
    t["date"] = pd.to_datetime(t["condition_date"])
    t["available_at"] = t["date"] + pd.Timedelta(days=SAT_SST_LAG_DAYS - 1, hours=20)
    out["satsst"] = t.drop(columns="condition_date").sort_values("available_at").reset_index(drop=True)
    return out


def _slice(df: pd.DataFrame, lo: pd.Timestamp, hi: pd.Timestamp, col: str = "ts") -> pd.DataFrame:
    t = df[col].to_numpy()
    i, j = np.searchsorted(t, np.datetime64(lo), "left"), np.searchsorted(t, np.datetime64(hi), "right")
    return df.iloc[i:j]


def _mean(s: pd.Series) -> float:
    s = s.dropna()
    return float(s.mean()) if len(s) else float("nan")


def trip_features(date: pd.Timestamp, cls: str, data: dict, cutoff: pd.Timestamp) -> dict:
    f: dict = {}
    a, b = WINDOWS[cls]
    w0 = date + pd.Timedelta(a + ":00")
    w1 = date + pd.Timedelta(b + ":00")
    nan = float("nan")
    # --- tide predictions over the trip window (predictions are public ahead of time)
    tw = _slice(data["tides"], w0 - pd.Timedelta(hours=1), w1 + pd.Timedelta(hours=1))
    if len(tw) >= 3:
        h = tw["height_ft"].to_numpy()
        f["hc_tide_start"], f["hc_tide_change"] = float(h[0]), float(h[-1] - h[0])
        f["hc_tide_range"] = float(h.max() - h.min())
        f["hc_tide_maxrate"] = float(np.abs(np.diff(h)).max())
        f["hc_tide_turns"] = int(((np.diff(np.sign(np.diff(h))) != 0)).sum())
    else:
        f.update(hc_tide_start=nan, hc_tide_change=nan, hc_tide_range=nan, hc_tide_maxrate=nan, hc_tide_turns=nan)
    # --- pier (CO-OPS 9410230) water temperature up to the cutoff
    pv = _slice(data["pier"], cutoff - pd.Timedelta(days=10), cutoff)
    last24 = pv[pv["ts"] > cutoff - pd.Timedelta(hours=24)]
    prev = pv[(pv["ts"] > cutoff - pd.Timedelta(hours=96)) & (pv["ts"] <= cutoff - pd.Timedelta(hours=72))]
    f["hc_pier_wtmp_24h"] = _mean(last24["wtmp_c"])
    f["hc_pier_wtmp_chg3d"] = f["hc_pier_wtmp_24h"] - _mean(prev["wtmp_c"])
    f["hc_pier_wtmp_7d"] = _mean(pv[pv["ts"] > cutoff - pd.Timedelta(days=7)]["wtmp_c"])
    f["hc_pier_air_minus_water_24h"] = _mean(last24["atmp_c"]) - f["hc_pier_wtmp_24h"]
    # --- buoys up to the cutoff
    for st, name in (("46225", "tp"), ("46232", "pl"), ("46254", "sn")):
        g = data["buoy"].get(st)
        if g is None:
            f[f"hc_b{name}_wtmp_24h"] = f[f"hc_b{name}_wvht_24h"] = nan
            continue
        g24 = _slice(g, cutoff - pd.Timedelta(hours=24), cutoff)
        f[f"hc_b{name}_wtmp_24h"] = _mean(g24["wtmp_c"])
        f[f"hc_b{name}_wvht_24h"] = _mean(g24["wvht_m"])
    g = data["buoy"].get("46225")
    f["hc_btp_dpd_24h"] = _mean(_slice(g, cutoff - pd.Timedelta(hours=24), cutoff)["dpd_s"]) if g is not None else nan
    lj = data["buoy"].get("LJPC1")
    f["hc_ljpc1_wspd_24h"] = _mean(_slice(lj, cutoff - pd.Timedelta(hours=24), cutoff)["wspd_ms"]) if lj is not None else nan
    # --- upwelling index (public ~14 days after the described day)
    up = data["upw"]
    upv = up[(up["available_at"] <= cutoff) & (up["available_at"] > cutoff - pd.Timedelta(days=60))]
    u33 = upv[upv["location"] == "L33N"].sort_values("date")
    f["hc_cuti33_7"] = _mean(u33["cuti"].tail(7))
    f["hc_cuti33_30"] = _mean(u33["cuti"].tail(30))
    f["hc_beuti33_30"] = _mean(u33["beuti"].tail(30))
    # --- climate indices: latest month already published at the cutoff
    ci = data["climate"]
    civ = ci[(ci["available_at"] <= cutoff) & ci["value"].notna()]
    for idx in ("oni", "pdo", "npgo", "mei_v2"):
        s = civ[civ["index_id"] == idx]
        f[f"hc_ci_{idx}"] = float(s.sort_values("month")["value"].iloc[-1]) if len(s) else nan
    # --- glider temperature at depth (2014+) and sea-level anomaly (2015+), D-045
    gv = data["glider"]
    gv = gv[(gv["available_at"] <= cutoff) & (gv["date"] > cutoff - pd.Timedelta(days=10 + GLIDER_LAG_DAYS))]
    t5, t45 = _mean(gv[gv["depth_m"] == 5]["temp_c"]), _mean(gv[gv["depth_m"] == 45]["temp_c"])
    f["hc_glider_t5_10d"], f["hc_glider_t45_10d"], f["hc_glider_strat_10d"] = t5, t45, t5 - t45
    sv = data["sla"]
    sv = sv[(sv["available_at"] <= cutoff) & (sv["date"] > cutoff - pd.Timedelta(days=30))]
    f["hc_sla_lj_last"] = float(sv["sla_m"].iloc[-1]) if len(sv) and pd.notna(sv["sla_m"].iloc[-1]) else nan
    f["hc_sla_lj_7d"] = _mean(sv[sv["date"] > cutoff - pd.Timedelta(days=7 + SLA_LAG_DAYS)]["sla_m"])
    # --- kelp canopy (Landsat quarterly), usable only from quarter end + KELP_LAG_DAYS, D-046.
    # NULL = cloud-blocked quarter, skipped; anomaly = latest minus mean of earlier visible same-quarter values.
    kv = data["kelp"]
    kv = kv[(kv["available_at"] <= cutoff) & kv["kelp_area_ha"].notna()]
    for zone, name in (("la_jolla", "lj"), ("point_loma_kelp", "pl")):
        z = kv[kv["sub_zone_id"] == zone].sort_values("qstart")
        if len(z):
            last = z.iloc[-1]
            same = z[(z["quarter"] == last["quarter"]) & (z["qstart"] < last["qstart"])]["kelp_area_ha"]
            f[f"hc_kelp_{name}_last"] = float(last["kelp_area_ha"])
            f[f"hc_kelp_{name}_anom"] = float(last["kelp_area_ha"] - same.mean()) if len(same) >= 3 else nan
        else:
            f[f"hc_kelp_{name}_last"] = f[f"hc_kelp_{name}_anom"] = nan
    # --- KSAN METAR (hourly airport obs), D-047
    mv = _slice(data["metar"], cutoff - pd.Timedelta(hours=48), cutoff)
    m24 = mv[mv["ts"] > cutoff - pd.Timedelta(hours=24)]
    mpm = mv[(mv["ts"] >= cutoff.normalize() + pd.Timedelta(hours=12)) & (mv["ts"] <= cutoff.normalize() + pd.Timedelta(hours=17, minutes=30))]
    f["hc_san_wspd_24h"], f["hc_san_onshore_24h"] = _mean(m24["sknt"]), _mean(m24["onshore"])
    f["hc_san_wspd_prevpm"] = _mean(mpm["sknt"])
    f["hc_san_mslp_24h"] = _mean(m24["mslp"])
    f["hc_san_mslp_chg24"] = f["hc_san_mslp_24h"] - _mean(mv[mv["ts"] <= cutoff - pd.Timedelta(hours=24)]["mslp"])
    f["hc_san_relh_24h"], f["hc_san_vsby_24h"] = _mean(m24["relh"]), _mean(m24["vsby_sm"])
    # --- satellite chlorophyll (log mg/m3), D-048: day d usable from d + (CHL_LAG_DAYS - 1) days + 21:00
    cv = data["chl"]
    last_ok = (cutoff - pd.Timedelta(hours=21)).normalize() - pd.Timedelta(days=CHL_LAG_DAYS - 1)
    cv = cv[(cv["date"] <= last_ok) & (cv["date"] > last_ok - pd.Timedelta(days=120))]
    for zone, name in CHL_ZONES.items():
        z120 = cv[cv["zone_id"] == zone]
        if name in ("sd", "lj"):  # D-052: slow (season-scale) chlorophyll level
            f[f"hc_chl_{name}_60d"] = _mean(z120[z120["date"] > last_ok - pd.Timedelta(days=60)]["logchl"])
            f[f"hc_chl_{name}_120d"] = _mean(z120["logchl"])
        z = z120[z120["date"] > last_ok - pd.Timedelta(days=30)]
        z3 = z[z["date"] > last_ok - pd.Timedelta(days=3)]["logchl"]
        f[f"hc_chl_{name}_3d"] = _mean(z3)
        f[f"hc_chl_{name}_anom30"] = f[f"hc_chl_{name}_3d"] - _mean(z["logchl"])
    # --- satellite SST (blended, daily), D-049: latest visible day within 5 days, per box
    tv = data["satsst"]
    tv = tv[(tv["available_at"] <= cutoff) & (tv["available_at"] > cutoff - pd.Timedelta(days=5))]
    for zone, name in SAT_SST_ZONES.items():
        z = tv[tv["zone_id"] == zone].sort_values("date")
        f[f"hc_sat_{name}_f"] = float(z["sst_f"].iloc[-1]) if len(z) else nan
    # --- EXPLANATORY: observed during the trip window (never a forecast input)
    pw = _slice(data["pier"], w0, w1)
    f["ex_pier_wtmp_trip"] = _mean(pw["wtmp_c"])
    wind_src = [data["buoy"].get(s) for s in ("LJPC1", "46254", "46232")]
    ws = next((w for w in (_slice(g, w0, w1) for g in wind_src if g is not None) if w["wspd_ms"].notna().any()), None)
    f["ex_wind_trip_mean"] = _mean(ws["wspd_ms"]) if ws is not None else nan
    f["ex_wind_trip_max"] = float(ws["wspd_ms"].max()) if ws is not None and ws["wspd_ms"].notna().any() else nan
    tp = _slice(data["buoy"]["46225"], w0, w1) if "46225" in data["buoy"] else None
    f["ex_wvht_trip"] = _mean(tp["wvht_m"]) if tp is not None else nan
    f["ex_btp_wtmp_trip"] = _mean(tp["wtmp_c"]) if tp is not None else nan
    mw = _slice(data["metar"], w0, w1)
    f["ex_san_wspd_trip"], f["ex_san_onshore_trip"] = _mean(mw["sknt"]), _mean(mw["onshore"])
    f["ex_san_wspd_max_trip"] = float(mw["sknt"].max()) if mw["sknt"].notna().any() else nan
    f["ex_san_vsby_trip"] = _mean(mw["vsby_sm"])
    return f


def build(trips: pd.DataFrame, data: dict) -> pd.DataFrame:
    """trips: rows with 'date' (Timestamp) and 'cls'. Returns one feature row per input row."""
    rows = []
    for d, c in zip(trips["date"], trips["cls"]):
        cutoff = d - pd.Timedelta(days=1) + pd.Timedelta(hours=21)
        rows.append(trip_features(d, c, data, cutoff))
    return pd.DataFrame(rows, index=trips.index)


HC_FEATURES = ["hc_tide_start", "hc_tide_change", "hc_tide_range", "hc_tide_maxrate", "hc_tide_turns",
               "hc_pier_wtmp_24h", "hc_pier_wtmp_chg3d", "hc_pier_wtmp_7d", "hc_pier_air_minus_water_24h",
               "hc_btp_wtmp_24h", "hc_btp_wvht_24h", "hc_bpl_wtmp_24h", "hc_bpl_wvht_24h", "hc_bsn_wtmp_24h",
               "hc_bsn_wvht_24h", "hc_btp_dpd_24h", "hc_ljpc1_wspd_24h", "hc_cuti33_7", "hc_cuti33_30",
               "hc_beuti33_30", "hc_ci_oni", "hc_ci_pdo", "hc_ci_npgo", "hc_ci_mei_v2",
               "hc_glider_t5_10d", "hc_glider_t45_10d", "hc_glider_strat_10d", "hc_sla_lj_last", "hc_sla_lj_7d",
               "hc_kelp_lj_last", "hc_kelp_lj_anom", "hc_kelp_pl_last", "hc_kelp_pl_anom",
               "hc_san_wspd_24h", "hc_san_onshore_24h", "hc_san_wspd_prevpm", "hc_san_mslp_24h",
               "hc_san_mslp_chg24", "hc_san_relh_24h", "hc_san_vsby_24h",
               "hc_chl_sd_3d", "hc_chl_sd_anom30", "hc_chl_nc_3d", "hc_chl_nc_anom30", "hc_chl_bf_3d", "hc_chl_bf_anom30",
               "hc_chl_lj_3d", "hc_chl_lj_anom30", "hc_chl_pl_3d", "hc_chl_pl_anom30",
               "hc_chl_sd_60d", "hc_chl_sd_120d", "hc_chl_lj_60d", "hc_chl_lj_120d",
               "hc_sat_lj_f", "hc_sat_pl_f", "hc_sat_sd_f", "hc_sat_nc_f"]
EX_FEATURES = ["ex_pier_wtmp_trip", "ex_wind_trip_mean", "ex_wind_trip_max", "ex_wvht_trip", "ex_btp_wtmp_trip",
               "ex_san_wspd_trip", "ex_san_onshore_trip", "ex_san_wspd_max_trip", "ex_san_vsby_trip"]
