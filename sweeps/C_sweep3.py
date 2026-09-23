# Agent C sweep 3: can a shallow tree model use temperature / forecast non-linearly?
# 3 feature sets (incl. a no-environment control) x 2 thresholds = 6 configurations. No bootstrap.
import sys; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import _R2, _D1
df, _ = dataset.build(); df = evaluate.eligible(df)
MF = ["mf_wind_max", "mf_gust", "mf_seas", "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west"]
sets = {"hgb_R2D1": _R2 + _D1, "hgb_R2D1+WTC": _R2 + _D1 + ["wt_c", "wt_all_7"],
        "hgb_R2D1+WTC+MF": _R2 + _D1 + ["wt_c", "wt_all_7"] + MF}
grid = ["fixed:0.35", "fixed:0.4"]
print(f"configurations scored: {len(sets) * len(grid)}", flush=True)
for name, fs in sets.items():
    for thr in grid:
        sp = Spec(f"{name}_{thr}", fs, "hgb", threshold_rule=thr)
        p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
        pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
        print(f"{sp.name:32s} nf={len(fs):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
              f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
