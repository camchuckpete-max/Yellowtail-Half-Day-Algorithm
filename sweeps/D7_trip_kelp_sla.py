# Goal D sweep 7 (D-046): kelp canopy (quarter end + 365 d PIT lag) on the complete kelp table, and SLA
# re-tested on the complete SLA table. Kelp scored on folds 2012-2023 (full coverage), SLA on 2016-2023.
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
BASE = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc", "hc_Fc_pm", "hc_Fc_tw",
                              "hc_Fc_dcos", "hc_Fc_dsin", "hc_ci_oni", "hc_Fc_oni", "hc_pier_wtmp_chg3d"]
KL = ["hc_kelp_lj_last", "hc_kelp_lj_anom", "hc_kelp_pl_last", "hc_kelp_pl_anom"]
SL = ["hc_sla_lj_last", "hc_sla_lj_7d"]
runs = [("D5 base", BASE, range(2012, 2024)), ("base+kelp", BASE + KL, range(2012, 2024)),
        ("D5 base", BASE, range(2016, 2024)), ("base+sla", BASE + SL, range(2016, 2024)),
        ("base+kelp+sla", BASE + KL + SL, range(2016, 2024))]
print(f"# Goal D configurations scored on dev: {len(runs)}; source {man['source_commit'][:7]}")
dev = df[df.date.dt.year.between(2012, 2023)]
print("coverage 2012-2023:", {c: round(float(dev[c].notna().mean()), 2) for c in KL + SL})
for k, fs, yrs in runs:
    s = trips.summary(trips.walk_forward(df, fs, yrs, C=0.1))
    print(f"{k:14s} folds {min(yrs)}-{max(yrs)} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
# Descriptive: hit rate by visible La Jolla kelp anomaly tercile, within pier-temp bands (dev only)
d = dev.dropna(subset=["hc_kelp_lj_anom", "hc_Fc"]).copy()
d["kelp_t"] = pd.qcut(d["hc_kelp_lj_anom"], 3, labels=["low", "mid", "high"])
d["Fband"] = pd.cut(d["hc_Fc"] + 66, [0, 64, 68, 72, 99], labels=["<64", "64-68", "68-72", ">72"])
print("\nhit rate (trips) by pier-temp band x La Jolla kelp anomaly tercile, dev 2012-2023:")
print(d.groupby(["Fband", "kelp_t"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("kelp_t").to_string())
