# Goal D sweep 2 (D-041): per-trip New Seaforth + Sea Watch, trip-window conditions from requests
# 0001-0003 (pier/buoy water temp, tide during the trip, upwelling, climate indices). Dev folds
# 2012-2023 only (holdout >= 2024 untouched). P = predictive (21:00 PT D-1); E = explanatory.
import sys; sys.path.insert(0, '.')
from yt import trips, hourly
df, man = trips.build()
T0 = trips.TRIP_FEATURES + ["doy_sin", "doy_cos", "doy_sin2", "doy_cos2"]
PIER = ["hc_pier_wtmp_24h", "hc_pier_wtmp_chg3d", "hc_pier_wtmp_7d", "hc_pier_air_minus_water_24h"]
TIDE = ["hc_tide_start", "hc_tide_change", "hc_tide_range", "hc_tide_maxrate", "hc_tide_turns"]
BUOY = ["hc_btp_wtmp_24h", "hc_bpl_wtmp_24h", "hc_btp_wvht_24h", "hc_bpl_wvht_24h", "hc_btp_dpd_24h"]
UPW = ["hc_cuti33_7", "hc_cuti33_30", "hc_beuti33_30"]
CI = ["hc_ci_oni", "hc_ci_pdo", "hc_ci_npgo", "hc_ci_mei_v2"]
ALLP = PIER + TIDE + BUOY + UPW + CI + ["hc_ljpc1_wspd_24h"]
runs = [("T0", T0, "P"), ("T0+pier", T0 + PIER, "P"), ("T0+tide", T0 + TIDE, "P"), ("T0+buoy", T0 + BUOY, "P"),
        ("T0+upw", T0 + UPW, "P"), ("T0+climate", T0 + CI, "P"), ("T0+pier+climate", T0 + PIER + CI, "P"),
        ("T0+allP", T0 + ALLP, "P"), ("E: T0+allP+EX", T0 + ALLP + hourly.EX_FEATURES, "E")]
print(f"# Goal D configurations scored on dev: {len(runs) * 2}; source {man['source_commit'][:7]}; trips {len(df)}")
keep = {}
for name, feats, track in runs:
    for C in (0.1, 1.0):
        p = trips.walk_forward(df, feats, range(2012, 2024), C=C, track=track)
        s = trips.summary(p)
        print(f"{name:18s} [{track}] C={C:<4} AUC={s['auc']:.3f} Brier={s['brier']:.4f} base={s['base_rate']:.3f} "
              f"folds={s['per_fold_auc']}", flush=True)
        keep[(name, C)] = p
for key in (("T0", 1.0), ("T0+pier+climate", 0.1), ("T0+allP", 0.1), ("E: T0+allP+EX", 0.1)):
    print(f"\nBand table {key} (held-out years 2012-2023):")
    print(trips.band_table(keep[key]).to_string(index=False))
