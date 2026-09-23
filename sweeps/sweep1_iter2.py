# Exploratory sweep (not saved as runs). Output is copied into the repo's sweeps/ folder for audit.
import sys; sys.path.insert(0,'/home/user/yellowtail-half-day-algorithm')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.features import FEATURES
df,_=dataset.build(); df=evaluate.eligible(df)
R=["hd_yt_d1","hd_yt_lastday","hd_ytdays_3","hd_ytdays_7","hd_ytdays_30","hd_days_since_yt","clim_rate","doy_sin","doy_cos"]
D1=["hd_yt_trip_frac_d1","hd_log_ytfish_d1","hd_yt_landings_d1","hd_yt_d2","tq_yt_d1","hd_yt_streak"]
NEW=["hd_yt_am_d1","hd_yt_pm_d1","hd_yt_boats_3","hd_yt_boats_7","hd_yt_seaforth_3","hd_yt_fishermans_3","hd_yt_hm_3","hd_yt_point_loma_3"]
INT=["hd_yt_lastday*clim_rate","hd_yt_lastday*hd_log_ytfish_d1","!hd_yt_lastday*hd_ytdays_7","!hd_yt_lastday*hd_yt_d2","hd_yt_lastday*doy_cos","!hd_yt_lastday*clim_rate"]
sets={"R":R,"R+D1":R+D1,"R+D1+NEW":R+D1+NEW,"R+D1+INT":R+D1+INT,"R+D1+NEW+INT":R+D1+NEW+INT,"ALL+INT":list(FEATURES)+INT}
for name,fs in sets.items():
  for C in (0.03,0.3,1.0):
    for thr in ("fixed:0.35","fixed:0.4","fixed:0.45","fixed:0.5","mcc"):
      sp=Spec(f"{name}_C{C}_{thr}",fs,"logreg",C=C,threshold_rule=thr)
      p,_=evaluate.run_spec(df,sp); s=evaluate.summarize(p)
      print(f"{sp.name:40s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} acc={s['model']['accuracy']:.3f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} ci=[{s['mcc_diff_vs_best_baseline']['lo95']:.3f},{s['mcc_diff_vs_best_baseline']['hi95']:.3f}]", flush=True)
