# Agent B sweep 3: compact catch-history extension (C), combination with existing sentence-level
# FishDope features (FS/FSI, from e007), and threshold rules fixed:0.3 / mcc_range:0.3:0.5.
import sys; sys.path.insert(0, '/home/user/yt-wt-B')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
X = ["bt_hot_last", "bt_hot_sailed_d1", "hd_yt_trips_d1", "hd_yt_ewm", "tq_yt_trip_frac_3", "tq_yt_trip_frac_30",
     "hd_ytrate_60", "d1_surface_frac", "hd_surface_frac_7"]
XC = ["hd_yt_ewm", "tq_yt_trip_frac_3", "tq_yt_trip_frac_30", "hd_ytrate_60", "bt_hot_last"]
FS = ["fd_local_catch_d1", "fd_local_sight_d1", "fd_local_neg_d1", "fd_coronado_catch_d1", "fd_north_catch_d1",
      "fd_local_catch_3", "fd_local_catchdays_3", "fd_local_sight_3", "fd_coronado_catch_3"]
FSI = ["hd_yt_lastday*fd_local_catch_3", "!hd_yt_lastday*fd_local_catch_3", "hd_yt_lastday*fd_local_neg_d1",
       "!hd_yt_lastday*fd_coronado_catch_d1"]
B, C = R + D1 + X, R + D1 + XC
MR = "mcc_range:0.3:0.5"
cfgs = [
    Spec("C_logreg_C0.03_fixed:0.35", C, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    Spec("C_logreg_C0.03_mccrange", C, "logreg", C=0.03, threshold_rule=MR),
    Spec("C_logreg_C0.01_fixed:0.35", C, "logreg", C=0.01, threshold_rule="fixed:0.35"),
    Spec("C_logreg_C0.01_mccrange", C, "logreg", C=0.01, threshold_rule=MR),
    Spec("C_logreg_C0.03_fixed:0.3", C, "logreg", C=0.03, threshold_rule="fixed:0.3"),
    Spec("B_logreg_C0.03_fixed:0.3", B, "logreg", C=0.03, threshold_rule="fixed:0.3"),
    Spec("B+FS+FSI_logreg_C0.03_fixed:0.35", B + FS + FSI, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    Spec("B+FS+FSI_logreg_C0.03_mccrange", B + FS + FSI, "logreg", C=0.03, threshold_rule=MR),
    Spec("C+FS+FSI_logreg_C0.03_fixed:0.35", C + FS + FSI, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    Spec("C+FS+FSI_logreg_C0.03_mccrange", C + FS + FSI, "logreg", C=0.03, threshold_rule=MR),
    Spec("e007set_logreg_C0.03_mccrange", R + D1 + FS + FSI, "logreg", C=0.03, threshold_rule=MR),
]
print(f"configurations scored on dev in this sweep: {len(cfgs)}", flush=True)
for sp in cfgs:
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k: round(v["threshold"], 2) for k, v in info.items()}
    print(f"{sp.name:34s} nfeat={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
          f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf} thr={th}", flush=True)
