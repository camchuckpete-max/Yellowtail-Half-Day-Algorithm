# Agent E sweep 1 (D-E01/D-E02): trip-level model outputs (walk-forward inside the feature) used
# (a) directly as the day probability ("column" model) and (b) as extra inputs to the day-level logistic.
# tm = trip model without boat identity, tmb = with main-boat one-hots. 12 configurations, 2 processes.
import sys; sys.path.insert(0, '/home/user/yt-wt-E')
from multiprocessing import Pool
from yt import dataset, evaluate, experiments
from yt.evaluate import Spec

E05 = experiments.get("e005_recency_d1_C001_p35").features
B01 = experiments.get("eB01_fleet_C003_mccrange").features
TM = lambda p: [f"{p}_logit", f"{p}_exp", f"{p}_ntrips", f"{p}_pymax"]
CFGS = [
    Spec("col_tm_mccr", ["tm_p"], "column", threshold_rule="mcc_range:0.3:0.5"),
    Spec("col_tmb_mccr", ["tmb_p"], "column", threshold_rule="mcc_range:0.3:0.5"),
    Spec("col_tm_mccr2", ["tm_p"], "column", threshold_rule="mcc_range:0.2:0.6"),
    Spec("lr_tmlogit_b1_C003", ["tm_logit", "hd_yt_lastday"], "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5"),
    Spec("e005+tm_logit", E05 + ["tm_logit"], "logreg", C=0.01, threshold_rule="fixed:0.35"),
    Spec("e005+tmb_logit", E05 + ["tmb_logit"], "logreg", C=0.01, threshold_rule="fixed:0.35"),
    Spec("eB01+tm_logit", B01 + ["tm_logit"], "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5"),
    Spec("eB01+tmb_logit", B01 + ["tmb_logit"], "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5"),
    Spec("eB01+TM", B01 + TM("tm"), "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5"),
    Spec("eB01+TMB", B01 + TM("tmb"), "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5"),
    Spec("e005+TM_p40", E05 + TM("tm"), "logreg", C=0.01, threshold_rule="fixed:0.4"),
    Spec("small_TM_b1_ewm", TM("tm") + ["hd_yt_lastday", "hd_yt_ewm"], "logreg", C=0.03,
         threshold_rule="mcc_range:0.3:0.5"),
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
