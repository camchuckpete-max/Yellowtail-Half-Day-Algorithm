# Goal C sweep 4 (D-034): SST-era conditions-only models. Train from 2020-01-01, dev folds
# 2021-2023 (D-033), yearly-frozen models (D-032 purity rule). Benchmark: season-only S0.
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
from yt import dataset, evaluate
from yt.evaluate import Spec
S0 = ["doy_sin", "doy_cos"]
SST1 = ["sst_sd_last"]
SST = ["sst_sd_last", "sst_sd_7", "sst_sd_trend7", "sst_sd_max30"]
SSTX = SST + ["sst_cor_last", "sst_nine_last", "sst_offshore_grad", "sst_warm_frac", "sst_tiles_max"]
OCN = SSTX + ["chl_sd_last", "cur_sd_speed_3", "cur_sd_north_3"]
FCST = ["cd_sws_90_anom", "cd_upw_30_anom", "cd_seas_3", "cd_upw_14", "mf_swell_south", "fc_wind_kt"]
SETS = {"S0": S0, "SST1": SST1, "S0+SST1": S0 + SST1, "S0+SST": S0 + SST, "S0+SSTX": S0 + SSTX,
        "S0+OCN": S0 + OCN, "S0+OCN+FCST": S0 + OCN + FCST}
CONFIGS = [(k, "logreg", C) for k in SETS for C in (0.1, 1.0)] + [("S0+OCN+FCST", "hgb", 1.0)]
df = None


def run(cfg):
    global df
    if df is None:
        d, _ = dataset.build(); df = evaluate.eligible(d)
    k, model, C = cfg
    sp = Spec(f"C_sst_{k}_{model}_C{C}", SETS[k], model, C=C, threshold_rule="mcc_range:0.2:0.5",
              inputs="conditions", dev_years=(2021, 2022, 2023), train_start="2020-01-01")
    p, _ = evaluate.run_spec(df, sp); s = evaluate.summarize(p, bootstrap=False)
    pf = {f: round(v["mcc"], 3) for f, v in s["per_fold"].items()}
    return (f"{sp.name:36s} mcc={s['model']['mcc']:.3f} auc={s['model']['auc']:.4f} brier={s['model']['brier']:.4f} "
            f"acc={s['model']['accuracy']:.3f} B1={s['baselines']['B1_yesterday']['mcc']:.3f} "
            f"base_rate={s['model']['base_rate']:.3f} folds={pf}")


if __name__ == "__main__":
    print(f"# Goal C configurations scored on dev: {len(CONFIGS)}", flush=True)
    dataset.build()
    with Pool(4) as pool:
        for line in pool.imap(run, CONFIGS):
            print(line, flush=True)
