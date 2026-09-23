# Agent A sweep 3: where (if anywhere) does text help? AUC stratified by the B1 input, plus
# gradient boosting on R+D1+V2 (can use interactions). No bootstrap.
# Configurations scored on dev in this script: 5 (2 are re-scores of configs already counted
# in A_sweep1 / earlier sweep 3; counted again to be conservative).
import sys; sys.path.insert(0, '.')
from sklearn.metrics import roc_auc_score
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
FS = ["fd_local_catch_d1", "fd_local_sight_d1", "fd_local_neg_d1", "fd_coronado_catch_d1", "fd_north_catch_d1",
      "fd_local_catch_3", "fd_local_catchdays_3", "fd_local_sight_3", "fd_coronado_catch_3"]
FSI = ["hd_yt_lastday*fd_local_catch_3", "!hd_yt_lastday*fd_local_catch_3", "hd_yt_lastday*fd_local_neg_d1",
       "!hd_yt_lastday*fd_coronado_catch_d1"]
V2 = ["fd2_local_catch_d1", "fd2_local_neg_d1", "fd2_local_present_d1", "fd2_local_catchdays_3", "fd2_local_presdays_3",
      "fd2_local_catch_priv_3", "fd2_local_catch_boat_3", "fd2_local_net_d1", "fd2_coronado_catch_d1",
      "fd2_local_catchdays_7", "fd2_local_days_since_catch"]
runs = [("R+D1_C0.01_fixed:0.35", R + D1, "logreg", 0.01, "fixed:0.35"),
        ("e007_repro", R + D1 + FS + FSI, "logreg", 0.03, "fixed:0.35"),
        ("R+D1+V2_C0.03_fixed:0.4", R + D1 + V2, "logreg", 0.03, "fixed:0.4"),
        ("R+D1+V2_hgb_fixed:0.35", R + D1 + V2, "hgb", 1.0, "fixed:0.35"),
        ("R+D1+V2_hgb_fixed:0.4", R + D1 + V2, "hgb", 1.0, "fixed:0.4")]
print(f"# configurations scored: {len(runs)}")
for name, fs, model, C, thr in runs:
    sp = Spec(name, fs, model, C=C, threshold_rule=thr)
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    strat = {b: round(roc_auc_score(g["y"], g["prob"]), 3) for b, g in p.groupby("hd_yt_lastday")}
    print(f"{sp.name:30s} nfeat={len(fs):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
          f"auc|B1=0={strat[0]} auc|B1=1={strat[1]} brier={s['model']['brier']:.4f} folds={pf}", flush=True)
