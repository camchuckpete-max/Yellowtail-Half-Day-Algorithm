# Agent E sweep 2 (D-E03): trip-model variants with extended boat/pair inputs (tmx), a boosted
# yt model (tmh) and recency-weighted trip training (tmw), each used as the day probability and inside
# the eB01 logistic; plus a B1-split logistic, monthly refit and effort-only additions. 10 configurations.
import sys; sys.path.insert(0, '/home/user/yt-wt-E')
from multiprocessing import Pool
from yt import dataset, evaluate, experiments
from yt.evaluate import Spec

E05 = experiments.get("e005_recency_d1_C001_p35").features
B01 = experiments.get("eB01_fleet_C003_mccrange").features
TM5 = lambda p: [f"{p}_logit", f"{p}_exp", f"{p}_ntrips", f"{p}_pymax", f"{p}_psmax"]
MR = "mcc_range:0.3:0.5"
CFGS = [Spec(f"col_{v}_mccr", [f"{v}_p"], "column", threshold_rule=MR) for v in ("tmx", "tmh", "tmw")]
CFGS += [Spec(f"eB01+TM5({v})", B01 + TM5(v), "logreg", C=0.03, threshold_rule=MR) for v in ("tmx", "tmh", "tmw")]
CFGS += [
    Spec("e005+tmh_logit", E05 + ["tmh_logit"], "logreg", C=0.01, threshold_rule="fixed:0.35"),
    Spec("split_tmh_small", ["hd_yt_lastday", "tmh_logit", "tmh_ntrips", "hd_yt_ewm", "hd_ytdays_7"], "logreg_split",
         C=0.03, threshold_rule=MR),
    Spec("eB01+TMB_monthly_p40", B01 + ["tmb_logit", "tmb_exp", "tmb_ntrips", "tmb_pymax"], "logreg", C=0.03,
         threshold_rule="fixed:0.4", retrain="month"),
    Spec("eB01+effort", B01 + ["tm_ntrips", "hd_trips_dow_4w"], "logreg", C=0.03, threshold_rule=MR),
]
df = None


def run(sp):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(v["mcc"], 3) for k, v in s["per_fold"].items()}
    th = {k: round(v["threshold"], 2) for k, v in info.items() if "-" not in k or k.endswith("-01")}
    m = s["model"]
    return (f"{sp.name:22s} nfeat={len(sp.features):2d} mcc={m['mcc']:.3f} auc={m['auc']:.3f} brier={m['brier']:.4f} "
            f"calls={m['tp'] + m['fp']} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf} thr={th}")


if __name__ == "__main__":
    print(f"# configurations scored on dev in this sweep: {len(CFGS)}", flush=True)
    dataset.build()
    with Pool(2) as pool:
        for line in pool.imap(run, CFGS):
            print(line, flush=True)
