# Agent C diagnostic (no new model scored): do the environmental features explain the residual of the
# e007 base configuration's walk-forward dev predictions? Correlation of each feature with (y - p), overall
# and on days where B1 is wrong-prone (hd_yt_lastday == 0), plus positive rate by feature tercile.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import dataset, evaluate, experiments
df, _ = dataset.build(); df = evaluate.eligible(df)
p, _ = evaluate.run_spec(df, experiments.get("e007_recency_d1_fdsent_C003_p35"))
print("configurations scored: 0 (re-scores existing spec e007 only to get its residuals)")
d = p.merge(df, on=["date", "y", "hd_yt_lastday", "hd_ytdays_7", "hd_ytdays_3"])
d["res"] = d["y"] - d["prob"]
cols = ["wt_all_3", "wt_all_7", "wt_local_7", "wt_local_14", "wt_trend", "wt_max_7", "wt_n_7", "wt_anom_7",
        "bait_sardine_7", "bait_squid_7", "bait_anchovy_7", "bait_mackerel_7", "mf_wind_max", "mf_gust", "mf_seas",
        "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west", "fc_wind_kt", "fc_swell_ft"]
for sub, g in (("all", d), ("lastday=0", d[d.hd_yt_lastday == 0]), ("lastday=1", d[d.hd_yt_lastday == 1])):
    print(f"\n== {sub}: n={len(g)} pos={g.y.mean():.3f}")
    for c in cols:
        x = g[[c, "res", "y"]].dropna()
        if x[c].nunique() < 2: continue
        r = np.corrcoef(x[c], x["res"])[0, 1]
        q = pd.qcut(x[c].rank(method="first"), 3, labels=False)
        rates = x.groupby(q)["y"].mean().round(3).tolist(); resm = x.groupby(q)["res"].mean().round(3).tolist()
        print(f"{c:18s} n={len(x):4d} corr(res)={r:+.3f}  y by tercile={rates}  mean res by tercile={resm}")
