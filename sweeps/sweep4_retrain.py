# Sweep 4 (coordinator, D-026): refit cadence and recency weighting, run on 4 processes.
# 36 configurations = 3 feature sets x retrain {year, month} x halflife {0, 365, 120} x threshold {0.35, 0.4}.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate, experiments
from yt.evaluate import Spec

SETS = {"e005": experiments.get("e005_recency_d1_C001_p35"),
        "e007": experiments.get("e007_recency_d1_fdsent_C003_p35"),
        "eB01": experiments.get("eB01_fleet_C003_mccrange")}
CONFIGS = [(k, rt, hl, thr) for k in SETS for rt in ("year", "month") for hl in (0.0, 365.0, 120.0)
           for thr in ("fixed:0.35", "fixed:0.4")]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, rt, hl, thr = cfg
    base = SETS[k]
    sp = Spec(f"{k}_{rt}_hl{int(hl)}_{thr}", base.features, base.model, C=base.C, threshold_rule=thr,
              retrain=rt, halflife_days=hl, extra=base.extra)
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:34s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
            f"calls={s['model']['tp'] + s['model']['fp']} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()  # warm the cache once before forking
    with Pool(4) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
