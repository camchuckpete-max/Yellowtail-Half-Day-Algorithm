# Goal D sweep 15 (D-054): Kd490 water clarity (SNPP science quality, 2012 -> now), SD-coast tile and La Jolla
# kelp box. Default availability = observed ~10-day publication lag (KD_LAG_DAYS=10); a 1-day run is a
# sensitivity check only (the owner's 1-day rule, D-048, covers chlorophyll, not Kd490).
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips, hourly
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
YEARS = list(range(2013, 2024))
print(f"# Goal D configurations scored on dev: 8 (4 x 2 lags); folds 2013-2023")
for lag in (10, 1):
    hourly.KD_LAG_DAYS = lag
    df, man = trips.build()
    F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
    df["hc_Fc"] = F - 66.0
    for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
        df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
    d = df[df["hc_kd_sd_120d"].notna()].copy()
    tag = "DEFAULT" if lag == 10 else "SENSITIVITY ONLY"
    print(f"\n## KD_LAG_DAYS={lag} ({tag}); source {man['source_commit'][:7]}; scored trips {d[d.date.dt.year.isin(YEARS)].shape[0]}")
    for k, fs in (("D5 base", BASE), ("base+kd SD 3d", BASE + ["hc_kd_sd_3d"]), ("base+kd SD 120d", BASE + ["hc_kd_sd_120d"]),
                  ("base+kd SD+LJ 3d+120d", BASE + ["hc_kd_sd_3d", "hc_kd_sd_120d", "hc_kd_lj_3d", "hc_kd_lj_120d"])):
        s = trips.summary(trips.walk_forward(d, fs, YEARS, C=0.1, train_start="2012-01-01"))
        print(f"{k:24s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
    if lag == 10:
        dv = d[d.date.dt.year.between(2012, 2023) & (d.trip_twilight == 0)].copy()
        dv["pier_F"] = F; dv["yr"] = dv.date.dt.year
        dv["Fband"] = pd.cut(dv["pier_F"], [0, 64, 68, 72, 99], labels=["<64", "64-68", "68-72", ">=72"])
        x = dv.dropna(subset=["hc_kd_sd_3d"]).copy()
        x["t"] = x.groupby("Fband", observed=True)["hc_kd_sd_3d"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["clear", "mid", "murky"]))
        x["ty"] = x.groupby(["yr", "Fband"], observed=True)["hc_kd_sd_3d"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["clear", "mid", "murky"]) if len(s) >= 9 else pd.Series(np.nan, index=s.index))
        print("\nday trips 2012-2023, pooled terciles within pier band (Kd490 SD 3d):")
        print(x.groupby(["Fband", "t"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("t").to_string())
        print("\nsame, terciles within year x pier band:")
        print(x.groupby(["Fband", "ty"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("ty").to_string())
        yl = dv[dv.date.dt.month.between(7, 10)].groupby("yr").agg(kd=("hc_kd_sd_120d", "mean"), chl=("hc_chl_sd_120d", "mean"), rate=("y", "mean"))
        yl["warm_rate"] = dv[dv.date.dt.month.between(7, 10) & (dv.pier_F >= 68)].groupby("yr")["y"].mean()
        print("\nJul-Oct by year: mean Kd490 120d (m^-1), chl 120d (mg/m3), hit rate all / pier>=68F")
        print(pd.DataFrame({"kd": np.exp(yl.kd), "chl": np.exp(yl.chl), "all": yl.rate, "warm": yl.warm_rate}).round(3).to_string())
        print(f"Spearman kd vs warm_rate {yl.kd.corr(yl.warm_rate, method='spearman'):.2f}; kd vs all {yl.kd.corr(yl.rate, method='spearman'):.2f}; "
              f"kd vs chl {yl.kd.corr(yl.chl, method='spearman'):.2f}")
