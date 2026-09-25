# Goal D sweep 13b (D-052): is the low-chlorophyll effect a year fingerprint? (a) terciles computed within
# year x pier band; (b) 2012-2019 vs 2020-2023 (sensor switch 2021-08 falls in the second period);
# (c) per-year low-vs-high contrast for warm water (pier >= 68F).
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips
df, man = trips.build()
df["pier_F"] = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
d = df[df.date.dt.year.between(2012, 2023) & (df.trip_twilight == 0) & df["hc_chl_sd_3d"].notna() & df["pier_F"].notna()].copy()
d["Fband"] = pd.cut(d["pier_F"], [0, 64, 68, 72, 99], labels=["<64", "64-68", "68-72", ">=72"])
d["yr"] = d.date.dt.year
print(f"# descriptive only; source {man['source_commit'][:7]}; day trips {len(d)}")
def terc(s):
    return pd.qcut(s.rank(method="first"), 3, labels=["low", "mid", "high"]) if len(s) >= 9 else pd.Series(np.nan, index=s.index)
d["t_yb"] = d.groupby(["yr", "Fband"], observed=True)["hc_chl_sd_3d"].transform(terc)
print("\n(a) SD-coast chl terciles WITHIN year x pier band (removes between-year differences):")
print(d.groupby(["Fband", "t_yb"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("t_yb").to_string())
d["t_b"] = d.groupby("Fband", observed=True)["hc_chl_sd_3d"].transform(terc)
for lab, yrs in (("2012-2019", (2012, 2019)), ("2020-2023", (2020, 2023))):
    w = d[d.yr.between(*yrs)].copy()
    w["t"] = w.groupby("Fband", observed=True)["hc_chl_sd_3d"].transform(terc)
    print(f"\n(b) {lab}: terciles within pier band (this period only)")
    print(w.groupby(["Fband", "t"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("t").to_string())
warm = d[d["pier_F"] >= 68].copy()
warm["t"] = warm.groupby("yr")["hc_chl_sd_3d"].transform(terc)
print("\n(c) pier >= 68F day trips, per year: hit rate low / high chl tercile (within year), trips")
g = warm.groupby(["yr", "t"], observed=True)["y"].agg(["mean", "size"]).unstack("t")
print(g.round(2).to_string())
print("chl edges (mg/m3, all dev):", [round(float(np.exp(x)), 2) for x in np.quantile(d["hc_chl_sd_3d"], [1/3, 2/3])])
# (d) Year level: Jul-Oct mean log chl (SD coast, as visible at trip time) vs that year's warm-water hit rate.
yl = d[d.date.dt.month.between(7, 10)].groupby("yr").agg(chl=("hc_chl_sd_3d", "mean"), pier=("pier_F", "mean"))
yl["warm_rate"] = d[d.date.dt.month.between(7, 10) & (d.pier_F >= 68)].groupby("yr")["y"].mean()
yl["all_rate"] = d[d.date.dt.month.between(7, 10)].groupby("yr")["y"].mean()
yl["chl_mg"] = np.exp(yl["chl"])
print("\n(d) Jul-Oct by year: mean chl (mg/m3), mean pier F, hit rate (all day trips, pier>=68F)")
print(yl[["chl_mg", "pier", "all_rate", "warm_rate"]].round(2).to_string())
for lab, s in (("all years", yl), ("2012-2021 (one sensor, SNPP)", yl.loc[2012:2020])):
    print(f"Spearman chl vs warm_rate, {lab}: {s['chl'].corr(s['warm_rate'], method='spearman'):.2f}; "
          f"chl vs all_rate: {s['chl'].corr(s['all_rate'], method='spearman'):.2f}; pier vs all_rate: {s['pier'].corr(s['all_rate'], method='spearman'):.2f}")
