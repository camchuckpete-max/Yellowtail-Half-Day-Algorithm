# Goal D sweep 8 (D-047): KSAN METAR (hourly airport wind / pressure / humidity / visibility), 2010+.
# Predictive (hc_, up to D-1 21:00) and explanatory (ex_, during the trip window) tracks, folds 2012-2023.
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
SAN = ["hc_san_wspd_24h", "hc_san_onshore_24h", "hc_san_wspd_prevpm", "hc_san_mslp_24h", "hc_san_mslp_chg24",
       "hc_san_relh_24h", "hc_san_vsby_24h"]
EXS = ["ex_san_wspd_trip", "ex_san_onshore_trip", "ex_san_wspd_max_trip", "ex_san_vsby_trip"]
YEARS = range(2012, 2024)
runs = [("D5 base", BASE, "P"), ("base+san_wind", BASE + SAN[:3], "P"), ("base+san_press", BASE + SAN[3:5], "P"),
        ("base+san_all", BASE + SAN, "P"), ("E: base+ex_san", BASE + EXS, "E"), ("E: base+san+ex_san", BASE + SAN + EXS, "E")]
print(f"# Goal D configurations scored on dev: {len(runs)}; source {man['source_commit'][:7]}; folds 2012-2023")
dev = df[df.date.dt.year.between(2012, 2023)].copy()
print("coverage:", {c: round(float(dev[c].notna().mean()), 2) for c in SAN + EXS})
for k, fs, tr in runs:
    s = trips.summary(trips.walk_forward(df, fs, YEARS, C=0.1, track=tr))
    print(f"{k:20s} [{tr}] AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
# Descriptive: warm-water trips (pier >= 68F), hit rate by in-trip KSAN wind tercile and AM/PM
w = dev[(dev["hc_Fc"] >= 2) & dev["ex_san_wspd_trip"].notna() & (dev["trip_twilight"] == 0)].copy()
w["wind_t"] = pd.qcut(w["ex_san_wspd_trip"], 3)
w["slot"] = w["trip_pm"].map({1: "PM", 0: "AM"})
print("\nwarm-water (pier >= 68F) AM/PM trips: hit rate by in-trip KSAN wind (kt) tercile")
print(w.groupby(["slot", "wind_t"], observed=True)["y"].agg(["mean", "size"]).round(3).to_string())
w["press_t"] = pd.qcut(w["hc_san_mslp_chg24"], 3)
print("\nsame trips: hit rate by 24h pressure change (mb) tercile")
print(w.groupby("press_t", observed=True)["y"].agg(["mean", "size"]).round(3).to_string())
