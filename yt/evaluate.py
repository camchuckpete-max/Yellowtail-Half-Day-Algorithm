"""Walk-forward evaluation, baselines, metrics and auditable run artifacts.

Protocol (DECISIONS.md D-006..D-010):
  * Dev folds: test years 2012-2023 (D-033). Each fold trains ONLY on target
    days < (first test day - 1 day) so every training label was fully known
    at the first prediction's cutoff. The model is frozen for the whole year.
  * Threshold: chosen on inner walk-forward out-of-fold predictions inside
    the training window (never on the test fold).
  * Holdout: every target day >= 2024-01-01 (D-033). Evaluated only with --holdout;
    every access is appended to holdout_access.log.
  * Coverage filter: a target day is scored only if >=5 of the previous 7
    days had half-day reports visible at the cutoff.
"""
from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, matthews_corrcoef, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
DEV_YEARS = tuple(range(2012, 2024))         # D-033 (2012-2016 per D-027; 2012-2014 before that)
HOLDOUT_START = pd.Timestamp("2024-01-01")   # D-033 (was 2017-01-01 per D-027; never accessed)
MIN_COV7 = 5
# Breakout-eligible day: no half-day yellowtail visible in D-3..D-1 (D-015, user
# change 2026-09-23; was D-7..D-1 under D-013).
BREAKOUT_COL = "hd_ytdays_3"


# ---------------------------------------------------------------- models
@dataclass
class Spec:
    name: str
    features: list[str]
    model: str = "logreg"          # logreg | hgb
    C: float = 1.0
    subset: str = "all"            # all | breakout (train/score only BREAKOUT_COL == 0 days)
    threshold_rule: str = "mcc"    # mcc | precision>=P
    clip_z: float = 4.0            # logreg: clip standardized inputs to +-clip_z (D-011)
    retrain: str = "year"          # year | month: refit cadence inside a test fold (D-026)
    halflife_days: float = 0.0     # >0: training rows weighted 0.5**(age/halflife) (D-026)
    inputs: str = "any"            # "conditions": Goal C allowlist enforced (D-031)
    dev_years: tuple = ()          # override DEV_YEARS (subset only), e.g. SST era (D-033)
    train_start: str = ""          # drop training rows before this date, e.g. "2020-01-01" (D-033)
    notes: str = ""
    extra: dict = field(default_factory=dict)


