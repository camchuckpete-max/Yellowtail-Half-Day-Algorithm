# Agent A: bootstrap (D-009) for the single best agent-A configuration from A_sweep1.
# Configurations scored on dev in this script: 1 (re-score of R+D1+V2_C0.03_fixed:0.4 from A_sweep1).
import sys, json; sys.path.insert(0, '.')
from yt import dataset, evaluate
from yt.evaluate import Spec
df, _ = dataset.build(); df = evaluate.eligible(df)
R = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt", "clim_rate", "doy_sin", "doy_cos"]
D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
V2 = ["fd2_local_catch_d1", "fd2_local_neg_d1", "fd2_local_present_d1", "fd2_local_catchdays_3", "fd2_local_presdays_3",
      "fd2_local_catch_priv_3", "fd2_local_catch_boat_3", "fd2_local_net_d1", "fd2_coronado_catch_d1",
      "fd2_local_catchdays_7", "fd2_local_days_since_catch"]
print("# configurations scored: 1")
sp = Spec("R+D1+V2_C0.03_fixed:0.4", R + D1 + V2, "logreg", C=0.03, threshold_rule="fixed:0.4")
p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=True)
print(sp.name, json.dumps({"mcc": s["model"]["mcc"], "auc": s["model"]["auc"],
                           "per_fold": {k: v["mcc"] for k, v in s["per_fold"].items()},
                           "best_baseline": s["best_baseline"], "B1": s["baselines"]["B1_yesterday"]["mcc"],
                           "diff_ci": s["mcc_diff_vs_best_baseline"]}, indent=1))
