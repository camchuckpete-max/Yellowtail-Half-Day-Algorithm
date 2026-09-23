# Agent C sweep 2: dense centred water temperature (D-C03) and its interaction with B1's input,
# motivated by sweeps/C_diag1_output.txt (residual correlation on dev -> selection on dev, disclosed).
# 5 feature sets x 4 (C, threshold) = 20 configurations. No bootstrap.
import sys; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import _R2, _D1, _FS, _FSI
df, _ = dataset.build(); df = evaluate.eligible(df)
B = _R2 + _D1 + _FS + _FSI
TI = ["hd_yt_lastday*wt_c", "!hd_yt_lastday*wt_c"]
sets = {"B+WTC": B + ["wt_c"], "B+TI": B + TI, "B+WTC+TI": B + ["wt_c"] + TI,
        "B+TI+LOC": B + TI + ["hd_yt_lastday*wt_c_local"], "R2D1+TI": _R2 + _D1 + TI}
grid = [(0.03, "fixed:0.35"), (0.03, "fixed:0.4"), (0.1, "fixed:0.35"), (0.01, "fixed:0.35")]
print(f"configurations scored: {len(sets) * len(grid)}", flush=True)
for name, fs in sets.items():
    for C, thr in grid:
        sp = Spec(f"{name}_C{C}_{thr}", fs, "logreg", C=C, threshold_rule=thr)
        p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
        pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
        print(f"{sp.name:32s} nf={len(fs):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
              f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
