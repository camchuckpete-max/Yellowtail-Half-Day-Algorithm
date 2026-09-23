# Agent C: bootstrap CI (D-009) for agent C's two best configurations from sweeps C_sweep1/C_sweep2.
# Re-scores already-counted configurations; 0 new configurations.
import sys; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import _R2, _D1, _FS, _FSI
df, _ = dataset.build(); df = evaluate.eligible(df)
B = _R2 + _D1 + _FS + _FSI
print("configurations scored: 0 new (re-scores B+WT2_C0.01_fixed:0.35 and B+WTC_C0.03_fixed:0.4)", flush=True)
for sp in (Spec("B+WT2_C0.01_fixed:0.35", B + ["wt_all_7", "wt_anom_7", "wt_trend", "wt_local_14", "wt_max_7", "wt_n_7"],
                "logreg", C=0.01, threshold_rule="fixed:0.35"),
           Spec("B+WTC_C0.03_fixed:0.4", B + ["wt_c"], "logreg", C=0.03, threshold_rule="fixed:0.4")):
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=True)
    d = s["mcc_diff_vs_best_baseline"]
    print(f"{sp.name:28s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} vs {s['best_baseline']} "
          f"dMCC mean={d['mean']:.3f} CI95=[{d['lo95']:.3f}, {d['hi95']:.3f}] p(<=0)={d['p_le_0']:.3f}", flush=True)
