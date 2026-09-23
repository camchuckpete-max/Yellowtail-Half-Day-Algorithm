# Agent A sweep 1: v2 FishDope evidence (D-A01) on top of catch history. No bootstrap.
# Configurations scored on dev in this script: 21 (1 e007 reproduction + 18 + 2).
import sys; sys.path.insert(0, '.')
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
V2I = ["!hd_yt_lastday*fd2_local_catchdays_3", "hd_yt_lastday*fd2_local_neg_d1", "!hd_yt_lastday*fd2_local_presdays_3",
       "hd_yt_lastday*fd2_local_net_d1"]
V2ALL = [f for f in __import__("yt.features", fromlist=["FEATURES"]).FEATURES if f.startswith("fd2_")]
runs = [("e007_repro", R + D1 + FS + FSI, 0.03, "fixed:0.35")]
for name, fs in (("R+D1+V2", R + D1 + V2), ("R+D1+V2+V2I", R + D1 + V2 + V2I), ("R+D1+FS+FSI+V2+V2I", R + D1 + FS + FSI + V2 + V2I)):
    for C in (0.01, 0.03, 0.1):
        for thr in ("fixed:0.35", "fixed:0.4"):
            runs.append((f"{name}_C{C}_{thr}", fs, C, thr))
for thr in ("fixed:0.35", "fixed:0.4"):
    runs.append((f"R+D1+V2ALL_C0.03_{thr}", R + D1 + V2ALL, 0.03, thr))
print(f"# configurations scored: {len(runs)}")
for name, fs, C, thr in runs:
    sp = Spec(name, fs, "logreg", C=C, threshold_rule=thr)
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    print(f"{sp.name:36s} nfeat={len(fs):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
          f"B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
