# Agent B sweep 5: probability average of two separately regularized logistic fits:
# compact catch-history set (C) and the e007 set (catch history + sentence-level FishDope).
import sys; sys.path.insert(0, '/home/user/yt-wt-B')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
XC = ["hd_yt_ewm", "tq_yt_trip_frac_3", "tq_yt_trip_frac_30", "hd_ytrate_60", "bt_hot_last"]
FS = ["fd_local_catch_d1", "fd_local_sight_d1", "fd_local_neg_d1", "fd_coronado_catch_d1", "fd_north_catch_d1",
      "fd_local_catch_3", "fd_local_catchdays_3", "fd_local_sight_3", "fd_coronado_catch_3"]
FSI = ["hd_yt_lastday*fd_local_catch_3", "!hd_yt_lastday*fd_local_catch_3", "hd_yt_lastday*fd_local_neg_d1",
       "!hd_yt_lastday*fd_coronado_catch_d1"]
C, E7 = R + D1 + XC, R + D1 + FS + FSI
U = list(dict.fromkeys(C + E7))
cfgs = [Spec(f"avg(C,E7)_C0.03_{t}", U, "avg_subsets", C=0.03, threshold_rule=t, extra={"subsets": [C, E7]})
        for t in ("fixed:0.35", "fixed:0.4")]
print(f"configurations scored on dev in this sweep: {len(cfgs)}", flush=True)
for sp in cfgs:
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k: round(v["threshold"], 2) for k, v in info.items()}
    print(f"{sp.name:34s} nfeat={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
          f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf} thr={th}", flush=True)
