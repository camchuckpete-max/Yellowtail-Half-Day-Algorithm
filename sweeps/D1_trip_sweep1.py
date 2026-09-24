# Goal D sweep 1 (D-039): per-trip, New Seaforth + Sea Watch, conditions only. Dev years only.
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import trips
df, man = trips.build()
T0 = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2"]
MOONTIDE = ["moon_illum", "moon_sin", "moon_cos", "tide_range_d", "tide_high_d", "tide_low_d", "tide_range_chg"]
DAY = ["fc_wind_kt", "fc_swell_ft", "fc_swell_s", "cd_upw_d", "cd_swell_south_d", "mf_wind_max", "mf_gust",
       "mf_seas", "mf_wind_offshore", "mf_wind_south", "mf_swell_south", "mf_swell_west"]
HIST = ["cd_upw_14", "cd_upw_30_anom", "cd_sws_90_anom", "cd_wind_7", "cd_swell_7", "cd_seas_3"]
SST = ["sst_sd_last", "sst_sd_7", "sst_south_minus_north", "chl_sd_last"]
runs = [("T0", T0, range(2012, 2024), None), ("T0+moon/tide", T0 + MOONTIDE, range(2012, 2024), None),
        ("T0+day fcst", T0 + DAY, range(2012, 2024), None), ("T0+hist", T0 + HIST, range(2012, 2024), None),
        ("T0 [sst era]", T0, (2021, 2022, 2023), "2020-01-01"),
        ("T0+sst1 [sst era]", T0 + ["sst_sd_last"], (2021, 2022, 2023), "2020-01-01"),
        ("T0+sst+ [sst era]", T0 + SST, (2021, 2022, 2023), "2020-01-01"),
        ("T0+sst1+day [sst era]", T0 + ["sst_sd_last"] + DAY, (2021, 2022, 2023), "2020-01-01")]
print(f"# Goal D configurations scored on dev: {len(runs) * 2}; source {man['source_commit'][:7]}")
best = None
for name, feats, years, ts in runs:
    for C in (0.1, 1.0):
        p = trips.walk_forward(df, feats, years, C=C, train_start=ts)
        s = trips.summary(p)
        print(f"{name:24s} C={C:<4} trips={s['trips']} base={s['base_rate']:.3f} AUC={s['auc']:.3f} "
              f"Brier={s['brier']:.4f} folds={s['per_fold_auc']}", flush=True)
        if name == "T0+sst1 [sst era]" and C == 1.0:
            best = p
print("\nBand table, T0+sst1 [sst era] C=1 (held-out folds 2021-2023):")
print(trips.band_table(best).to_string(index=False))
