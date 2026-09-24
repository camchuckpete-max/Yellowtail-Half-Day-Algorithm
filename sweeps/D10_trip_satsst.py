# Goal D sweep 10 (D-049): satellite SST at the kelp boxes (la_jolla, point_loma_kelp: 2010-2019-09 only) and
# coastal tiles vs the Scripps Pier thermometer. Kelp-box models scored on folds 2012-2019 (trips with a value).
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import trips
df, man = trips.build()
F = df["hc_pier_wtmp_24h"] * 9 / 5 + 32
df["hc_Fc"] = F - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Fc_{k}"] = df["hc_Fc"] * df[col]
df["hc_Sc"] = df["hc_sat_lj_f"] - 66.0
for k, col in (("pm", "trip_pm"), ("tw", "trip_twilight"), ("dcos", "doy_cos"), ("dsin", "doy_sin"), ("oni", "hc_ci_oni")):
    df[f"hc_Sc_{k}"] = df["hc_Sc"] * df[col]
df["hc_pier_minus_satlj"] = F - df["hc_sat_lj_f"]
df["hc_satlj_minus_sd"] = df["hc_sat_lj_f"] - df["hc_sat_sd_f"]
SEASON = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2", "hc_ci_oni", "hc_pier_wtmp_chg3d"]
PIER = ["hc_Fc", "hc_Fc_pm", "hc_Fc_tw", "hc_Fc_dcos", "hc_Fc_dsin", "hc_Fc_oni"]
SAT = ["hc_Sc", "hc_Sc_pm", "hc_Sc_tw", "hc_Sc_dcos", "hc_Sc_dsin", "hc_Sc_oni"]
d = df[df["hc_sat_lj_f"].notna() & df["hc_Fc"].notna()].copy()
YEARS = range(2012, 2020)
runs = [("pier (D5 base)", SEASON + PIER), ("kelp-box sat instead of pier", SEASON + SAT),
        ("pier + sat_lj", SEASON + PIER + ["hc_Sc"]), ("pier + pier-minus-sat", SEASON + PIER + ["hc_pier_minus_satlj"]),
        ("pier + sat lj/pl/sd/nc", SEASON + PIER + ["hc_sat_lj_f", "hc_sat_pl_f", "hc_sat_sd_f", "hc_sat_nc_f"]),
        ("pier + lj-minus-offshore", SEASON + PIER + ["hc_satlj_minus_sd"])]
print(f"# Goal D configurations scored on dev: {len(runs)}; source {man['source_commit'][:7]}; folds 2012-2019; trips {d[d.date.dt.year.isin(YEARS)].shape[0]}")
print("corr pier F vs sat la_jolla F:", round(float(d[["hc_Fc", "hc_sat_lj_f"]].corr().iloc[0, 1]), 3),
      "| mean pier - sat:", round(float(d["hc_pier_minus_satlj"].mean()), 2), "F")
for k, fs in runs:
    s = trips.summary(trips.walk_forward(d, fs, YEARS, C=0.1))
    print(f"{k:28s} AUC={s['auc']:.3f} Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
dv = d[d.date.dt.year.between(2012, 2019) & (d.trip_twilight == 0)].copy()
dv["pier"] = pd.cut(dv["hc_Fc"] + 66, [0, 64, 68, 72, 99], labels=["<64", "64-68", "68-72", ">=72"])
dv["gap"] = pd.cut(dv["hc_pier_minus_satlj"], [-99, -1.5, 1.5, 99], labels=["pier colder >1.5F", "within 1.5F", "pier warmer >1.5F"])
print("\nday trips 2012-2019: hit rate by pier band x (pier minus kelp-box satellite SST)")
print(dv.groupby(["pier", "gap"], observed=True)["y"].agg(["mean", "size"]).round(3).unstack("gap").to_string())
