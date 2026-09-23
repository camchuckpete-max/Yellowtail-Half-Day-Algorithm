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
