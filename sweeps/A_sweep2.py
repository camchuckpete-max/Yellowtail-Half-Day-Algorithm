# Agent A sweep 2: compact v2 FishDope summaries (1-3 features) on top of R+D1. No bootstrap.
# Chosen from 2010-2011 (training-only years) univariate tables, not from dev scores.
# Configurations scored on dev in this script: 12.
import sys; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
sets = {"P": ["fd2_local_presdays_3"],
        "P+C7": ["fd2_local_presdays_3", "fd2_local_catchdays_7"],
        "P+C3+N": ["fd2_local_presdays_3", "fd2_local_catchdays_3", "fd2_local_net_d1"]}
runs = [(f"R+D1+{k}_C{C}_{thr}", R + D1 + v, C, thr) for k, v in sets.items()
        for C in (0.01, 0.03) for thr in ("fixed:0.35", "fixed:0.4")]
print(f"# configurations scored: {len(runs)}")
for name, fs, C, thr in runs:
    sp = Spec(name, fs, "logreg", C=C, threshold_rule=thr)
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    print(f"{sp.name:36s} nfeat={len(fs):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
          f"B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
