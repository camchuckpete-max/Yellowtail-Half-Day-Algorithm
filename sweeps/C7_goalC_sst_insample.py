# Goal C sweep 7 (D-035): same SST sets, threshold chosen on in-sample training predictions
# (insample_mcc_range:0.1:0.5), so the 2021 fold (one training year) gets a real threshold.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
SETS = {"sst": ["sst_sd_last"],
        "sst+grad+chl": ["sst_sd_last", "sst_offshore_grad", "chl_sd_last"],
        "S0+sst+grad": ["doy_sin", "doy_cos", "sst_sd_last", "sst_offshore_grad"],
        "S0": ["doy_sin", "doy_cos"]}
CONFIGS = [(k, C) for k in SETS for C in (0.03, 1.0)]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, C = cfg
    sp = Spec(f"C_sst_{k}_C{C}_insample", SETS[k], "logreg", C=C, threshold_rule="insample_mcc_range:0.1:0.5",
              inputs="conditions", dev_years=(2021, 2022, 2023), train_start="2020-01-01")
    p, info = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    th = {f: round(v["threshold"], 2) for f, v in info.items()}
    return (f"{sp.name:32s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.4f} brier={s['model']['brier']:.4f} "
            f"prec={s['model']['precision']:.3f} rec={s['model']['recall']:.3f} thr={th} folds={pf}")


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()
    with Pool(4) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