class Model:
    def __init__(self, spec: Spec):
        self.spec = spec

    @staticmethod
    def _tx(X: pd.DataFrame) -> pd.DataFrame:
        """log1p every per-trip rate (heavy-tailed, regime-shifting; D-011)."""
        X = X.copy()
        for c in X.columns:
            if "per_trip" in c:
                X[c] = np.log1p(X[c].clip(lower=0))
        return X

    def _z(self, Xf: pd.DataFrame) -> pd.DataFrame:
        return ((Xf - self.mu) / self.sd).clip(-self.spec.clip_z, self.spec.clip_z)

    # D-B03: composite model types built from the base learners.
    #   logreg_split: separate logistic fits for regime B1=1 and B1=0 (spec.extra["split_col"])
    #   ens:          mean of logistic and HGB probabilities
    def fit(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray | None = None) -> "Model":
        if self.spec.model == "logreg_split":
            col = self.spec.extra.get("split_col", "hd_yt_lastday")
            self.parts = {}
            for v in (0, 1):
                m = (X[col].to_numpy() == v)
                sub = Spec(**{**self.spec.__dict__, "model": "logreg",
                              "C": self.spec.extra.get(f"C{v}", self.spec.C)})
                if len(set(y[m])) < 2:  # regime has one class in this window: fall back to pooled fit
                    m = np.ones(len(y), dtype=bool)
                self.parts[v] = Model(sub).fit(X[m].drop(columns=[col]), y[m], None if w is None else w[m])
            return self
        if self.spec.model == "avg_subsets":  # D-B03: mean of logistic fits on named feature subsets
            self.parts = {i: Model(Spec(**{**self.spec.__dict__, "model": "logreg", "features": fs})).fit(X[fs], y, w)
                          for i, fs in enumerate(self.spec.extra["subsets"])}
            return self
        if self.spec.model == "ens":
            self.parts = {k: Model(Spec(**{**self.spec.__dict__, "model": k})).fit(X, y, w) for k in ("logreg", "hgb")}
            return self
        X = self._tx(X)
        self.med = X.median(numeric_only=True).fillna(0.0)
        Xf = X.fillna(self.med)
        if self.spec.model == "logreg":
            self.mu = Xf.mean()
            self.sd = Xf.std(ddof=0).replace(0, 1.0)
            Z = self._z(Xf)
            self.clf = LogisticRegression(C=self.spec.C, max_iter=5000).fit(Z.to_numpy(), y, sample_weight=w)
        else:
            p = dict(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0, random_state=0)
            p.update(self.spec.extra.get("hgb", {}))
            mono = self.spec.extra.get("monotone")  # D-B03: {feature: +1/-1}, others 0
            if mono:
                p["monotonic_cst"] = [int(mono.get(c, 0)) for c in X.columns]
            self.clf = HistGradientBoostingClassifier(**p).fit(Xf.to_numpy(), y, sample_weight=w)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.spec.model == "logreg_split":
            col = self.spec.extra.get("split_col", "hd_yt_lastday")
            p = np.zeros(len(X))
            for v, m in self.parts.items():
                sel = (X[col].to_numpy() == v)
                if sel.any():
                    p[sel] = m.predict(X[sel].drop(columns=[col]))
            return p
        if self.spec.model == "avg_subsets":
            return np.mean([m.predict(X[self.spec.extra["subsets"][i]]) for i, m in self.parts.items()], axis=0)
        if self.spec.model == "ens":
            w = self.spec.extra.get("w_logreg", 0.5)
            return w * self.parts["logreg"].predict(X) + (1 - w) * self.parts["hgb"].predict(X)
        Xf = self._tx(X).fillna(self.med)
        if self.spec.model == "logreg":
            Xf = self._z(Xf)
        return self.clf.predict_proba(Xf.to_numpy())[:, 1]

    def weights(self) -> dict:
        if self.spec.model in ("logreg_split", "ens", "avg_subsets"):
            return {str(k): m.weights() for k, m in self.parts.items()}
        w = {"transform": "log1p on *per_trip* features, then median impute"
                           + (f", standardize, clip z to +-{self.spec.clip_z}" if self.spec.model == "logreg" else ""),
             "impute_median": self.med.to_dict()}
        if self.spec.model == "logreg":
            coef = self.clf.coef_[0]
            w["standardized_coef"] = dict(zip(self.mu.index, coef.tolist()))
            w["intercept_standardized"] = float(self.clf.intercept_[0])
            w["scaler_mean"] = self.mu.to_dict()
            w["scaler_sd"] = self.sd.to_dict()
            raw = coef / self.sd.to_numpy()
            w["raw_coef_on_transformed_inputs"] = dict(zip(self.mu.index, raw.tolist()))
            w["raw_intercept"] = float(self.clf.intercept_[0] - (raw * self.mu.to_numpy()).sum())
        else:
            w["hgb_params"] = self.clf.get_params()
        return w


