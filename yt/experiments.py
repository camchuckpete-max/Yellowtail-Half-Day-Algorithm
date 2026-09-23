"""Named experiment specs. Every run references one of these by name, so the
exact feature list / model / threshold rule of any logged run is in git.
Never edit a spec after it has been run: add a new name instead."""
from __future__ import annotations

from .evaluate import Spec
from .features import FEATURES

# Frozen copy of the feature list used by iteration-1 specs (D-017).
_ALL_V1 = [f for f in FEATURES if f not in ("hd_yt_lastday", "hd_lastday_age")]
_ALL_V2 = list(FEATURES)

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
