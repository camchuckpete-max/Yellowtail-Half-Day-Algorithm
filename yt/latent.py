"""Latent-state ("yellowtail are within half-day range") filter, D-F01.

Two-state hidden Markov model over days. For target day D the filter starts from the
seasonal stationary distribution LAT_L days back and runs FORWARD ONLY over the evidence
columns `lat_*_k` (k = LAT_L..1), which features.build computed from the events visible
at the D-1 21:00 PT cutoff. There is no backward (smoothing) pass, so P(state on D)
depends on nothing that was not public at the cutoff.

  transition   P(s_t=1 | s_t-1=1) = sigmoid(a0 + a1 sin(doy) + a2 cos(doy))      persistence
               P(s_t=1 | s_t-1=0) = sigmoid(b0 + b1 sin(doy) + b2 cos(doy))      arrival
  emission     half-day: k of n trips with yt, binomial with per-trip rate q1 (state 1) or
               q0 (state 0), log-likelihood ratio tempered by tau (trips on one day are not
               independent); 3/4-day likewise with r1 / r0 (own temper tau_tq);
               FishDope (only when a report for that date is visible): local catch sentence
               Bernoulli c1 / c0, local negation Bernoulli g1 / g0.
               A day with no trips / no report contributes no evidence (log-ratio 0).
  output       P(y_D = 1) = pi_D * sigmoid(u1 + v log n_hat) + (1 - pi_D) * sigmoid(u0 + v log n_hat),
               n_hat = hd_trips_dow_4w (same-weekday trip count over 4 weeks, visible proxy for effort on D).

Parameters are fitted on the training window only (the rows Model.fit receives), by
minimising the log-loss of y_D given each training row's own visible evidence, plus a
small ridge toward the starting values. Finite-difference gradients are evaluated for
all parameters in one batched forward pass.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .features import LAT_L

PARAMS = ["a0", "a1", "a2", "b0", "b1", "b2", "lq1", "lq0", "ltau", "lr1", "lr0", "ltau_tq",
          "lc1", "lc0", "lg1", "lg0", "u1", "u0", "v",
          # emission "day" (D-F03): day-level log-ratios, see forward()
          "e_any", "e_cnt", "e_z0", "e_zn", "t_any", "t_z",
          # hotness covariate on the transitions (D-F03)
          "a3", "b3"]
# Starting values: persistence ~0.9, arrival ~0.03, per-trip yt rate 0.35 when present / 0.01 absent.
THETA0 = np.array([2.2, 0.0, 0.0, -3.5, 0.0, 0.0, -0.6, -4.6, -0.7, -1.0, -2.5, -0.7,
                   -1.5, -3.0, -3.0, -1.0, 0.0, -3.0, 0.5,
                   3.0, -1.0, 0.0, 0.0, 1.0, -1.0,
                   0.0, 0.0])
FD_PARAMS = ("lc1", "lc0", "lg1", "lg0")
TQ_PARAMS = ("lr1", "lr0", "ltau_tq", "t_any", "t_z")
BINOM_PARAMS = ("lq1", "lq0", "ltau", "lr1", "lr0", "ltau_tq")
DAY_PARAMS = ("e_any", "e_cnt", "e_z0", "e_zn", "t_any", "t_z")
HOT_PARAMS = ("a3", "b3")
_softplus = lambda x: np.logaddexp(0.0, x)

_sig = lambda x: 1.0 / (1.0 + np.exp(-x))


def _log_sig(x):
    return -np.logaddexp(0.0, -x)


def evidence(X: pd.DataFrame) -> dict[str, np.ndarray]:
    """(n_rows, LAT_L) arrays ordered oldest lag first, plus doy of each lag day and effort."""
    ev = {o: np.stack([X[f"lat_{o}_{k}"].to_numpy(float) for k in range(LAT_L, 0, -1)], axis=1)
          for o in ("nhd", "khd", "ntq", "ktq", "fdv", "fdc", "fdn")}
    doy = X["lat_doy"].to_numpy(float)[:, None] - np.arange(LAT_L, 0, -1)[None, :]  # doy of day D-k
    ang = 2 * np.pi * doy / 365.25
    ev["sin"], ev["cos"] = np.sin(ang), np.cos(ang)
    ang_d = 2 * np.pi * X["lat_doy"].to_numpy(float) / 365.25
    ev["sin_d"], ev["cos_d"] = np.sin(ang_d), np.cos(ang_d)
    ev["log_n"] = np.log(np.maximum(X["hd_trips_dow_4w"].to_numpy(float), 0.5))
    if "hd_ytrate_60" in X.columns:
        r = np.clip(X["hd_ytrate_60"].to_numpy(float), 0.02, 0.98)
        ev["hot"] = np.log(r / (1 - r))
    return ev


def forward(theta: np.ndarray, ev: dict, use: dict) -> tuple[np.ndarray, np.ndarray]:
    """theta: (P, n_params). Returns (P(state on D = 1), P(y_D = 1)), each (P, n_rows).

    use["emit"] == "binom": per-trip binomial emissions (module docstring).
    use["emit"] == "day" (D-F03): day-level log-ratios that do not assume trips are independent:
        half-day, k >= 1 yt trips:  e_any + softplus(e_cnt) * log(k)
        half-day, 0 of n >= 1:      -(softplus(e_z0) + softplus(e_zn) * log(n))
        3/4-day:  k >= 1: t_any;  0 of n >= 1: -softplus(t_z)
    use["hot"] (D-F03): transitions also get a3 * h / b3 * h, h = logit of the 60-day half-day
        yt-day rate as of the cutoff (hd_ytrate_60, visible prefix), one value per target day."""
    T = {k: theta[:, i][:, None] for i, k in enumerate(PARAMS)}
    day = use.get("emit", "binom") == "day"
    hot = ev["hot"][None, :] if use.get("hot") else 0.0
    q1, q0 = _sig(T["lq1"]), _sig(T["lq0"])
    kh_pos = np.log(q1 / q0); kh_neg = np.log((1 - q1) / (1 - q0)); tau = _sig(T["ltau"])
    r1, r0 = _sig(T["lr1"]), _sig(T["lr0"])
    kt_pos = np.log(r1 / r0); kt_neg = np.log((1 - r1) / (1 - r0)); tau_t = _sig(T["ltau_tq"])
    c1, c0, g1, g0 = (_sig(T[k]) for k in FD_PARAMS)
    fc_pos, fc_neg = np.log(c1 / c0), np.log((1 - c1) / (1 - c0))
    fg_pos, fg_neg = np.log(g1 / g0), np.log((1 - g1) / (1 - g0))

    def trans(s, c):
        return (_sig(T["a0"] + T["a1"] * s + T["a2"] * c + T["a3"] * hot),
                _sig(T["b0"] + T["b1"] * s + T["b2"] * c + T["b3"] * hot))

    a, b = trans(ev["sin"][None, :, 0], ev["cos"][None, :, 0])
    pi = b / (1 - a + b)  # stationary distribution at the start of the window
    for j in range(LAT_L):
        if j:
            a, b = trans(ev["sin"][None, :, j], ev["cos"][None, :, j])
            pi = pi * a + (1 - pi) * b
        n, k = ev["nhd"][None, :, j], ev["khd"][None, :, j]
        if day:
            llr = np.where(k > 0, T["e_any"] + _softplus(T["e_cnt"]) * np.log(np.maximum(k, 1)),
                           np.where(n > 0, -(_softplus(T["e_z0"]) + _softplus(T["e_zn"]) * np.log(np.maximum(n, 1))), 0.0))
        else:
            llr = tau * (k * kh_pos + (n - k) * kh_neg)
        if use["tq"]:
            n, k = ev["ntq"][None, :, j], ev["ktq"][None, :, j]
            if day:
                llr = llr + np.where(k > 0, T["t_any"], np.where(n > 0, -_softplus(T["t_z"]), 0.0))
            else:
                llr = llr + tau_t * (k * kt_pos + (n - k) * kt_neg)
        if use["fd"]:
            v, c, g = ev["fdv"][None, :, j], ev["fdc"][None, :, j], ev["fdn"][None, :, j]
            llr = llr + v * (c * fc_pos + (1 - c) * fc_neg + g * fg_pos + (1 - g) * fg_neg)
        lp = np.log(np.clip(pi, 1e-12, 1 - 1e-12)) - np.log(np.clip(1 - pi, 1e-12, 1))
        pi = _sig(lp + llr)
    a, b = trans(ev["sin_d"][None, :], ev["cos_d"][None, :])
    pi = pi * a + (1 - pi) * b  # one-step prediction to D
    ln = ev["log_n"][None, :]
    py = pi * _sig(T["u1"] + T["v"] * ln) + (1 - pi) * _sig(T["u0"] + T["v"] * ln)
    return pi, np.clip(py, 1e-9, 1 - 1e-9)


class LatentFilter:
    def __init__(self, use_tq: bool = True, use_fd: bool = True, ridge: float = 0.01, emit: str = "binom",
                 hot: bool = False):
        self.use = {"tq": use_tq, "fd": use_fd, "emit": emit, "hot": hot}
        self.ridge = ridge
        unused = set(DAY_PARAMS if emit == "binom" else BINOM_PARAMS) | (set() if hot else set(HOT_PARAMS))
        self.free = np.array([not ((p in FD_PARAMS and not use_fd) or (p in TQ_PARAMS and not use_tq) or p in unused)
                              for p in PARAMS])

    def fit(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray | None = None) -> "LatentFilter":
        ev = evidence(X)
        y = np.asarray(y, float)
        w = np.ones(len(y)) if w is None else np.asarray(w, float)
        w = w / w.sum()
        idx = np.flatnonzero(self.free)
        h = 1e-4

        def loss_batch(thetas):
            _, py = forward(thetas, ev, self.use)
            ll = (w * (y * np.log(py) + (1 - y) * np.log(1 - py))).sum(axis=1)
            return -ll + self.ridge * ((thetas - THETA0) ** 2).sum(axis=1)

        def fg(z):
            th = THETA0.copy(); th[idx] = z
            batch = np.repeat(th[None, :], len(idx) + 1, axis=0)
            batch[np.arange(1, len(idx) + 1), idx] += h
            L = loss_batch(batch)
            return float(L[0]), (L[1:] - L[0]) / h

        with np.errstate(all="ignore"):  # extreme trial steps give inf/nan losses; L-BFGS backtracks
            r = minimize(fg, THETA0[idx], jac=True, method="L-BFGS-B", options={"maxiter": 400})
        self.theta = THETA0.copy(); self.theta[idx] = r.x
        self.fit_info = {"converged": bool(r.success), "nit": int(r.nit), "train_logloss": float(r.fun)}
        return self

    def predict_state(self, X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        pi, py = forward(self.theta[None, :], evidence(X), self.use)
        return pi[0], py[0]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.predict_state(X)[1]

    def weights(self) -> dict:
        return {"params": dict(zip(PARAMS, self.theta.tolist())), "free": dict(zip(PARAMS, self.free.tolist())),
                "use": self.use, "ridge": self.ridge, **self.fit_info}
