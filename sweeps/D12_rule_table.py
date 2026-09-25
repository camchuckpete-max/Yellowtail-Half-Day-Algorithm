# Goal D sweep 12 (D-051): the owner's deliverable — readable condition ranges -> chance of a yellowtail on a
# New Seaforth / Sea Watch half-day trip. A shallow tree is fit on 2012-2019 only; every leaf is then scored
# on 2020-2023 (never used for fitting) so each range carries an out-of-sample hit rate.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from yt import trips
df, man = trips.build()
df["pier_F"] = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["month"] = df.date.dt.month
df["slot"] = np.select([df.trip_twilight == 1, df.trip_pm == 1], [2, 1], 0)   # 0 AM, 1 PM, 2 twilight
df["oni"] = df["hc_ci_oni"]
df["kelp_minus_pier_F"] = df["hc_sat_lj_f"] - df["pier_F"]
df["pier_chg3d_F"] = df["hc_pier_wtmp_chg3d"] * 9 / 5
X = ["pier_F", "month", "slot", "oni", "kelp_minus_pier_F", "pier_chg3d_F"]
d = df[df.date.dt.year.between(2012, 2023)].dropna(subset=X).copy()
tr, te = d[d.date.dt.year <= 2019], d[d.date.dt.year >= 2020]
print(f"# Goal D configurations: 3 tree depths fit on 2012-2019, scored on 2020-2023; source {man['source_commit'][:7]}")
print(f"trips: fit {len(tr)} (rate {tr.y.mean():.3f}), check {len(te)} (rate {te.y.mean():.3f})")
from sklearn.metrics import roc_auc_score
best = None
for depth in (3, 4, 5):
    t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=80, random_state=0).fit(tr[X], tr.y)
    auc = roc_auc_score(te.y, t.predict_proba(te[X])[:, 1])
    print(f"depth {depth}: leaves {t.get_n_leaves()}, 2020-2023 AUC {auc:.3f}")
    if depth == 4: best = t
t = best
print("\nTree (depth 4, fit 2012-2019):")
print(export_text(t, feature_names=X, decimals=1))
tr = tr.assign(leaf=t.apply(tr[X])); te = te.assign(leaf=t.apply(te[X]))
g = pd.DataFrame({"fit_rate": tr.groupby("leaf").y.mean(), "fit_trips": tr.groupby("leaf").size(),
                  "check_rate": te.groupby("leaf").y.mean(), "check_trips": te.groupby("leaf").size()})
# human-readable path per leaf
tree = t.tree_; paths = {}
def walk(n, conds):
    if tree.children_left[n] == -1:
        paths[n] = " & ".join(conds) or "all"; return
    f, thr = X[tree.feature[n]], tree.threshold[n]
    walk(tree.children_left[n], conds + [f"{f} <= {thr:.1f}"]); walk(tree.children_right[n], conds + [f"{f} > {thr:.1f}"])
walk(0, [])
g["conditions"] = [paths[i] for i in g.index]
g = g.sort_values("fit_rate")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 140)
print("\nLeaves sorted by 2012-2019 rate (slot: 0 AM, 1 PM, 2 twilight; oni = ENSO index; temps F):")
print(g[["fit_rate", "fit_trips", "check_rate", "check_trips", "conditions"]].round(3).to_string())
