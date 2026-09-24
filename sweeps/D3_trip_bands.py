# Goal D sweep 3 (D-043): calibrated probability bands + plain-language rules. Dev 2012-2023 only.
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips
df, man = trips.build()
df["pier_wtmp_f"] = df["hc_pier_wtmp_24h"] * 9 / 5 + 32          # derived (°F) for readable rules
df["hc_pier_wtmp_f"] = df["pier_wtmp_f"]
df["hc_month"] = df["date"].dt.month                              # calendar only
T0 = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2"]
PIER = ["hc_pier_wtmp_24h", "hc_pier_wtmp_chg3d", "hc_pier_wtmp_7d", "hc_pier_air_minus_water_24h"]
CI = ["hc_ci_oni", "hc_ci_pdo", "hc_ci_npgo", "hc_ci_mei_v2"]
YEARS = range(2012, 2024)
print(f"# Goal D configurations scored on dev: 3; source {man['source_commit'][:7]}; trips {len(df)}")
for name, feats in (("T0+pier", T0 + PIER), ("T0+pier+climate", T0 + PIER + CI)):
    p = trips.walk_forward_calibrated(df, feats, YEARS, C=0.1)
    s = trips.summary(p)
    print(f"\n{name} CALIBRATED: AUC={s['auc']:.3f} Brier={s['brier']:.4f}")
    print(trips.band_table(p).to_string(index=False))
# Plain-language rules: shallow tree on readable inputs (°F pier temp, month, trip type, ONI)
R = ["hc_pier_wtmp_f", "hc_month", "trip_am", "trip_pm", "trip_twilight", "boat_seawatch", "hc_ci_oni", "hc_pier_wtmp_chg3d"]
pt, rules = trips.tree_rules(df, R, YEARS, depth=3, min_leaf=150)
s = trips.summary(pt)
print(f"\nRule tree (depth 3, leaf >= 150 trips), walk-forward: AUC={s['auc']:.3f} Brier={s['brier']:.4f}")
print(trips.band_table(pt).to_string(index=False))
print("\nRules of the tree trained on 2010-2022 (weights = [no yt, yt] training trips):")
print(rules)
# Descriptive: observed hit rate by pier water temperature x trip type, dev 2012-2023
d = df[(df.date >= "2012-01-01") & (df.date < "2024-01-01")].dropna(subset=["pier_wtmp_f"])
d["trip"] = np.select([d.trip_am == 1, d.trip_pm == 1], ["AM", "PM"], "twilight")
bins = [0, 60, 62, 64, 66, 68, 70, 72, 99]
tab = d.groupby([pd.cut(d.pier_wtmp_f, bins), "trip"], observed=True).y.agg(["size", "mean"]).unstack()
print("\nObserved hit rate by pier water temp (°F, last 24h before the 9pm cutoff) x trip type, dev 2012-2023:")
print(tab.round(3).to_string())
