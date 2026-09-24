# Agent F diagnostic 1: ceiling of the decision layer. Re-scores two already-counted configurations
# (eB01 spec; F_sweep2 "B01+LATd(py,pi)_C0.03_p40") and reports the MCC an EX-POST (dev-chosen, i.e.
# not legitimate) single threshold and pair of B1-regime thresholds would reach. If even these are
# below the Goal 1 bar, no threshold rule chosen on training data can reach it with these probabilities.
import sys; sys.path.insert(0, '/home/user/yt-wt-F')
import numpy as np
from sklearn.metrics import matthews_corrcoef
from yt import dataset, evaluate, experiments
from yt.evaluate import Spec
from yt.experiments import _R2, _D1, _FLEET
from yt.features import LAT_COLS
df, _ = dataset.build(); df = evaluate.eligible(df)
B01 = _R2 + _D1 + _FLEET
LAT = LAT_COLS + ["hd_trips_dow_4w", "hd_ytrate_60"]
print("configurations scored: 0 new (re-scores eB01_fleet_C003_mccrange and F_sweep2 B01+LATd(py,pi)_C0.03_p40)", flush=True)
for sp in (experiments.get("eB01_fleet_C003_mccrange"),
           Spec("B01+LATd(py,pi)_C0.03_p40", B01 + [c for c in LAT if c not in B01], "latent_logreg", C=0.03,
                threshold_rule="fixed:0.4", extra=dict(logreg_features=B01, lat_out=["py", "pi"], lat_emit="day",
                                                       lat_hot=True, lat_ridge=0.001))):
    p, _ = evaluate.run_spec(df, sp)
    y, pr, b1 = p["y"].to_numpy(), p["prob"].to_numpy(), p["hd_yt_lastday"].to_numpy()
    grid = np.round(np.arange(0.1, 0.9, 0.01), 2)
    one = max((matthews_corrcoef(y, pr >= t), t) for t in grid)
    two = max((matthews_corrcoef(y, pr >= np.where(b1 == 1, t1, t0)), t0, t1) for t0 in grid for t1 in grid)
    print(f"{sp.name}: legit mcc={matthews_corrcoef(y, p['call']):.3f}  ex-post single thr {one[1]} -> {one[0]:.3f}  "
          f"ex-post regime thr (B1=0 {two[1]}, B1=1 {two[2]}) -> {two[0]:.3f}  B1={matthews_corrcoef(y, b1):.3f}", flush=True)
    # Ex-post threshold per fold (year): ceiling for any within-year recalibration of a single threshold.
    calls = np.zeros(len(y), bool)
    for f in p["fold"].unique():
        m = (p["fold"] == f).to_numpy()
        t = max((matthews_corrcoef(y[m], pr[m] >= t), t) for t in grid)[1]
        calls[m] = pr[m] >= t
    print(f"   ex-post threshold per fold (year) -> pooled mcc {matthews_corrcoef(y, calls):.3f}", flush=True)
    for v in (0, 1):
        m = b1 == v
        q = np.quantile(pr[m], [0.1, 0.25, 0.5, 0.75, 0.9])
        bins = np.digitize(pr[m], [0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
        tab = {f"bin{k}": f"{int((bins == k).sum())}:{y[m][bins == k].mean():.2f}" for k in range(7) if (bins == k).any()}
        print(f"   B1={v}: n={m.sum()} y={y[m].mean():.3f} meanp={pr[m].mean():.3f} p-quantiles={np.round(q, 2).tolist()} "
              f"[bins <.2,.2-.3,...,>=.7 -> n:rate] {tab}", flush=True)
