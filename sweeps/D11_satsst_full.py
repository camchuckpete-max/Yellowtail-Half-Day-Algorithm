# Goal D sweep 11 (D-050): kelp-box satellite SST on the full 2010 -> now series (request 0005).
# 1) Same D10/D10b models on folds 2012-2023. 2) Out-of-sample check of D-049: the Jul-Oct gap table
# for 2020-2023 only (years not seen when the effect was found). 3) Held-out band table for the best model.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
df["hc_maxT_c"] = np.fmax(F, df["hc_sat_lj_f"]) - 66.0
df["hc_gap"] = df["hc_sat_lj_f"] - F
MAP = {"pm": "trip_pm", "tw": "trip_twilight", "dcos": "doy_cos", "dsin": "doy_sin", "oni": "hc_ci_oni"}
for base in ("hc_Fc", "hc_maxT_c"):
    for k, col in MAP.items():
        df[f"{base}_{k}"] = df[base] * df[col]
SEASON = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_ci_oni", "hc_pier_wtmp_chg3d"]
PIER = ["hc_Fc"] + [f"hc_Fc_{k}" for k in MAP]
MAXT = ["hc_maxT_c"] + [f"hc_maxT_c_{k}" for k in MAP]
d = df[df["hc_sat_lj_f"].notna() & df["hc_Fc"].notna()].copy()
YEARS = range(2012, 2024)
cov = d.groupby(d.date.dt.year).size()
print(f"# Goal D configurations scored on dev: 3; source {man['source_commit'][:7]}; folds 2012-2023")
print("trips with kelp-box SST by year:", cov.to_dict())
res = {}
for k, fs in (("pier (D5 base)", SEASON + PIER), ("pier + gap", SEASON + PIER + ["hc_gap"]), ("max(pier,sat)", SEASON + MAXT)):
    p = trips.walk_forward(d, fs, YEARS, C=0.1); res[k] = p
    s = trips.summary(p)
    print(f"{k:16s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
dv = d[(d.trip_twilight == 0) & d.date.dt.month.between(7, 10)].copy()
dv["pier"] = pd.cut(dv["hc_Fc"] + 66, [0, 66, 70, 99], labels=["<66", "66-70", ">=70"])
dv["gap_c"] = pd.cut(dv["hc_gap"], [-99, 1.5, 99], labels=["sat not >1.5F warmer", "sat >1.5F warmer"])
for lab, yrs in (("2012-2019 (where D-049 was found)", (2012, 2019)), ("2020-2023 (out-of-sample check)", (2020, 2023))):
    w = dv[dv.date.dt.year.between(*yrs)]
    print(f"\nJul-Oct day trips {lab}: hit rate by pier band x gap")
    print(w.groupby(["pier", "gap_c"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("gap_c").to_string())
print("\nBand table, max(pier,sat), held-out 2012-2023:")
print(trips.band_table(res["max(pier,sat)"]).to_string(index=False))
print("\nBand table, pier (D5 base), same trips:")
print(trips.band_table(res["pier (D5 base)"]).to_string(index=False))
