# Goal D sweep 14 (D-053): Del Mar mooring temperature at 1 m / 15 m and their difference (stratification),
# 2010-2021-05. Folds 2012-2020, trips with a 1 m and 15 m value.
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
d = df[df["hc_moor_strat_3d"].notna() & df["hc_Fc"].notna()].copy()
YEARS = [y for y in range(2012, 2021) if (d.date.dt.year == y).sum() >= 150]
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
print(f"# Goal D configurations scored on dev: 3; source {man['source_commit'][:7]}; folds {YEARS}")
print("trips with mooring 1m+15m by year:", d.groupby(d.date.dt.year).size().to_dict())
print("corr pier F vs mooring 1 m:", round(float(d[["hc_Fc", "hc_moor_t1_3d"]].corr().iloc[0, 1]), 3))
for k, fs in (("D5 base", BASE), ("base+strat", BASE + ["hc_moor_strat_3d"]),
              ("base+t1+t15", BASE + ["hc_moor_t1_3d", "hc_moor_t15_3d"])):
    s = trips.summary(trips.walk_forward(d, fs, YEARS, C=0.1))
    print(f"{k:14s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
dv = d[d.date.dt.year.between(2012, 2020) & (d.trip_twilight == 0)].copy()
dv["Fband"] = pd.cut(dv["hc_Fc"] + 66, [0, 64, 68, 72, 99], labels=["<64", "64-68", "68-72", ">=72"])
dv["strat_t"] = dv.groupby("Fband", observed=True)["hc_moor_strat_3d"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["well mixed", "mid", "stratified"]))
print("\nday trips: hit rate by pier band x stratification tercile (1 m minus 15 m, within band)")
print(dv.groupby(["Fband", "strat_t"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("strat_t").to_string())
print("stratification (C) tercile medians:", dv.groupby("strat_t", observed=True)["hc_moor_strat_3d"].median().round(2).to_dict())
# Within-year check (warm water, pier >= 68F): terciles of stratification computed within each year
w = dv[dv["hc_Fc"] >= 2].copy()
w["yr"] = w.date.dt.year
w["t"] = w.groupby("yr")["hc_moor_strat_3d"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["mixed", "mid", "strat"]) if len(s) >= 15 else pd.Series(index=s.index, dtype=object))
print("\npier >= 68F day trips: hit rate by within-year stratification tercile")
print(w.groupby(["yr", "t"], observed=True)["y"].agg(["mean", "size"]).round(2).unstack("t").to_string())
w2 = w.dropna(subset=["t"])
print("pooled within-year terciles:", w2.groupby("t", observed=True)["y"].mean().round(3).to_dict())
