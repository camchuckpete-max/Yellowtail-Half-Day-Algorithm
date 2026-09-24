# Agent D sweep 2: bait groups on the e007 base (FishDope sentences) and a few variants of the best sweep-1 base
# (eB01 features, monthly refit). 8 configurations. No bootstrap.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import get
B01, E07 = get("eB01_fleet_C003_mccrange"), get("e007_recency_d1_fdsent_C003_p35")
G1 = ["bb_loc_sardine", "bb_loc_mackerel", "bb_loc_short", "bb_sardine_frac_7"]
G3 = ["fo_loc_sardine", "fo_reg_sardine", "fo_reg_squid", "fo_loc_out"]
GI = ["!hd_yt_lastday*bb_loc_sardine", "hd_yt_lastday*bb_loc_sardine", "hd_yt_lastday*bb_loc_short",
      "!hd_yt_lastday*bb_reg_sardine"]
M = dict(retrain="month")
cfgs = {
    "E07y_G1": Spec("E07y_G1", E07.features + G1, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    "E07y_G1+GI": Spec("E07y_G1+GI", E07.features + G1 + GI, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    "E07y_G3": Spec("E07y_G3", E07.features + G3, "logreg", C=0.03, threshold_rule="fixed:0.35"),
    "B01m_mccr_G1": Spec("B01m_mccr_G1", B01.features + G1, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5", **M),
    "B01m_p40_G1+GI_hl730": Spec("B01m_p40_G1+GI_hl730", B01.features + G1 + GI, "logreg", C=0.03,
                                 threshold_rule="fixed:0.4", halflife_days=730, **M),
    "B01m_p40_sard": Spec("B01m_p40_sard", B01.features + ["bb_loc_sardine"], "logreg", C=0.03, threshold_rule="fixed:0.4", **M),
    "B01m_p40_G1+G3": Spec("B01m_p40_G1+G3", B01.features + G1 + G3, "logreg", C=0.03, threshold_rule="fixed:0.4", **M),
    "B01m_p40_G1+GI_C001": Spec("B01m_p40_G1+GI_C001", B01.features + G1 + GI, "logreg", C=0.01, threshold_rule="fixed:0.4", **M),
}
df, _ = dataset.build(); df = evaluate.eligible(df)


def run(name):
    sp = cfgs[name]
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(x["mcc"], 3) for k, x in s["per_fold"].items()}
    return (f"{sp.name:22s} nf={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
            f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"configurations scored: {len(cfgs)}", flush=True)
    with Pool(2) as pool:
        for line in pool.imap(run, list(cfgs)):
            print(line, flush=True)
