# Agent F: bootstrap CI (D-009) for the two best F configurations (eF01 = F_sweep3 B01_C0.03_recal90_mccrange,
# eF02 = F_sweep3 B01_C0.03_recal60_p40). Finalist re-runs: 2 configurations counted.
import sys; sys.path.insert(0, '/home/user/yt-wt-F')
from yt import dataset, evaluate, experiments
df, _ = dataset.build(); df = evaluate.eligible(df)
print("configurations scored: 2 finalist re-runs (eF01, eF02) with bootstrap", flush=True)
for name in ("eF01_B01_recal90_mccrange", "eF02_B01_recal60_p40"):
    sp = experiments.get(name)
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=True)
    d = s["mcc_diff_vs_best_baseline"]
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    pb = {f: round(evaluate.hard_metrics(g["y"], g["hd_yt_lastday"])["mcc"], 3) for f, g in p.groupby("fold")}
    print(f"{name:28s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
          f"vs {s['best_baseline']} {s['baselines'][s['best_baseline']]['mcc']:.3f} dMCC mean={d['mean']:.3f} "
          f"CI95=[{d['lo95']:.3f}, {d['hi95']:.3f}] p(<=0)={d['p_le_0']:.3f} folds={pf} B1 folds={pb}", flush=True)
