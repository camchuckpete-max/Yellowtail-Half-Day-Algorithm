# Agent B sweep 1: catch-history feature groups (D-B02) on top of the e005 set, logistic C=0.03.
# No bootstrap; configurations are counted in the first output line.
import sys; sys.path.insert(0, '/home/user/yt-wt-B')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
BT = ["bt_hot_last", "bt_hot_any3", "bt_hot_sailed_d1", "bt_yt_boats_d1", "hd_yt_trips_d1", "hd_yt_tw_d2"]
SP = ["d1_surface_frac", "d1_bottom_only_frac", "hd_surface_frac_7", "d1_bonito_per_trip", "d1_barracuda_per_trip",
      "d1_calico_per_trip", "d1_mackerel_per_trip"]
OF = ["tq_log_yt_d1", "tq_yt_trip_frac_3", "ov_log_yt_3", "tq_log_yt_trend", "tq_log_yt_7", "ov_log_yt_7"]
EW = ["hd_yt_ewm", "hd_trips_dow_4w", "hd_cov_d1"]
sets = {"R+D1+BT": R + D1 + BT, "R+D1+SP": R + D1 + SP, "R+D1+OF": R + D1 + OF, "R+D1+EW": R + D1 + EW,
        "R+D1+NEW": R + D1 + BT + SP + OF + EW}
cfgs = [Spec("ref_e005", R + D1, "logreg", C=0.01, threshold_rule="fixed:0.35")]
for name, fs in sets.items():
    for thr in ("fixed:0.35", "fixed:0.4"):
        cfgs.append(Spec(f"{name}_C0.03_{thr}", fs, "logreg", C=0.03, threshold_rule=thr))
cfgs.append(Spec("R+D1+NEW_C0.01_fixed:0.35", R + D1 + BT + SP + OF + EW, "logreg", C=0.01, threshold_rule="fixed:0.35"))
cfgs.append(Spec("R+D1+NEW_C0.01_fixed:0.4", R + D1 + BT + SP + OF + EW, "logreg", C=0.01, threshold_rule="fixed:0.4"))
print(f"configurations scored on dev in this sweep: {len(cfgs)}", flush=True)
for sp in cfgs:
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    print(f"{sp.name:30s} nfeat={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
          f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}", flush=True)
