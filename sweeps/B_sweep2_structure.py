# Agent B sweep 2: model structure (regime-split logistic, monotone HGB, logistic+HGB ensemble,
# bounded inner-OOF threshold) on the e005 set (A) and an EDA-chosen catch-history extension (B).
import sys; sys.path.insert(0, '/home/user/yt-wt-B')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
X = ["bt_hot_last", "bt_hot_sailed_d1", "hd_yt_trips_d1", "hd_yt_ewm", "tq_yt_trip_frac_3", "tq_yt_trip_frac_30",
     "hd_ytrate_60", "d1_surface_frac", "hd_surface_frac_7"]
A, B = R + D1, R + D1 + X
MONO = {f: 1 for f in B}
MONO.update({"doy_sin": 0, "doy_cos": 0, "hd_days_since_yt": -1})
HGB = {"max_depth": 2, "learning_rate": 0.05, "max_iter": 150, "l2_regularization": 5.0, "min_samples_leaf": 40}
cfgs = []
for thr in ("fixed:0.35", "fixed:0.4"):
    cfgs.append(Spec(f"B_logreg_C0.03_{thr}", B, "logreg", C=0.03, threshold_rule=thr))
    for nm, fs in (("A", A), ("B", B)):
        cfgs.append(Spec(f"{nm}_split_C0.03_{thr}", fs, "logreg_split", C=0.03, threshold_rule=thr))
    cfgs.append(Spec(f"B_split_C0.1_{thr}", B, "logreg_split", C=0.1, threshold_rule=thr))
    for nm, fs in (("A", A), ("B", B)):
        cfgs.append(Spec(f"{nm}_hgbmono_{thr}", fs, "hgb", threshold_rule=thr, extra={"hgb": HGB, "monotone": MONO}))
        cfgs.append(Spec(f"{nm}_ens_C0.03_{thr}", fs, "ens", C=0.03, threshold_rule=thr, extra={"hgb": HGB, "monotone": MONO}))
cfgs.append(Spec("B_logreg_C0.03_mccrange", B, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5"))
cfgs.append(Spec("B_ens_C0.03_mccrange", B, "ens", C=0.03, threshold_rule="mcc_range:0.3:0.5", extra={"hgb": HGB, "monotone": MONO}))
print(f"configurations scored on dev in this sweep: {len(cfgs)}", flush=True)
for sp in cfgs:
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k: round(v["threshold"], 2) for k, v in info.items()}
    print(f"{sp.name:30s} nfeat={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
          f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf} thr={th}", flush=True)
