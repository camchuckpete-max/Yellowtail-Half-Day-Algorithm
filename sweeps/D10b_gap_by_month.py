# Goal D sweep 10b (D-049): is the pier-vs-kelp-box-satellite gap effect just season (summer stratification)?
# Descriptive within calendar month, plus 3 models (gap x temp interaction, max of the two, tree) on folds 2012-2019.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
df["hc_gap"] = df["hc_sat_lj_f"] - F                    # + = kelp-box surface warmer than the pier
df["hc_gap_x_Fc"] = df["hc_gap"] * df["hc_Fc"]
df["hc_maxT_c"] = np.fmax(F, df["hc_sat_lj_f"]) - 66.0
d = df[df["hc_sat_lj_f"].notna() & df["hc_Fc"].notna()].copy()
YEARS = range(2012, 2020)
print(f"# Goal D configurations scored on dev: 4; source {man['source_commit'][:7]}; folds 2012-2019")
dv = d[d.date.dt.year.between(2012, 2019) & (d.trip_twilight == 0)].copy()
dv["month"] = dv.date.dt.month
dv["gap_c"] = pd.cut(dv["hc_gap"], [-99, -1.5, 1.5, 99], labels=["sat colder", "within 1.5F", "sat warmer >1.5F"])
print("\nmean gap (sat - pier, F) by month:", dv.groupby("month")["hc_gap"].mean().round(2).to_dict())
w = dv[dv.month.between(7, 10)]
w = w.assign(pier=pd.cut(w["hc_Fc"] + 66, [0, 66, 70, 99], labels=["<66", "66-70", ">=70"]))
print("\nJul-Oct day trips: hit rate by month x pier band x gap class")
print(w.groupby(["month", "pier", "gap_c"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("gap_c").to_string())
SEASON = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_ci_oni", "hc_pier_wtmp_chg3d"]
PIER = ["hc_Fc", "hc_Fc_pm", "hc_Fc_tw", "hc_Fc_dcos", "hc_Fc_dsin", "hc_Fc_oni"]
runs = [("pier (D5 base)", SEASON + PIER), ("pier + gap", SEASON + PIER + ["hc_gap"]),
        ("pier + gap + gap x temp", SEASON + PIER + ["hc_gap", "hc_gap_x_Fc"]),
        ("max(pier,sat) instead", SEASON + ["hc_maxT_c"] + [c.replace("hc_Fc", "hc_maxT_c") for c in PIER[1:]])]
for c in PIER[1:]:
    d[c.replace("hc_Fc", "hc_maxT_c")] = d["hc_maxT_c"] * d[{"hc_Fc_pm": "trip_pm", "hc_Fc_tw": "trip_twilight", "hc_Fc_dcos": "doy_cos", "hc_Fc_dsin": "doy_sin", "hc_Fc_oni": "hc_ci_oni"}[c]]
print()
for k, fs in runs:
    s = trips.summary(trips.walk_forward(d, fs, YEARS, C=0.1))
    print(f"{k:26s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
# Year composition of the high cells (descriptive only)
w2 = dv[dv.month.between(7, 10) & (dv["hc_Fc"] >= 0)].copy()
w2["cell"] = np.where((w2["hc_Fc"] >= 4) & (w2["hc_gap"] > 1.5), "pier>=70 & sat warmer>1.5",
             np.where((w2["hc_Fc"] < 4) & (w2["hc_gap"] > 1.5), "pier 66-70 & sat warmer>1.5", "other pier>=66"))
print("\nJul-Oct, pier >= 66F: hit rate and trips by year x cell")
print(w2.groupby(["cell", w2.date.dt.year], observed=True)["y"].agg(["mean", "size"]).round(2).unstack(0).to_string())
