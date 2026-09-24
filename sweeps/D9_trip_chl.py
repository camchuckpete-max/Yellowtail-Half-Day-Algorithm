# Goal D sweep 9 (D-048): satellite chlorophyll with the owner's D-1 availability rule (CHL_LAG_DAYS=1),
# plus a lag-2 sensitivity run. Chlorophyll exists for 2012-2014Q1 and 2021+ only (backfill running), so
# all models here are trained and scored on trips with chlorophyll visible: folds 2013, 2021, 2022, 2023.
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import trips, hourly
CH = ["hc_chl_sd_3d", "hc_chl_sd_anom30", "hc_chl_nc_3d", "hc_chl_nc_anom30", "hc_chl_bf_3d", "hc_chl_bf_anom30"]
YEARS = [2013, 2021, 2022, 2023]
def prep(df):
    F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
    df["hc_Fc"] = F - 66.0
    for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
        df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
    return df[df["hc_chl_sd_3d"].notna()].copy()
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
SEASON = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2"]
runs = [("season only", SEASON), ("season+chl", SEASON + CH), ("D5 base", BASE), ("base+chl_sd", BASE + CH[:2]),
        ("base+chl_all", BASE + CH)]
print(f"# Goal D configurations scored on dev: {2 * len(runs)}; folds {YEARS}")
for lag in (1, 2):
    hourly.CHL_LAG_DAYS = lag
    df, man = trips.build()
    d = prep(df)
    print(f"\n## CHL_LAG_DAYS={lag}; source {man['source_commit'][:7]}; trips with chl: {len(d)} "
          f"({d[d.date.dt.year.isin(YEARS)].shape[0]} in scored folds, positive rate {d[d.date.dt.year.isin(YEARS)].y.mean():.3f})")
    for k, fs in runs:
        s = trips.summary(trips.walk_forward(d, fs, YEARS, C=0.1, train_start="2012-01-01"))
        print(f"{k:14s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
    if lag == 1:
        dv = d[d.date.dt.year.between(2012, 2023) & (d.trip_twilight == 0)].copy()
        dv["chl_t"] = pd.qcut(dv["hc_chl_sd_3d"], 3, labels=["low", "mid", "high"])
        dv["Fband"] = pd.cut(dv["hc_Fc"] + 66, [0, 64, 68, 99], labels=["<64", "64-68", ">=68"])
        print("\nday trips, dev: hit rate by pier-temp band x SD-coast chlorophyll tercile (D-1, 3-day log mean)")
        print(dv.groupby(["Fband", "chl_t"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("chl_t").to_string())
        import numpy as np
        print("tercile edges (mg/m3):", [round(float(np.exp(x)), 2) for x in pd.qcut(dv["hc_chl_sd_3d"], 3, retbins=True)[1]])
