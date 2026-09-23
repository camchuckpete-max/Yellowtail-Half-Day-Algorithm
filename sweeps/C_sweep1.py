# Agent C sweep 1: environmental features (D-C01 water temp / bait, D-C02 NWS CWF) on top of the e007
# feature set. No bootstrap; 8 feature sets x 3 (C, threshold) = 24 configurations.
import sys; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import _R2, _D1, _FS, _FSI
df, _ = dataset.build(); df = evaluate.eligible(df)
B = _R2 + _D1 + _FS + _FSI
WT = ["wt_all_7", "wt_anom_7", "wt_trend"]
WT2 = WT + ["wt_local_14", "wt_max_7", "wt_n_7"]
BAIT = ["bait_sardine_7", "bait_squid_7", "bait_anchovy_7", "bait_mackerel_7"]
MF = ["mf_wind_max", "mf_gust", "mf_seas", "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west"]
ENVI = ["!hd_yt_lastday*wt_anom_7", "hd_yt_lastday*wt_anom_7"]
sets = {"B": B, "B+WT": B + WT, "B+WT2": B + WT2, "B+BAIT": B + BAIT, "B+MF": B + MF,
        "B+WT+BAIT": B + WT + BAIT, "B+WT+BAIT+MF": B + WT + BAIT + MF, "B+WT+ENVI": B + WT + ENVI}
grid = [(0.03, "fixed:0.35"), (0.03, "fixed:0.4"), (0.01, "fixed:0.35")]
print(f"configurations scored: {len(sets) * len(grid)}", flush=True)
for name, fs in sets.items():
    for C, thr in grid:
        sp = Spec(f"{name}_C{C}_{thr}", fs, "logreg", C=C, threshold_rule=thr)
        p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
        pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
        print(f"{sp.name:32s} nf={len(fs):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
              f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
