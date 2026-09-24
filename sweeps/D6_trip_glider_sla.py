# Goal D sweep 6 (D-045): glider temperature at depth (2014+) and sea-level anomaly (2015+) on top of
# the D5 model. All models scored on the same folds 2016-2023 (dev); train from 2010, missing -> median.
import sys; sys.path.insert(0, '.')
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
GL = ["hc_glider_t5_10d", "hc_glider_t45_10d", "hc_glider_strat_10d"]
SL = ["hc_sla_lj_last", "hc_sla_lj_7d"]
YEARS = range(2016, 2024)
sets = {"D5 base": BASE, "base+glider": BASE + GL, "base+sla": BASE + SL, "base+glider+sla": BASE + GL + SL}
print(f"# Goal D configurations scored on dev: {len(sets)}; source {man['source_commit'][:7]}; folds 2016-2023")
print("coverage (share of dev trips with value):", {c: round(float(df.loc[df.date.dt.year.between(2016, 2023), c].notna().mean()), 2) for c in GL + SL})
res = {}
for k, fs in sets.items():
    p = trips.walk_forward(df, fs, YEARS, C=0.1)
    s = trips.summary(p); res[k] = p
    print(f"{k:16s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
