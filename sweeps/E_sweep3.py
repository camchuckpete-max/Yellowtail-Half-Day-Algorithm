# Agent E sweep 3 (D-E04): trip model with each boat's species mix / anglers on its last trip and the
# pair's own last-trip yellowtail (tmz), and the same with weaker L2 (C=1) and daily refit (tmz1).
# 6 configurations, 2 processes.
import sys; sys.path.insert(0, '/home/user/yt-wt-E')
from multiprocessing import Pool
from yt import dataset, evaluate, experiments
from yt.evaluate import Spec

E05 = experiments.get("e005_recency_d1_C001_p35").features
B01 = experiments.get("eB01_fleet_C003_mccrange").features
TM5 = lambda p: [f"{p}_logit", f"{p}_exp", f"{p}_ntrips", f"{p}_pymax", f"{p}_psmax"]
MR = "mcc_range:0.3:0.5"
CFGS = [Spec(f"col_{v}_mccr", [f"{v}_p"], "column", threshold_rule=MR) for v in ("tmz", "tmz1")]
CFGS += [Spec(f"eB01+TM5({v})", B01 + TM5(v), "logreg", C=0.03, threshold_rule=MR) for v in ("tmz", "tmz1")]
CFGS += [
    Spec("e005+tmz_logit", E05 + ["tmz_logit"], "logreg", C=0.01, threshold_rule="fixed:0.35"),
    Spec("calib_tmz_ntrips_b1", ["tmz_logit", "tmz_ntrips", "hd_yt_lastday"], "logreg", C=1.0, threshold_rule=MR),
]
df = None


def run(sp):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k: round(v["threshold"], 2) for k, v in info.items()}
    m = s["model"]
    return (f"{sp.name:22s} nfeat={len(sp.features):2d} mcc={m['mcc']:.3f} auc={m['auc']:.3f} brier={m['brier']:.4f} "
            f"calls={m['tp'] + m['fp']} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf} thr={th}")


if __name__ == "__main__":
    print(f"# configurations scored on dev in this sweep: {len(CFGS)}", flush=True)
    dataset.build()
    with Pool(2) as pool:
        for line in pool.imap(run, CFGS):
            print(line, flush=True)
