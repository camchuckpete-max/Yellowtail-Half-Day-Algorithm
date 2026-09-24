"""Goal D (D-039): per-trip yellowtail presence for New Seaforth / Sea Watch half-day trips,
conditions-only inputs, walk-forward by year, reported as calibrated probability bands."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from . import dataset, events, features, source
from .evaluate import Model, Spec, HOLDOUT_START

BOATS = ("New Seaforth", "Sea Watch")
TRIP_FEATURES = ["trip_am", "trip_pm", "trip_twilight", "boat_seawatch"]
BANDS = [(0.0, 0.05), (0.05, 0.15), (0.15, 0.35), (0.35, 0.65), (0.65, 0.85), (0.85, 1.01)]
BAND_NAMES = ["0-5%", "5-15%", "15-35% (~25%)", "35-65% (~50%)", "65-85% (~75%)", "85-100%"]


def build(strict: bool = False) -> tuple[pd.DataFrame, dict]:
    """One row per trip; conditions features are the PIT day-level features for the trip date
    (built for the 21:00 PT D-1 cutoff) — only the conditions allowlist is ever used."""
    day, manifest = dataset.build(strict=strict)
    db = source.open_db(source.source_manifest())
    t = events.load_trips(db, strict=strict)
    t = t[t["boat"].isin(BOATS) & t["is_hd_fishing"]].copy()
    t["y"] = (t["yt"] > 0).astype(int)
    t["trip_am"] = (t["cls"] == "hd_am").astype(int)
    t["trip_pm"] = t["cls"].isin(["hd_pm", "hd_unspecified"]).astype(int)
    t["trip_twilight"] = (t["cls"] == "hd_twilight").astype(int)
    t["boat_seawatch"] = (t["boat"] == "Sea Watch").astype(int)
    cond = [c for c in day.columns if c.startswith(features.CONDITIONS_PREFIXES)
            and not c.startswith(features.FORBIDDEN_PREFIXES)]
    out = t[["fished_date", "boat", "cls", "y", *TRIP_FEATURES]].merge(
        day[["date", *cond]], left_on="fished_date", right_on="date", how="inner")
    return out.drop(columns=["fished_date"]).sort_values("date").reset_index(drop=True), manifest


def walk_forward(df: pd.DataFrame, feats: list[str], years, model="logreg", C=1.0,
                 train_start: str | None = None, extra: dict | None = None) -> pd.DataFrame:
    features.assert_conditions_only([f for f in feats if f not in TRIP_FEATURES])
    spec = Spec("tripD", feats, model, C=C, extra=extra or {})
    d = df if not train_start else df[df["date"] >= pd.Timestamp(train_start)]
    preds = []
    for y in years:
        first = pd.Timestamp(y, 1, 1)
        assert first < HOLDOUT_START, "Goal D dev folds must precede the holdout"
        tr = d[d["date"] < first - pd.Timedelta(days=1)]
        te = d[d["date"].dt.year == y]
        if tr["y"].nunique() < 2 or te.empty:
            continue
        m = Model(spec).fit(tr[feats], tr["y"].to_numpy())
        preds.append(te.assign(prob=m.predict(te[feats]), fold=y))
    return pd.concat(preds, ignore_index=True)


def band_table(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (lo, hi), name in zip(BANDS, BAND_NAMES):
        s = p[(p["prob"] >= lo) & (p["prob"] < hi)]
        rows.append({"band": name, "trips": len(s), "predicted_mean": s["prob"].mean() if len(s) else np.nan,
                     "observed_rate": s["y"].mean() if len(s) else np.nan})
    return pd.DataFrame(rows)


def summary(p: pd.DataFrame) -> dict:
    return {"trips": len(p), "base_rate": float(p["y"].mean()), "auc": float(roc_auc_score(p["y"], p["prob"])),
            "brier": float(brier_score_loss(p["y"], p["prob"])),
            "per_fold_auc": {int(f): round(float(roc_auc_score(g["y"], g["prob"])), 3)
                             for f, g in p.groupby("fold") if g["y"].nunique() > 1}}
