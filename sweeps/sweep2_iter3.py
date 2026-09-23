# Iter 3 exploratory sweep: FishDope features added (D-020). No bootstrap (speed); finalists are
# promoted to named specs and run with the full bootstrap.
import sys; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.features import FEATURES
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
FD = ["fd_visible_d1", "fd_yt_local_d1", "fd_yt_coronado_d1", "fd_yt_north_d1", "fd_yt_all_d1",
      "fd_yt_local_3", "fd_yt_local_days_3", "fd_yt_local_prev4_7", "fd_yt_coronado_3"]
FDI = ["hd_yt_lastday*fd_yt_local_d1", "!hd_yt_lastday*fd_yt_local_d1", "hd_yt_lastday*fd_yt_local_3", "!hd_yt_lastday*fd_yt_coronado_d1"]
sets = {"R+D1": R + D1, "R+D1+FD": R + D1 + FD, "R+D1+FD+FDI": R + D1 + FD + FDI, "R+FD": R + FD, "ALL": list(FEATURES)}
for name, fs in sets.items():
    for C in (0.01, 0.03, 0.1):
        for thr in ("fixed:0.35", "fixed:0.4", "fixed:0.45", "fixed:0.5", "mcc"):
            sp = Spec(f"{name}_C{C}_{thr}", fs, "logreg", C=C, threshold_rule=thr)
            p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
            pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
            print(f"{sp.name:32s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} acc={s['model']['accuracy']:.3f} "
                  f"B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
