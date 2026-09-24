# Goal C sweep 2 (D-032): one-at-a-time screen. S0 (doy_sin, doy_cos) + one conditions feature,
# logistic C=1, threshold mcc_range 0.2-0.5. Reports dAUC / dBrier vs S0 alone. Dev 2012-2016.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate, features
from yt.evaluate import Spec

S0 = ["doy_sin", "doy_cos"]
CANDS = [f for f in features.FEATURES if f.startswith(features.CONDITIONS_PREFIXES)
         and not f.startswith(features.FORBIDDEN_PREFIXES) and f not in S0]
df = None


def run(extra):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    fs = S0 + ([extra] if extra else [])
    sp = Spec(f"S0+{extra or '-'}", fs, "logreg", C=1.0, threshold_rule="mcc_range:0.2:0.5", inputs="conditions")
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    return extra, s["model"]["auc"], s["model"]["brier"], s["model"]["mcc"], {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CANDS) + 1}", flush=True)
    dataset.build()
    with Pool(4) as pool:
        res = pool.map(run, [None] + CANDS)
    base = res[0]
    print(f"S0 alone: auc={base[1]:.4f} brier={base[2]:.4f} mcc={base[3]:.3f} folds={base[4]}")
    for extra, auc, br, mcc, pf in sorted(res[1:], key=lambda r: -r[1]):
        print(f"{extra:24s} dAUC={auc - base[1]:+.4f} dBrier={br - base[2]:+.4f} auc={auc:.4f} mcc={mcc:.3f} folds={pf}")
