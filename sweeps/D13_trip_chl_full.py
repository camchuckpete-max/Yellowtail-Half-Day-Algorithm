# Goal D sweep 13 (D-052): chlorophyll on the complete series (SNPP SQ 2012-2021-08, NOAA-20 NRT after), owner's
# 1-day lag (D-048). Tiles + kelp boxes. All models trained/scored on trips with SD-coast chl visible, folds 2013-2023.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
df["hc_n20"] = (df["date"] >= "2021-08-27").astype(int)   # sensor switch indicator (SNPP SQ -> NOAA-20 NRT)
d = df[df["hc_chl_sd_3d"].notna()].copy()
YEARS = list(range(2013, 2024))
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
SD = ["hc_chl_sd_3d", "hc_chl_sd_anom30"]; LJ = ["hc_chl_lj_3d", "hc_chl_lj_anom30"]
ALL = SD + LJ + ["hc_chl_nc_3d", "hc_chl_nc_anom30", "hc_chl_bf_3d", "hc_chl_bf_anom30", "hc_chl_pl_3d", "hc_chl_pl_anom30"]
runs = [("D5 base", BASE), ("base+chl SD", BASE + SD + ["hc_n20"]), ("base+chl LJ kelp", BASE + LJ + ["hc_n20"]),
        ("base+chl all", BASE + ALL + ["hc_n20"]), ("base+chl anomalies only", BASE + [c for c in ALL if "anom" in c])]
sc = d[d.date.dt.year.isin(YEARS)]
print(f"# Goal D configurations scored on dev: {len(runs)}; source {man['source_commit'][:7]}; folds 2013-2023; "
      f"scored trips {len(sc)} (rate {sc.y.mean():.3f})")
print("coverage in scored trips:", {c: round(float(sc[c].notna().mean()), 2) for c in SD + LJ})
for k, fs in runs:
    s = trips.summary(trips.walk_forward(d, fs, YEARS, C=0.1, train_start="2012-01-01"))
    print(f"{k:24s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
dv = d[d.date.dt.year.between(2012, 2023) & (d.trip_twilight == 0)].copy()
dv["Fband"] = pd.cut(dv["hc_Fc"] + 66, [0, 64, 68, 72, 99], labels=["<64", "64-68", "68-72", ">=72"])
for col, lab in (("hc_chl_sd_3d", "SD coast"), ("hc_chl_lj_3d", "La Jolla kelp box"), ("hc_chl_sd_anom30", "SD coast 3d minus 30d")):
    x = dv.dropna(subset=[col]).copy()
    x["t"] = x.groupby("Fband", observed=True)[col].transform(lambda s: pd.qcut(s, 3, labels=["low", "mid", "high"]))
    print(f"\nday trips 2012-2023: hit rate by pier band x {lab} tercile (terciles within band)")
    print(x.groupby(["Fband", "t"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("t").to_string())
