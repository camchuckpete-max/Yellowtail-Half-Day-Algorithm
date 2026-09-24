# Goal C sweep 3 (D-032): small combinations of the only screen features that helped AUC or Brier.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
S0 = ["doy_sin", "doy_cos"]
SETS = {"S0": S0,
        "S0+sws90": S0 + ["cd_sws_90_anom"],
        "S0+sws90+upw30": S0 + ["cd_sws_90_anom", "cd_upw_30_anom"],
        "S0+sws90+upw30+seas3": S0 + ["cd_sws_90_anom", "cd_upw_30_anom", "cd_seas_3"],
        "S2+sws90+upw30+seas3": S0 + ["doy_sin2", "doy_cos2", "cd_sws_90_anom", "cd_upw_30_anom", "cd_seas_3"]}
CONFIGS = [(k, C, rt) for k in SETS for C in (0.1, 1.0) for rt in ("year", "month")]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, C, rt = cfg
    sp = Spec(f"C_{k}_C{C}_{rt}", SETS[k], "logreg", C=C, threshold_rule="mcc_range:0.2:0.5", retrain=rt, inputs="conditions")
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:40s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.4f} brier={s['model']['brier']:.4f} "
            f"acc={s['model']['accuracy']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()
    with Pool(4) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
