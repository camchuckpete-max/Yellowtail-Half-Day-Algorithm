"""Named experiment specs. Every run references one of these by name, so the
exact feature list / model / threshold rule of any logged run is in git.
Never edit a spec after it has been run: add a new name instead."""
from __future__ import annotations

from .evaluate import Spec

# Frozen, literal copy of the 41-feature list used by iteration-1 specs (D-017, fixed in
# D-024: this was previously derived from the live FEATURES list and silently grew).
_ALL_V1 = [
    "hd_yt_d1", "hd_cov_d1", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_14", "hd_ytdays_30",
    "hd_covdays_7", "hd_covdays_30", "hd_ytrate_7", "hd_ytrate_30", "hd_ytdays_prev7",
    "hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak",
    "hd_ntrips_7", "hd_ytfish_per_trip_7", "hd_log_ytfish_7", "hd_bonito_per_trip_7",
    "hd_barracuda_per_trip_7", "hd_calico_per_trip_7", "hd_rockfish_per_trip_7", "hd_days_since_yt",
    "oth_ntrips_7", "oth_yt_per_trip_7", "oth_log_yt_3", "oth_log_yt_7", "tq_log_yt_7", "ov_log_yt_7",
    "clim_rate", "doy_sin", "doy_cos", "weekend", "moon_illum", "moon_sin", "moon_cos",
    "fc_wind_kt", "fc_swell_ft", "fc_swell_s",
]
assert len(_ALL_V1) == 41

SPECS: dict[str, Spec] = {}


def _add(s: Spec) -> None:
    assert s.name not in SPECS
    SPECS[s.name] = s


# --- iteration 1: first candidates for Goal 1 (after infra debugging, see DECISIONS D-011/D-012)
_RECENCY = ["hd_yt_d1", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt",
            "clim_rate", "doy_sin", "doy_cos"]
_D1 = ["hd_yt_trip_frac_d1", "hd_log_ytfish_d1", "hd_yt_landings_d1", "hd_yt_d2", "tq_yt_d1", "hd_yt_streak"]
for thr_name, rule in (("mcc", "mcc"), ("p50", "fixed:0.5"), ("p40", "fixed:0.4")):
    _add(Spec(f"e001_logreg_all_{thr_name}", _ALL_V1, "logreg", C=0.1, threshold_rule=rule,
              notes="All candidate features, L2 logistic C=0.1"))
    _add(Spec(f"e002_hgb_all_{thr_name}", _ALL_V1, "hgb", threshold_rule=rule,
              notes="All candidate features, shallow gradient boosting"))
    _add(Spec(f"e003_logreg_recency_{thr_name}", _RECENCY + _D1, "logreg", C=1.0, threshold_rule=rule,
              notes="Half-day recency + D-1 intensity + seasonality"))
_add(Spec("e004_breakout_logreg", _ALL_V1, "logreg", C=0.1, subset="breakout",
          threshold_rule="precision>=0.45",
          notes="Goal 3: trained/scored only on days with no half-day yt in prior 7 days"))


def get(name: str) -> Spec:
    return SPECS[name]

# --- iteration 3: promoted from sweeps/sweep1_iter2 + sweeps/sweep2_iter3 (D-019)
_R2 = ["hd_yt_d1", "hd_yt_lastday", "hd_ytdays_3", "hd_ytdays_7", "hd_ytdays_30", "hd_days_since_yt",
       "clim_rate", "doy_sin", "doy_cos"]
_FD = ["fd_visible_d1", "fd_yt_local_d1", "fd_yt_coronado_d1", "fd_yt_north_d1", "fd_yt_all_d1",
       "fd_yt_local_3", "fd_yt_local_days_3", "fd_yt_local_prev4_7", "fd_yt_coronado_3"]
