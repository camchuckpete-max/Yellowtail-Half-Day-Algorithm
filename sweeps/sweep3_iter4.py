# Iter 4 sweep: sentence-level FishDope evidence (D-022). No bootstrap; finalists get named specs.
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
sets = {"R+D1": R + D1, "R+D1+FS": R + D1 + FS, "R+D1+FS+FSI": R + D1 + FS + FSI}
for name, fs in sets.items():
    for C in (0.01, 0.03, 0.1):
        for thr in ("fixed:0.35", "fixed:0.4", "fixed:0.45", "mcc"):
            sp = Spec(f"{name}_C{C}_{thr}", fs, "logreg", C=C, threshold_rule=thr)
            p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
            pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
            print(f"{sp.name:30s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} "
                  f"B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
