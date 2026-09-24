# Agent F sweep 3: online recalibration from recent out-of-sample labels (D-F04, a latent calibration-drift
# state) on the logistic and on the logistic + latent filter. Usage: F_sweep3.py <part 0|1> (2 processes).
import sys; sys.path.insert(0, '/home/user/yt-wt-F')
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import _R2, _D1, _FLEET
from yt.features import LAT_COLS
df, _ = dataset.build(); df = evaluate.eligible(df)
E5, B01 = _R2 + _D1, _R2 + _D1 + _FLEET
LAT = LAT_COLS + ["hd_trips_dow_4w", "hd_ytrate_60"]
lat = lambda **e: dict(e)
plus = lambda base: base + [c for c in LAT if c not in base]  # no duplicate columns
R = lambda W: {"recal": {"window": W, "k0": 10.0}}
LX = dict(logreg_features=B01, lat_out=["py", "pi"], lat_emit="day", lat_hot=True, lat_ridge=0.001)
cfgs = [
    Spec("B01_C0.03_recal60_mccrange", B01, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5", extra=R(60)),
    Spec("B01_C0.03_recal30_mccrange", B01, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5", extra=R(30)),
    Spec("B01_C0.03_recal90_mccrange", B01, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5", extra=R(90)),
    Spec("B01_C0.03_recal60_p40", B01, "logreg", C=0.03, threshold_rule="fixed:0.4", extra=R(60)),
    Spec("B01_C0.03_recal60_regime", B01, "logreg", C=0.03, threshold_rule="regime_mcc:0.2:0.7", extra=R(60)),
    Spec("E5_C0.01_recal60_p35", E5, "logreg", C=0.01, threshold_rule="fixed:0.35", extra=R(60)),
    Spec("B01+LATd(py,pi)_C0.03_recal60_p40", plus(B01), "latent_logreg", C=0.03, threshold_rule="fixed:0.4",
         extra={**LX, **R(60)}),
]
part = int(sys.argv[1])
mine = cfgs[part::2]
print(f"configurations scored on dev in this sweep: {len(cfgs)} (this part: {len(mine)})", flush=True)
for sp in mine:
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k[:4]: v["threshold"] for k, v in info.items()}
    cal = {f: f"{g['prob'].mean():.3f}/{g['y'].mean():.3f}" for f, g in p.groupby("fold")}
    nlat = sum(c.startswith("lat_") for c in sp.features) + (sp.model == "latent") * 2
    print(f"{sp.name:32s} nfeat={len(sp.features) - nlat:2d}+{'LAT' if nlat else '-'} mcc={s['model']['mcc']:.3f} "
          f"auc={s['model']['auc']:.3f} brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} "
          f"folds={pf} thr={th} meanp/y={cal} "
          f"diff_calls_vs_B1={int((p['call'] != p['hd_yt_lastday']).sum())}", flush=True)
