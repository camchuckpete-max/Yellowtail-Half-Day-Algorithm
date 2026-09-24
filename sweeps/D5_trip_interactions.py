# Goal D sweep 5 (D-044): pier-temperature interactions with trip type, season and ENSO,
# walk-forward (each year predicted by a model trained only on earlier years), dev 2012-2023.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0                                   # centred °F (derived from hc_pier_wtmp_24h)
df["hc_Fc_pm"] = df["hc_Fc"] * df["trip_pm"]
df["hc_Fc_tw"] = df["hc_Fc"] * df["trip_twilight"]
df["hc_Fc_dcos"] = df["hc_Fc"] * df["doy_cos"]
df["hc_Fc_dsin"] = df["hc_Fc"] * df["doy_sin"]
df["hc_Fc_oni"] = df["hc_Fc"] * df["hc_ci_oni"]
df["hc_Fc_chg"] = df["hc_pier_wtmp_chg3d"]
base = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_Fc"]
inter = ["hc_Fc_pm", "hc_Fc_tw", "hc_Fc_dcos", "hc_Fc_dsin"]
sets = {"F": base, "F+inter": base + inter, "F+inter+oni": base + inter + ["hc_ci_oni", "hc_Fc_oni"],
        "F+inter+oni+chg": base + inter + ["hc_ci_oni", "hc_Fc_oni", "hc_Fc_chg"]}
YEARS = range(2012, 2024)
print(f"# Goal D configurations scored on dev: {len(sets) * 2 + 1}; source {man['source_commit'][:7]}")
res = {}
for k, fs in sets.items():
    for C in (0.1, 1.0):
        p = trips.walk_forward(df, fs, YEARS, C=C)
        s = trips.summary(p); res[(k, C)] = p
        print(f"{k:18s} C={C:<4} AUC={s['auc']:.3f} Brier={s['brier']:.4f}", flush=True)
pt, rules = trips.tree_rules(df, ["hc_Fc", "doy_cos", "doy_sin", "trip_am", "trip_pm", "trip_twilight",
                                  "hc_ci_oni", "hc_pier_wtmp_chg3d"], YEARS, depth=4, min_leaf=100)
s = trips.summary(pt); print(f"tree depth4 leaf>=100 AUC={s['auc']:.3f} Brier={s['brier']:.4f}")
best = min(res, key=lambda k: trips.summary(res[k])["brier"])
print(f"\nHeld-out band table for best-Brier logistic {best}:")
print(trips.band_table(res[best]).to_string(index=False))
print("\nHeld-out band table for depth-4 tree:"); print(trips.band_table(pt).to_string(index=False))
print("\nDepth-4 tree trained on 2010-2022 (hc_Fc = pier °F - 66):"); print(rules)
