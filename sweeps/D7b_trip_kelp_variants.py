# Goal D sweep 7b (D-046): kelp variants after D7 showed pooled AUC loss concentrated in the 2014 fold.
# Tests anomaly-only, La Jolla-only, and kelp on folds 2016-2023 alone (same folds as SLA).
import sys; sys.path.insert(0, '.')
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
KL = ["hc_kelp_lj_last", "hc_kelp_lj_anom", "hc_kelp_pl_last", "hc_kelp_pl_anom"]
runs = [("base+kelp_anom", BASE + ["hc_kelp_lj_anom", "hc_kelp_pl_anom"], range(2012, 2024)),
        ("base+kelp_lj_anom", BASE + ["hc_kelp_lj_anom"], range(2012, 2024)),
        ("base+kelp", BASE + KL, range(2016, 2024))]
print(f"# Goal D configurations scored on dev: {len(runs)}; source {man['source_commit'][:7]}")
for k, fs, yrs in runs:
    s = trips.summary(trips.walk_forward(df, fs, yrs, C=0.1))
    print(f"{k:18s} folds {min(yrs)}-{max(yrs)} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
d = df[df.date.dt.year.between(2010, 2023)]
print("\nLa Jolla kelp visible at the cutoff, yearly mean (ha): ")
print(d.groupby(d.date.dt.year)[["hc_kelp_lj_last", "hc_kelp_lj_anom", "y"]].mean().round(2).to_string())
