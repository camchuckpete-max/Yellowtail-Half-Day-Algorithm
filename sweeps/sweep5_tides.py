# Sweep 5 (coordinator, D-029): add predicted-tide features to the three best existing sets.
# Pre-declared: 6 configurations, no further tuning after seeing results.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate, experiments
from yt.evaluate import Spec
TIDE = ["tide_range_d", "tide_high_d", "tide_low_d", "tide_range_chg"]
BASES = ["e005_recency_d1_C001_p35", "eB01_fleet_C003_mccrange", "e009_eB01_monthly_p40"]
CONFIGS = [(b, t) for b in BASES for t in (False, True)]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    b, t = cfg
    s0 = experiments.get(b)
    sp = Spec(f"{b}{'+tide' if t else ''}", s0.features + (TIDE if t else []), s0.model, C=s0.C,
              threshold_rule=s0.threshold_rule, retrain=s0.retrain, halflife_days=s0.halflife_days, extra=s0.extra)
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:36s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
            f"B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# configurations scored on dev: {len(CONFIGS)} (3 are unchanged controls re-scored)", flush=True)
    dataset.build()
    with Pool(2) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
