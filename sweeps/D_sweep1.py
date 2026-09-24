# Agent D sweep 1: bait-barge groups added to the two best dev specs (eB01 yearly mcc_range, e009 monthly p40).
# 2 bases x 6 feature variants = 12 configurations. No bootstrap.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
from yt.experiments import get
B01 = get("eB01_fleet_C003_mccrange")
G1 = ["bb_loc_sardine", "bb_loc_mackerel", "bb_loc_short", "bb_sardine_frac_7"]
G2 = G1 + ["bb_loc_anchovy", "bb_sd_sardine", "bb_reg_squid", "bb_sardine_in_c", "bb_stale", "bb_reg_sardine",
           "bb_sardine_change"]
G3 = ["fo_loc_sardine", "fo_reg_sardine", "fo_reg_squid", "fo_loc_out"]
GI = ["!hd_yt_lastday*bb_loc_sardine", "hd_yt_lastday*bb_loc_sardine", "hd_yt_lastday*bb_loc_short",
      "!hd_yt_lastday*bb_reg_sardine"]
variants = {"ctrl": [], "G1": G1, "G2": G2, "G3": G3, "G2+G3": G2 + G3, "G1+GI": G1 + GI}
bases = {"B01y": dict(threshold_rule=B01.threshold_rule, retrain="year"),
         "B01m_p40": dict(threshold_rule="fixed:0.4", retrain="month")}
cfgs = [(b, v) for b in bases for v in variants]
df, _ = dataset.build(); df = evaluate.eligible(df)


def run(cfg):
    b, v = cfg
    sp = Spec(f"{b}_{v}", B01.features + variants[v], "logreg", C=B01.C, **bases[b])
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {k: round(x["mcc"], 3) for k, x in s["per_fold"].items()}
    return (f"{sp.name:20s} nf={len(sp.features):2d} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.3f} "
            f"brier={s['model']['brier']:.4f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"configurations scored: {len(cfgs)}", flush=True)
    with Pool(2) as pool:
        for line in pool.imap(run, cfgs):
            print(line, flush=True)