_FDI = ["hd_yt_lastday*fd_yt_local_d1", "!hd_yt_lastday*fd_yt_local_d1", "hd_yt_lastday*fd_yt_local_3",
        "!hd_yt_lastday*fd_yt_coronado_d1"]
_add(Spec("e005_recency_d1_C001_p35", _R2 + _D1, "logreg", C=0.01, threshold_rule="fixed:0.35",
          notes="Best catch-history-only config in sweeps 1-2"))
_add(Spec("e006_recency_d1_fishdope_C003_p35", _R2 + _D1 + _FD + _FDI, "logreg", C=0.03,
          threshold_rule="fixed:0.35", notes="Best config using FishDope in sweep 2"))

# --- iteration 4: sentence-level FishDope evidence (D-022), promoted from sweeps/sweep3_iter4
_FS = ["fd_local_catch_d1", "fd_local_sight_d1", "fd_local_neg_d1", "fd_coronado_catch_d1", "fd_north_catch_d1",
       "fd_local_catch_3", "fd_local_catchdays_3", "fd_local_sight_3", "fd_coronado_catch_3"]
_FSI = ["hd_yt_lastday*fd_local_catch_3", "!hd_yt_lastday*fd_local_catch_3", "hd_yt_lastday*fd_local_neg_d1",
        "!hd_yt_lastday*fd_coronado_catch_d1"]
_add(Spec("e007_recency_d1_fdsent_C003_p35", _R2 + _D1 + _FS + _FSI, "logreg", C=0.03,
          threshold_rule="fixed:0.35", notes="Catch history + sentence-level FishDope catch/sight/negation"))

# --- agent B (catch-history / fleet), promoted from sweeps/B_sweep2_structure and sweeps/B_sweep3_compact
_FLEET = ["bt_hot_last", "bt_hot_sailed_d1", "hd_yt_trips_d1", "hd_yt_ewm", "tq_yt_trip_frac_3", "tq_yt_trip_frac_30",
          "hd_ytrate_60", "d1_surface_frac", "hd_surface_frac_7"]
_add(Spec("eB01_fleet_C003_mccrange", _R2 + _D1 + _FLEET, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5",
          notes="Catch history + boat/fleet state, 3/4-day success, species mix; inner-OOF threshold in [0.3, 0.5]"))
_add(Spec("eB02_fleet_fdsent_C003_p35", _R2 + _D1 + _FLEET + _FS + _FSI, "logreg", C=0.03,
          threshold_rule="fixed:0.35", notes="eB01 features + sentence-level FishDope (e007)"))

# --- iteration 5 (D-026/D-027): pre-registered finalists for dev 2012-2016, run once each
_B01 = get("eB01_fleet_C003_mccrange")
_E07 = get("e007_recency_d1_fdsent_C003_p35")
_add(Spec("e008_e007_monthly", _E07.features, "logreg", C=0.03, threshold_rule="fixed:0.35",
          retrain="month", notes="e007 with monthly refit"))
_add(Spec("e009_eB01_monthly_p40", _B01.features, _B01.model, C=_B01.C, threshold_rule="fixed:0.4",
          retrain="month", extra=_B01.extra, notes="eB01 feature set, monthly refit, threshold 0.4 (sweep 4 #2)"))

# --- agent F (latent state / decision layer), promoted from sweeps/F_sweep3 (D-F05)
_add(Spec("eF01_B01_recal90_mccrange", _B01.features, "logreg", C=0.03, threshold_rule="mcc_range:0.3:0.5",
          extra={"recal": {"window": 90, "k0": 10.0}},
          notes="eB01 features + online recalibration from out-of-sample labels of D-90..D-2 (D-F04); best F sweep dev MCC"))
_add(Spec("eF02_B01_recal60_p40", _B01.features, "logreg", C=0.03, threshold_rule="fixed:0.4",
          extra={"recal": {"window": 60, "k0": 10.0}},
          notes="eB01 features + online recalibration, pre-planned 60-day window, threshold 0.4"))
