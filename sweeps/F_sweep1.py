# Agent F sweep 1: latent-state filter (D-F01) alone and stacked under the logistic, and the
# regime-dependent two-threshold decision rule (D-F02). Usage: F_sweep1.py <part 0|1> (2 processes).
import sys; sys.path.insert(0, '/home/user/yt-wt-F')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import _R2, _D1, _FLEET
from yt.features import LAT_COLS
df, _ = dataset.build(); df = evaluate.eligible(df)
E5, B01 = _R2 + _D1, _R2 + _D1 + _FLEET
LAT = LAT_COLS + ["hd_trips_dow_4w"]
lat = lambda **e: dict(e)
cfgs = [
    Spec("LAT_all_mccrange", LAT, "latent", threshold_rule="mcc_range:0.3:0.5"),
    Spec("LAT_nofd_mccrange", LAT, "latent", threshold_rule="mcc_range:0.3:0.5", extra=lat(lat_fd=False)),
    Spec("LAT_all_regime", LAT, "latent", threshold_rule="regime_mcc:0.2:0.7"),
    Spec("LAT_all_monthly_mccrange", LAT, "latent", threshold_rule="mcc_range:0.3:0.5", retrain="month"),
    Spec("E5+LAT_C0.03_mccrange", E5 + LAT, "latent_logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5",
         extra=lat(logreg_features=E5)),
    Spec("B01+LAT_C0.03_mccrange", B01 + LAT, "latent_logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5",
         extra=lat(logreg_features=B01)),
    Spec("B01+LAT_C0.03_regime", B01 + LAT, "latent_logreg", C=0.03, threshold_rule="regime_mcc:0.2:0.7",
         extra=lat(logreg_features=B01)),
    Spec("B01_C0.03_regime", B01, "logreg", C=0.03, threshold_rule="regime_mcc:0.2:0.7"),
    Spec("B01+LAT_C0.03_monthly_mccrange", B01 + LAT, "latent_logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5",
         retrain="month", extra=lat(logreg_features=B01)),
]
part = int(sys.argv[1])
mine = cfgs[part::2]
print(f"configurations scored on dev in this sweep: {len(cfgs)} (this part: {len(mine)})", flush=True)
for sp in mine:
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k[:4]: v["threshold"] for k, v in info.items()}
    cal = {f: f"{g['prob'].mean():.3f}/{g['y'].mean():.3f}" for f, g in p.groupby("fold")}
    nlat = sum(c.startswith("lat_") for c in sp.features)
    print(f"{sp.name:32s} nfeat={len(sp.features) - nlat:2d}+{'LAT' if nlat else '-'} mcc={s['model']['mcc']:.3f} "
          f"auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} "
          f"folds={pf} thr={th} meanp/y={cal} "
          f"diff_calls_vs_B1={int((p['call'] != p['hd_yt_lastday']).sum())}", flush=True)
