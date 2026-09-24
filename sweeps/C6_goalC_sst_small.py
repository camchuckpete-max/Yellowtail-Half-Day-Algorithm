# Goal C sweep 6 (D-035): small SST-centred conditions models; train from 2020, dev folds 2021-2023,
# yearly-frozen. Monotone HGB encodes "warmer coast = more likely", "coast warmer than offshore = more likely".
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
SETS = {"sst": ["sst_sd_last"],
        "sst+grad": ["sst_sd_last", "sst_offshore_grad"],
        "sst+grad+chl": ["sst_sd_last", "sst_offshore_grad", "chl_sd_last"],
        "tmax+grad": ["sst_tiles_max", "sst_offshore_grad"],
        "sst+sst7+grad": ["sst_sd_last", "sst_sd_7", "sst_offshore_grad"],
        "S0+sst+grad": ["doy_sin", "doy_cos", "sst_sd_last", "sst_offshore_grad"]}
CONFIGS = [(k, "logreg", C, thr) for k in SETS for C in (0.03, 1.0) for thr in ("mcc_range:0.2:0.5",)]
CONFIGS += [("sst+grad", "hgb_mono", 1.0, "mcc_range:0.2:0.5"), ("sst+grad+chl", "hgb_mono", 1.0, "mcc_range:0.2:0.5")]
MONO = {"sst_sd_last": 1, "sst_tiles_max": 1, "sst_sd_7": 1, "sst_offshore_grad": -1, "chl_sd_last": -1}
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, model, C, thr = cfg
    extra = {}
    if model == "hgb_mono":
        model, extra = "hgb", {"monotone": MONO, "hgb": {"max_depth": 2, "max_iter": 100}}
    sp = Spec(f"C_sst_{k}_{cfg[1]}_C{C}", SETS[k], model, C=C, threshold_rule=thr, extra=extra,
              inputs="conditions", dev_years=(2021, 2022, 2023), train_start="2020-01-01")
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:34s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.4f} brier={s['model']['brier']:.4f} "
            f"prec={s['model']['precision']:.3f} rec={s['model']['recall']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()
    with Pool(4) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
