# Goal C sweep 1 (D-031): conditions-only models vs season-only S0. Dev 2012-2016.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec

S0 = ["doy_sin", "doy_cos"]
S2 = S0 + ["doy_sin2", "doy_cos2"]
MOON = ["moon_illum", "moon_sin", "moon_cos"]
TIDE = ["tide_range_d", "tide_high_d", "tide_low_d", "tide_range_chg"]
DAY = ["fc_wind_kt", "fc_swell_ft", "fc_swell_s", "cd_upw_d", "cd_swell_south_d",
       "mf_wind_max", "mf_gust", "mf_seas", "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west"]
HIST = ["cd_wind_3", "cd_upw_3", "cd_swell_3", "cd_wind_7", "cd_upw_7", "cd_swell_7", "cd_swell_south_7",
        "cd_wind_14", "cd_upw_14", "cd_swell_14", "cd_swell_south_14", "cd_wind_30", "cd_upw_30", "cd_swell_30",
        "cd_upw_14_anom", "cd_wind_14_anom", "cd_wind_offshore_3", "cd_wind_offshore_14", "cd_wind_south_3",
        "cd_wind_south_14", "cd_swell_south_3", "cd_swell_south_14", "cd_seas_3", "cd_seas_14"]
SETS = {"S0": S0, "S2": S2, "S2+moon": S2 + MOON, "S2+tide": S2 + TIDE, "S2+day": S2 + DAY,
        "S2+hist": S2 + HIST, "S2+all": S2 + MOON + TIDE + DAY + HIST + ["weekend"]}
CONFIGS = [(k, "logreg", C, thr) for k in SETS for C in (0.1, 1.0) for thr in ("mcc", "mcc_range:0.2:0.5")]
CONFIGS += [("S2+all", "hgb", 1.0, thr) for thr in ("mcc", "mcc_range:0.2:0.5")]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, model, C, thr = cfg
    sp = Spec(f"C_{k}_{model}_C{C}_{thr}", SETS[k], model, C=C, threshold_rule=thr, inputs="conditions")
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:44s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
            f"acc={s['model']['accuracy']:.3f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()
    with Pool(4) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
