# Goal C sweep 9 (D-036): spatial SST contrast. Train from 2020, dev folds 2021-2023, yearly-frozen,
# in-sample threshold (D-035). Pre-declared 6 configurations.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
SETS = {"sst": ["sst_sd_last"],
        "sst+s-n": ["sst_sd_last", "sst_south_minus_north"],
        "sst+s-n+ge68": ["sst_sd_last", "sst_south_minus_north", "sst_tiles_ge68"]}
CONFIGS = [(k, C) for k in SETS for C in (0.03, 1.0)]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, C = cfg
    sp = Spec(f"C_sp_{k}_C{C}", SETS[k], "logreg", C=C, threshold_rule="insample_mcc_range:0.1:0.5",
              inputs="conditions", dev_years=(2021, 2022, 2023), train_start="2020-01-01")
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:28s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.4f} brier={s['model']['brier']:.4f} "
            f"prec={s['model']['precision']:.3f} rec={s['model']['recall']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()
    with Pool(3) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