# ---------------------------------------------------------------- metrics
def hard_metrics(y: np.ndarray, call: np.ndarray) -> dict:
    y, call = np.asarray(y).astype(int), np.asarray(call).astype(int)
    tp = int(((call == 1) & (y == 1)).sum()); fp = int(((call == 1) & (y == 0)).sum())
    fn = int(((call == 0) & (y == 1)).sum()); tn = int(((call == 0) & (y == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    return {"n": len(y), "base_rate": float(y.mean()) if len(y) else float("nan"),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "accuracy": (tp + tn) / len(y) if len(y) else float("nan"),
            "precision": prec, "recall": rec,
            "f1": 2 * prec * rec / (prec + rec) if tp else 0.0,
            "mcc": float(matthews_corrcoef(y, call)) if len(set(y)) > 1 else float("nan")}


def prob_metrics(y, p) -> dict:
    y = np.asarray(y).astype(int)
    if len(set(y)) < 2:
        return {}
    return {"auc": float(roc_auc_score(y, p)), "brier": float(brier_score_loss(y, p))}


def wilson_lower(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return float("nan")
    ph = k / n
    return (ph + z * z / (2 * n) - z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def block_bootstrap_diff(y, a, b, block=14, reps=2000, seed=0) -> dict:
    """95% CI of MCC(a) - MCC(b) with a moving-block bootstrap over days."""
    rng = np.random.default_rng(seed)
    y, a, b = map(np.asarray, (y, a, b))
    n = len(y); nb = math.ceil(n / block)
    diffs = []
    for _ in range(reps):
        starts = rng.integers(0, n - block + 1, nb)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        if len(set(y[idx])) < 2:
            continue
        diffs.append(matthews_corrcoef(y[idx], a[idx]) - matthews_corrcoef(y[idx], b[idx]))
    d = np.array(diffs)
    return {"mean": float(d.mean()), "lo95": float(np.quantile(d, 0.025)),
            "hi95": float(np.quantile(d, 0.975)), "p_le_0": float((d <= 0).mean()), "reps": len(d)}


# ---------------------------------------------------------------- protocol
def eligible(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["hd_covdays_7"] >= MIN_COV7].reset_index(drop=True)


def _subset(df: pd.DataFrame, spec: Spec) -> pd.DataFrame:
    return df[df[BREAKOUT_COL] == 0] if spec.subset == "breakout" else df


def _pick_threshold(y, p, rule: str) -> tuple[float, dict]:
    cands = np.unique(np.round(p, 4))
    best_t, best_s, info = 0.5, -np.inf, {}
    if rule == "mcc":
        for t in cands:
            c = (p >= t).astype(int)
            if c.sum() == 0 or c.sum() == len(c):
                continue
            s = matthews_corrcoef(y, c)
            if s > best_s:
                best_t, best_s = float(t), s
        info = {"rule": "max MCC on inner OOF", "inner_mcc": float(best_s)}
    elif rule.startswith("mcc_range:"):  # D-B04: inner-OOF MCC max, restricted to [lo, hi]
        lo, hi = map(float, rule.split(":")[1:])
        best_t = (lo + hi) / 2
        for t in np.round(np.arange(lo, hi + 1e-9, 0.01), 2):
            c = (p >= t).astype(int)
            if c.sum() == 0 or c.sum() == len(c):
                continue
            s = matthews_corrcoef(y, c)
            if s > best_s:
                best_t, best_s = float(t), s
        info = {"rule": f"max MCC on inner OOF within [{lo}, {hi}]", "inner_mcc": float(best_s)}
    elif rule.startswith("fixed:"):
        best_t = float(rule.split(":")[1])
        info = {"rule": f"fixed {best_t}"}
    elif rule.startswith("precision>="):
        target = float(rule.split(">=")[1])
        min_calls = 10
        for t in cands:
            c = p >= t
            k = int(c.sum())
            if k < min_calls:
                continue
            prec = float(y[c].mean())
            if prec >= target and k > best_s:  # most calls among thresholds meeting target
                best_t, best_s = float(t), k
        if best_s == -np.inf:  # target unreachable in training: call nothing
            best_t = float("inf")
        info = {"rule": f"most calls with inner-OOF precision >= {target}, min {min_calls} calls",
                "inner_calls": None if best_s == -np.inf else int(best_s)}
    return best_t, info


def recency_weights(dates: pd.Series, ref: pd.Timestamp, spec: Spec) -> np.ndarray | None:
    """Weights relative to the first prediction day `ref`; None when weighting is off (D-026)."""
    if spec.halflife_days <= 0:
        return None
    age = (ref - dates).dt.days.to_numpy()
    return 0.5 ** (age / spec.halflife_days)


def _inner_oof(train: pd.DataFrame, spec: Spec) -> tuple[np.ndarray, np.ndarray]:
    ys, ps = [], []
    years = sorted(train["date"].dt.year.unique())
    for y in years[1:]:
        first = pd.Timestamp(y, 1, 1)
        tr = _subset(train[train["date"] < first - pd.Timedelta(days=1)], spec)
        te = _subset(train[train["date"].dt.year == y], spec)
        if len(tr) < 50 or tr["y"].nunique() < 2 or len(te) == 0:
            continue
        m = Model(spec).fit(tr[spec.features], tr["y"].to_numpy(), recency_weights(tr["date"], first, spec))
        ys.append(te["y"].to_numpy()); ps.append(m.predict(te[spec.features]))
    return (np.concatenate(ys), np.concatenate(ps)) if ys else (np.array([]), np.array([]))


def folds(df: pd.DataFrame, holdout: bool, years: tuple = ()):
    if holdout:
        yield "holdout", df[df["date"] >= HOLDOUT_START]
    else:
        assert set(years) <= set(DEV_YEARS), "dev_years must be a subset of DEV_YEARS"
        for y in (years or DEV_YEARS):
            yield str(y), df[df["date"].dt.year == y]


def add_derived(df: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """Derived columns named in a spec: 'a*b' = product, '!a' = 1 - a. Row-wise
    only, so they inherit the PIT property of their inputs."""
    df = df.copy()
    def col(n):
        return 1 - df[n[1:]] if n.startswith("!") else df[n]
    for n in names:
        if n in df.columns:
            continue
        if "*" in n:
            a, b = n.split("*")
            df[n] = col(a) * col(b)
        elif n.startswith("!"):
            df[n] = col(n)
    return df


def run_spec(df: pd.DataFrame, spec: Spec, holdout: bool = False) -> tuple[pd.DataFrame, dict]:
    preds, fold_info = [], {}
    if spec.inputs == "conditions":
        from .features import assert_conditions_only
        assert_conditions_only(spec.features)
    df = add_derived(df, spec.features)
    if spec.train_start:
        df = df[df["date"] >= pd.Timestamp(spec.train_start)]
    for name, test in folds(df, holdout, spec.dev_years):
        first = test["date"].min()
        train = df[df["date"] < first - pd.Timedelta(days=1)]
        assert train["date"].max() < first - pd.Timedelta(days=1)
        if spec.threshold_rule.startswith("insample_"):
            # D-035: threshold from the fitted model's own training-window predictions (training
            # data only). For short histories (e.g. SST era: one training year) where no inner
            # walk-forward fold exists.
            trs0 = _subset(train, spec)
            m0 = Model(spec).fit(trs0[spec.features], trs0["y"].to_numpy(),
                                 recency_weights(trs0["date"], first, spec))
            thr, tinfo = _pick_threshold(trs0["y"].to_numpy(), m0.predict(trs0[spec.features]),
                                         spec.threshold_rule[len("insample_"):])
            tinfo = {**tinfo, "source": "in-sample training predictions"}
        else:
            yi, pi = _inner_oof(train, spec)
            thr, tinfo = _pick_threshold(yi, pi, spec.threshold_rule) if len(yi) else (0.5, {"rule": "default 0.5"})
        # Threshold is fixed per fold (chosen from data before the fold); the model itself is
        # refit per chunk. Each chunk trains only on days < chunk start - 1 day (D-026).
        chunks = ([(name, test)] if spec.retrain == "year" else
                  [(f"{name}-{k:02d}", g) for k, g in test.groupby(test["date"].dt.month)])
        for cname, chunk in chunks:
            cfirst = chunk["date"].min()
            ctrain = df[df["date"] < cfirst - pd.Timedelta(days=1)]
            assert ctrain["date"].max() < cfirst - pd.Timedelta(days=1)
            trs = _subset(ctrain, spec)
            m = Model(spec).fit(trs[spec.features], trs["y"].to_numpy(), recency_weights(trs["date"], cfirst, spec))
            p = m.predict(chunk[spec.features])
            out = chunk[["date", "y", "hd_yt_lastday", "hd_ytdays_7", BREAKOUT_COL]].copy()
            out["fold"] = name
            out["prob"] = p
            out["call"] = (p >= thr).astype(int)
            if spec.subset == "breakout":
                out.loc[out[BREAKOUT_COL] > 0, "call"] = 0  # model only speaks on breakout-eligible days
            preds.append(out)
            fold_info[cname] = {"train_first": str(ctrain["date"].min().date()),
                                "train_last": str(ctrain["date"].max().date()),
                                "n_train": int(len(trs)), "threshold": thr, "threshold_info": tinfo,
                                "halflife_days": spec.halflife_days, "weights": m.weights()}
    return pd.concat(preds, ignore_index=True), fold_info


def baseline_calls(pred: pd.DataFrame) -> dict[str, np.ndarray]:
    return {"B1_yesterday": pred["hd_yt_lastday"].to_numpy().astype(int),
            "B2_last7": (pred["hd_ytdays_7"] > 0).to_numpy().astype(int)}


def summarize(pred: pd.DataFrame, bootstrap: bool = True) -> dict:
    y = pred["y"].to_numpy()
    res = {"model": {**hard_metrics(y, pred["call"]), **prob_metrics(y, pred["prob"])}}
    res["per_fold"] = {f: hard_metrics(g["y"], g["call"]) for f, g in pred.groupby("fold")}
    base = baseline_calls(pred)
    res["baselines"] = {k: hard_metrics(y, v) for k, v in base.items()}
    best = max(base, key=lambda k: res["baselines"][k]["mcc"])
    res["best_baseline"] = best
    res["mcc_diff_vs_best_baseline"] = (block_bootstrap_diff(y, pred["call"].to_numpy(), base[best])
                                        if bootstrap else {"lo95": float("nan"), "hi95": float("nan")})
    # Breakout: days with no half-day yellowtail visible in the breakout window.
    bo = pred[pred[BREAKOUT_COL] == 0]
    k = int(((bo["call"] == 1) & (bo["y"] == 1)).sum()); n = int((bo["call"] == 1).sum())
    res["breakout"] = {"definition": f"{BREAKOUT_COL} == 0", "eligible_days": int(len(bo)), "actual_breakouts": int(bo["y"].sum()),
                       "calls": n, "hits": k, "precision": k / n if n else float("nan"),
                       "precision_wilson_lo95": wilson_lower(k, n),
                       "recall": k / bo["y"].sum() if bo["y"].sum() else float("nan"),
                       "eligible_base_rate": float(bo["y"].mean()) if len(bo) else float("nan")}
    return res


# ---------------------------------------------------------------- artifacts
def _git(*args) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def write_run(spec: Spec, df: pd.DataFrame, manifest: dict, pred: pd.DataFrame, fold_info: dict,
              summary: dict, holdout: bool, tag: str = "") -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rid = f"{ts}_{spec.name}{'_HOLDOUT' if holdout else ''}"
    d = ROOT / "runs" / rid
    d.mkdir(parents=True)
    code = {"algo_repo_head": _git("rev-parse", "HEAD"),
            "algo_repo_dirty": bool(_git("status", "--porcelain", "yt", "tests"))}
    if not code["algo_repo_head"] or code["algo_repo_dirty"]:
        raise SystemExit("refusing to save a run from uncommitted code (commit yt/ first, or use --no-save)")
    (d / "config.json").write_text(json.dumps({**spec.__dict__, "holdout": holdout, "tag": tag,
                                               "dev_years": DEV_YEARS, "holdout_start": str(HOLDOUT_START.date()),
                                               "min_cov7": MIN_COV7}, indent=2, default=str))
    (d / "data_manifest.json").write_text(json.dumps({**manifest, **code}, indent=2, default=str))
    (d / "weights.json").write_text(json.dumps(fold_info, indent=2, default=str))
    (d / "metrics.json").write_text(json.dumps(summary, indent=2, default=str))
    df = add_derived(df, spec.features)
    inputs = df[df["date"].isin(pred["date"])][["date", "cutoff", "audit_max_trip_available_at",
                                                 "audit_fc_src_id", "audit_fc_available_at", *spec.features, "y"]]
    inputs.to_csv(d / "inputs.csv.gz", index=False)
    pred.to_csv(d / "predictions.csv", index=False)
    return d
