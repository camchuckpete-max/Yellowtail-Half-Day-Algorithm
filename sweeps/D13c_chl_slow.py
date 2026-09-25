# Goal D sweep 13c (D-052): slow chlorophyll (60/120-day mean log chl, 1-day lag) as the year/season-level
# signal. (1) walk-forward folds 2013-2023; (2) the D12 condition tree refit with chl_120d on 2012-2019 and
# checked on 2020-2023 — does it explain the 2020-2023 drop at equal water temperature?
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
df["hc_n20"] = (df["date"] >= "2021-08-27").astype(int)
df["hc_chl120_x_Fc"] = df["hc_chl_sd_120d"] * df["hc_Fc"]
d = df[df["hc_chl_sd_120d"].notna()].copy()
YEARS = list(range(2013, 2024))
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
runs = [("D5 base", BASE), ("base+chl60 SD", BASE + ["hc_chl_sd_60d"]), ("base+chl120 SD", BASE + ["hc_chl_sd_120d"]),
        ("base+chl120 SD + x temp", BASE + ["hc_chl_sd_120d", "hc_chl120_x_Fc"]),
        ("base+chl120 LJ", BASE + ["hc_chl_lj_120d"]), ("base+chl120 SD + chl3d", BASE + ["hc_chl_sd_120d", "hc_chl_sd_3d"]),
        ("base+chl120 SD + n20 flag", BASE + ["hc_chl_sd_120d", "hc_n20"])]
print(f"# Goal D configurations scored on dev: {len(runs)} + 2 trees; source {man['source_commit'][:7]}; folds 2013-2023")
res = {}
for k, fs in runs:
    p = trips.walk_forward(d, fs, YEARS, C=0.1, train_start="2012-01-01"); res[k] = p
    s = trips.summary(p)
    print(f"{k:26s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
best = min(res, key=lambda k: trips.summary(res[k])["brier"])
print(f"\nBand table, lowest-Brier model ({best}), held-out 2013-2023:")
print(trips.band_table(res[best]).to_string(index=False))
print("\nBand table, D5 base, same trips:")
print(trips.band_table(res["D5 base"]).to_string(index=False))
# Condition tree, fit 2012-2019 / check 2020-2023
d["pier_F"] = F; d["month"] = d.date.dt.month
d["slot"] = np.select([d.trip_twilight == 1, d.trip_pm == 1], [2, 1], 0)
d["oni"] = d["hc_ci_oni"]; d["chl120_mg"] = np.exp(d["hc_chl_sd_120d"])
e = d[d.date.dt.year.between(2012, 2023)].dropna(subset=["pier_F", "oni"])
tr, te = e[e.date.dt.year <= 2019], e[e.date.dt.year >= 2020]
for X in (["pier_F", "month", "slot", "oni"], ["pier_F", "month", "slot", "oni", "chl120_mg"]):
    t = DecisionTreeClassifier(max_depth=4, min_samples_leaf=80, random_state=0).fit(tr[X], tr.y)
    print(f"\ntree {X}: 2020-2023 AUC {roc_auc_score(te.y, t.predict_proba(te[X])[:, 1]):.3f}")
    tree = t.tree_; paths = {}
    def walk(n, c):
        if tree.children_left[n] == -1: paths[n] = " & ".join(c); return
        f, th = X[tree.feature[n]], tree.threshold[n]
        walk(tree.children_left[n], c + [f"{f}<={th:.2f}"]); walk(tree.children_right[n], c + [f"{f}>{th:.2f}"])
    walk(0, [])
    a, b = tr.assign(leaf=t.apply(tr[X])), te.assign(leaf=t.apply(te[X]))
    g = pd.DataFrame({"fit": a.groupby("leaf").y.mean(), "n_fit": a.groupby("leaf").size(),
                      "check": b.groupby("leaf").y.mean(), "n_check": b.groupby("leaf").size()})
    g["conditions"] = [paths[i] for i in g.index]
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 150)
    print(g.sort_values("fit").round(3).to_string())
