# Agent B sweep 4: regime interactions of the compact catch-history set (C) with B1
# (hd_yt_lastday), and a regime-split logistic with a weaker penalty on the B1=0 side.
import sys; sys.path.insert(0, '/home/user/yt-wt-B')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
XC = ["hd_yt_ewm", "tq_yt_trip_frac_3", "tq_yt_trip_frac_30", "hd_ytrate_60", "bt_hot_last"]
XI = ["!hd_yt_lastday*hd_yt_ewm", "!hd_yt_lastday*tq_yt_trip_frac_3", "!hd_yt_lastday*bt_hot_last",
      "!hd_yt_lastday*hd_ytrate_60", "hd_yt_lastday*hd_log_ytfish_d1", "hd_yt_lastday*tq_yt_trip_frac_3",
      "hd_yt_lastday*hd_ytrate_60"]
FS = ["fd_local_catch_d1", "fd_local_sight_d1", "fd_local_neg_d1", "fd_coronado_catch_d1", "fd_north_catch_d1",
      "fd_local_catch_3", "fd_local_catchdays_3", "fd_local_sight_3", "fd_coronado_catch_3"]
FSI = ["hd_yt_lastday*fd_local_catch_3", "!hd_yt_lastday*fd_local_catch_3", "hd_yt_lastday*fd_local_neg_d1",
       "!hd_yt_lastday*fd_coronado_catch_d1"]
C, CI = R + D1 + XC, R + D1 + XC + XI
cfgs = [
    Spec("CI_logreg_C0.03_fixed:0.35", CI, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    Spec("CI_logreg_C0.03_fixed:0.4", CI, "logreg", C=0.03, threshold_rule="fixed:0.4"),
    Spec("CI_logreg_C0.1_fixed:0.35", CI, "logreg", C=0.1, threshold_rule="fixed:0.35"),
    Spec("CI_logreg_C0.1_fixed:0.4", CI, "logreg", C=0.1, threshold_rule="fixed:0.4"),
    Spec("CI+FS+FSI_logreg_C0.03_fixed:0.35", CI + FS + FSI, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    Spec("C_split_C0=0.1_C1=0.03_fixed:0.35", C, "logreg_split", C=0.03, threshold_rule="fixed:0.35",
         extra={"C0": 0.1, "C1": 0.03}),
]
print(f"configurations scored on dev in this sweep: {len(cfgs)}", flush=True)
for sp in cfgs:
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k: round(v["threshold"], 2) for k, v in info.items()}
    print(f"{sp.name:34s} nfeat={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
          f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf} thr={th}", flush=True)
