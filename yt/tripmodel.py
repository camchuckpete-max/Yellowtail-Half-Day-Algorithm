"""Trip-level model, aggregated to a day-level PIT feature (agent E, D-E01..).

Two logistic models are fit on *candidate boat-trip rows*, one row per
(boat, trip class, day d) for every (boat, class) pair with a visible half-day
trip in d-28..d-1:
  * sail model:  P(pair sails on d)            label = a trip of that pair fished d
  * yt model:    P(>=1 yellowtail | it sails)  label = that trip caught yellowtail
Every row's inputs are computed from the events visible at cutoff(d) = d-1 21:00,
built by streaming the trips table in available_at order (so a row can only
see what was public at its own cutoff). A row's label becomes public at
`label_at` = the publication time of its class on d (events.PUBLISH_TIME).

For target day D both models are refit at an anchor day A <= D (every
`refit_days`, deterministic in D) on rows with label_at <= cutoff(A) and whose
day d had a half-day report visible at cutoff(A); hence every training label was
public before the prediction for D is made (walk-forward inside the feature).
The candidate rows for D itself are scored and combined:
    tm_p = 1 - prod_trips (1 - P(sail) * P(yt | sail)).
tests/test_pit.py poisons / deletes every post-cutoff event and checks these
features are unchanged.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

from . import events
from .features import cutoff_for

HD = {"hd_am": "am", "hd_pm": "pm", "hd_unspecified": "pm", "hd_twilight": "tw"}
PUB_CLS = {"am": "hd_am", "pm": "hd_pm", "tw": "hd_twilight"}  # label publication time per class
MAIN_BOATS = ("New Seaforth", "Premier", "Dolphin", "Daily Double")
ACTIVE_DAYS = 28   # a (boat, class) pair is a candidate for d if it sailed in d-28..d-1 (visible)
PRIOR_DAYS = 365   # boat yellowtail prior window
PRIOR_M = 20.0     # boat prior shrinkage toward the fleet rate (pseudo-trips)

SAIL_X = ["c_am", "c_pm", "c_tw", "s_dow4", "s_14", "s_last", "weekend", "doy_sin", "doy_cos",
          "f_yt_lastday", "b_yt_last"]
YT_X = ["c_am", "c_pm", "c_tw", "b_yt_last", "b_frac7", "b_sailed7", "b_prior_lr", "f_yt_lastday",
        "f_frac_last", "f_ytdays7", "f_ewm", "f_rate60", "tq_frac3", "log_anglers28", "doy_sin", "doy_cos",
        "weekend"]
BOAT_X = [f"boat_{i}" for i in range(len(MAIN_BOATS))]
EXT_X = ["b_log_yt_last", "b_log_days_since_yt", "p_frac14", "f_yt_boats3"]  # D-E03
MIX_X = ["p_yt_last", "b_surface_last", "b_bottom_only_last", "b_log_anglers_last"]  # D-E04
SURFACE = ("yt", "bonito", "barracuda", "mackerel", "white_seabass")
BOTTOM = ("rockfish", "whitefish", "sheephead")


def _logit(p: float) -> float:
    return math.log(p / (1 - p))


def candidate_rows(trips: pd.DataFrame, days: pd.DatetimeIndex, strict: bool = False) -> pd.DataFrame:
    """One row per candidate (boat, class) for each day in `days` (sorted ascending), inputs PIT at
    cutoff(d); labels (`sailed`, `yt`) from the trips table and `label_at` when they became public."""
    av = trips["available_at"].to_numpy()
    fdv = trips["fished_date"].to_numpy()
    cls = trips["cls"].to_numpy()
    boats = trips["boat"].to_numpy()
    ytv = trips["yt"].to_numpy()
    ang = trips["anglers"].to_numpy()
    surf = sum(trips[c].to_numpy() for c in SURFACE)   # surface species incl. yt, calico (kelp) excluded
    bott = sum(trips[c].to_numpy() for c in BOTTOM)
    # Labels: (boat, class, day) -> (any yt, latest available_at among those trips)
    lab: dict = {}
    for b, c, f, y, a in zip(boats, cls, fdv, ytv, av):
        if c in HD:
            k = (b, HD[c], pd.Timestamp(f))
            o = lab.get(k)
            lab[k] = (bool(y > 0) or (o is not None and o[0]), a if o is None else max(a, o[1]))
    # Streaming state (only events with available_at <= current cutoff are ever added)
    present: dict = defaultdict(set)                  # (boat, class) -> fished days
    pair_ang: dict = defaultdict(dict)                 # (boat, class) -> {day: [sum anglers, n]}
    boat_day: dict = defaultdict(dict)                 # boat -> {day: [n, n_yt, yt fish]}
    boat_mix: dict = defaultdict(dict)                 # boat -> {day: [n, n surface, n bottom-only, anglers]} (D-E04)
    pair_day: dict = defaultdict(dict)                 # (boat, class) -> {day: [n, n_yt]}
    fleet_day: dict = {}                               # day -> [n, n_yt]   (half-day fishing trips)
    tq_day: dict = {}                                  # day -> [n, n_yt]   (3/4-day trips)
    boat_last: dict = {}                               # boat -> latest visible fished day
    order = np.argsort(av, kind="stable")
    i, n = 0, len(order)
    fleet_last = None
    rows = []
    one = pd.Timedelta(days=1)
    for d in days:
        c_t = np.datetime64(cutoff_for(d))
        while i < n and av[order[i]] <= c_t:
            j = order[i]; i += 1
            f = pd.Timestamp(fdv[j])
            if cls[j] in HD:
                k = (boats[j], HD[cls[j]])
                present[k].add(f)
                if ang[j] == ang[j]:
                    s = pair_ang[k].setdefault(f, [0.0, 0]); s[0] += ang[j]; s[1] += 1
                s = boat_day[boats[j]].setdefault(f, [0, 0, 0]); s[0] += 1; s[1] += int(ytv[j] > 0); s[2] += ytv[j]
                s = pair_day[k].setdefault(f, [0, 0]); s[0] += 1; s[1] += int(ytv[j] > 0)
                s = boat_mix[boats[j]].setdefault(f, [0, 0, 0, 0.0]); s[0] += 1
                s[1] += int(surf[j] > 0); s[2] += int(surf[j] == 0 and bott[j] > 0)
                s[3] += ang[j] if ang[j] == ang[j] else 0.0
                boat_last[boats[j]] = max(f, boat_last.get(boats[j], f))
                fleet_last = f if fleet_last is None else max(f, fleet_last)
                s = fleet_day.setdefault(f, [0, 0]); s[0] += 1; s[1] += int(ytv[j] > 0)
            elif cls[j] == "three_quarter":
                s = tq_day.setdefault(f, [0, 0]); s[0] += 1; s[1] += int(ytv[j] > 0)
        # Fleet state at cutoff(d)
        f_: dict = {}
        if fleet_last is not None:
            assert fleet_last < d
            last = fleet_last
            f_["f_yt_lastday"] = int(fleet_day[last][1] > 0)
            f_["f_frac_last"] = fleet_day[last][1] / fleet_day[last][0]
        else:
            f_["f_yt_lastday"], f_["f_frac_last"] = 0, 0.0
        f_["f_yt_boats3"] = sum(1 for bd in boat_day.values() if any(bd.get(d - k * one, (0, 0, 0))[1] > 0
                                                                       for k in range(1, 4)))
        f_["f_ytdays7"] = sum(1 for k in range(1, 8) if fleet_day.get(d - k * one, (0, 0))[1] > 0)
        num = den = 0.0
        for k in range(1, 15):
            v = fleet_day.get(d - k * one)
            if v is not None:
                w = 0.5 ** ((k - 1) / 2); num += w * (v[1] > 0); den += w
        f_["f_ewm"] = num / den if den else 0.0
        cov = [fleet_day[d - k * one] for k in range(1, 61) if (d - k * one) in fleet_day]
        f_["f_rate60"] = sum(v[1] > 0 for v in cov) / len(cov) if cov else 0.0
        tq = [tq_day[d - k * one] for k in range(1, 4) if (d - k * one) in tq_day]
        f_["tq_frac3"] = sum(v[1] for v in tq) / sum(v[0] for v in tq) if tq else 0.0
        fn = fy = 0
        for k in range(1, PRIOR_DAYS + 1):
            v = fleet_day.get(d - k * one)
            if v is not None:
                fn += v[0]; fy += v[1]
        f_rate = min(max((fy + 1.0) / (fn + 2.0), 0.005), 0.995)
        dow = d.dayofweek
        doy = d.dayofyear
        cal = {"weekend": int(dow >= 5), "doy_sin": math.sin(2 * math.pi * doy / 365.25),
               "doy_cos": math.cos(2 * math.pi * doy / 365.25)}
        back = [d - k * one for k in range(1, ACTIVE_DAYS + 1)]
        bprior: dict = {}
        for (b, c), days_set in present.items():
            if not any(x in days_set for x in back):
                continue
            r = {"date": d, "boat": b, "cls": c, "c_am": int(c == "am"), "c_pm": int(c == "pm"),
                 "c_tw": int(c == "tw"), **cal, **f_}
            r["s_dow4"] = sum((d - 7 * k * one) in days_set for k in range(1, 5)) / 4
            r["s_14"] = sum((d - k * one) in days_set for k in range(2, 15)) / 13
            r["s_last"] = int((d - (2 if c == "tw" else 1) * one) in days_set)
            pa = [pair_ang[(b, c)][x] for x in back if x in pair_ang[(b, c)]]
            r["log_anglers28"] = math.log1p(sum(v[0] for v in pa) / sum(v[1] for v in pa)) if pa else float("nan")
            bd = boat_day[b]
            r["b_yt_last"] = int(bd[boat_last[b]][1] > 0)
            r["b_log_yt_last"] = math.log1p(bd[boat_last[b]][2])
            ys = [k for k in range(1, 61) if bd.get(d - k * one, (0, 0, 0))[1] > 0]
            r["b_log_days_since_yt"] = math.log(ys[0] if ys else 61)
            p14 = [pair_day[(b, c)][d - k * one] for k in range(1, 15) if (d - k * one) in pair_day[(b, c)]]
            r["p_frac14"] = sum(v[1] for v in p14) / sum(v[0] for v in p14) if p14 else 0.0
            pl = [x for x in (d - k * one for k in range(1, 15)) if x in pair_day[(b, c)]]
            r["p_yt_last"] = int(pair_day[(b, c)][pl[0]][1] > 0) if pl else 0
            mx = boat_mix[b][boat_last[b]]
            r["b_surface_last"] = mx[1] / mx[0]
            r["b_bottom_only_last"] = mx[2] / mx[0]
            r["b_log_anglers_last"] = math.log1p(mx[3] / mx[0])
            w7 = [bd[d - k * one] for k in range(1, 8) if (d - k * one) in bd]
            r["b_sailed7"] = int(bool(w7))
            r["b_frac7"] = sum(v[1] for v in w7) / sum(v[0] for v in w7) if w7 else 0.0
            if b not in bprior:
                bn = by = 0
                for k in range(1, PRIOR_DAYS + 1):
                    v = bd.get(d - k * one)
                    if v is not None:
                        bn += v[0]; by += v[1]
                bprior[b] = _logit(min(max((by + PRIOR_M * f_rate) / (bn + PRIOR_M), 0.005), 0.995)) - _logit(f_rate)
            r["b_prior_lr"] = bprior[b]
            for q, name in enumerate(MAIN_BOATS):
                r[f"boat_{q}"] = int(b == name)
            lb = lab.get((b, c, d))
            r["sailed"] = int(lb is not None)
            r["yt"] = int(bool(lb and lb[0]))
            r["label_at"] = events._available_at(d.date().isoformat(), PUB_CLS[c], strict)
            assert lb is None or lb[1] <= np.datetime64(r["label_at"]), (b, c, d)
            r["audit_cutoff"] = cutoff_for(d)
            rows.append(r)
    return pd.DataFrame(rows)


class _Logit:
    def __init__(self, C: float, clip: float = 4.0, kind: str = "logreg"):
        self.C, self.clip, self.kind = C, clip, kind

    def fit(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray | None = None) -> "_Logit":
        self.med = X.median().fillna(0.0)
        Xf = X.fillna(self.med)
        if self.kind == "hgb":  # D-E03: shallow boosting, same settings as the day-level HGB
            self.clf = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                      l2_regularization=1.0, random_state=0).fit(Xf.to_numpy(), y, sample_weight=w)
            return self
        self.mu, self.sd = Xf.mean(), Xf.std(ddof=0).replace(0, 1.0)
        Z = ((Xf - self.mu) / self.sd).clip(-self.clip, self.clip)
        self.clf = LogisticRegression(C=self.C, max_iter=5000).fit(Z.to_numpy(), y, sample_weight=w)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        Xf = X.fillna(self.med)
        if self.kind == "hgb":
            return self.clf.predict_proba(Xf.to_numpy())[:, 1]
        Z = ((Xf - self.mu) / self.sd).clip(-self.clip, self.clip)
        return self.clf.predict_proba(Z.to_numpy())[:, 1]


def all_days(trips: pd.DataFrame, days: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Target days plus every earlier day with a half-day report (training rows)."""
    hd_days = pd.DatetimeIndex(sorted(set(trips.loc[trips["is_hd_fishing"], "fished_date"])))
    return hd_days[hd_days <= days.max()].union(days)


def build(trips: pd.DataFrame, days: pd.DatetimeIndex, C: float = 0.1, refit_days: int = 7,
          boats: bool = False, prefix: str = "tm", strict: bool = False, min_pos: int = 30,
          rows: pd.DataFrame | None = None, kind: str = "logreg", ext: bool = False,
          halflife: float = 0.0, mix: bool = False) -> pd.DataFrame:
    """Day-level features from the trip-level models for each target day in `days`.
    kind: logreg | hgb (yt model; the sail model is always logistic); ext: add EXT_X inputs;
    halflife > 0: weight training rows by 0.5**(age at the anchor / halflife) (D-E03).
    Returns one row per day: date, {prefix}_p, _logit, _exp, _ntrips, _pymax, _psmax, audit_{prefix}_label_at."""
    days = pd.DatetimeIndex(sorted(set(days)))
    if rows is None:  # callers building several variants may pass candidate_rows(trips, all_days(...)) once
        rows = candidate_rows(trips, all_days(trips, days), strict=strict)
    # Days with a visible half-day report, and when they first became visible
    hd = trips[trips["is_hd_fishing"]]
    first_vis = hd.groupby("fished_date")["available_at"].min()
    rows["day_visible_at"] = rows["date"].map(first_vis)
    yx = YT_X + (BOAT_X if boats else []) + (EXT_X if ext else []) + (MIX_X if mix else [])
    epoch = pd.Timestamp("2000-01-03")  # a Monday; anchors are deterministic in D
    out, models = [], {}
    for D in days:
        A = D - pd.Timedelta(days=(D - epoch).days % refit_days)
        if A not in models:
            cA = cutoff_for(A)
            tr = rows[(rows["label_at"] <= cA) & (rows["day_visible_at"] <= cA)]
            sy = tr[tr["sailed"] == 1]
            ok = len(tr) and tr["sailed"].nunique() == 2 and sy["yt"].sum() >= min_pos and sy["yt"].nunique() == 2
            wt = (lambda t: 0.5 ** ((A - t["date"]).dt.days.to_numpy() / halflife)) if halflife > 0 else (lambda t: None)
            models[A] = (_Logit(C).fit(tr[SAIL_X], tr["sailed"].to_numpy(), wt(tr)),
                         _Logit(C, kind=kind).fit(sy[yx], sy["yt"].to_numpy(), wt(sy)),
                         tr["label_at"].max()) if ok else None
        cand = rows[rows["date"] == D]
        r = {"date": D}
        m = models[A]
        if m is None or not len(cand):
            r.update({f"{prefix}_p": np.nan, f"{prefix}_logit": np.nan, f"{prefix}_exp": np.nan,
                      f"{prefix}_ntrips": np.nan, f"{prefix}_pymax": np.nan, f"{prefix}_psmax": np.nan,
                      f"audit_{prefix}_label_at": pd.NaT})
        else:
            ps, py = m[0].predict(cand[SAIL_X]), m[1].predict(cand[yx])
            p = 1 - float(np.prod(1 - ps * py))
            q = min(max(p, 1e-4), 1 - 1e-4)
            r.update({f"{prefix}_p": p, f"{prefix}_logit": _logit(q), f"{prefix}_exp": float((ps * py).sum()),
                      f"{prefix}_ntrips": float(ps.sum()),
                      f"{prefix}_pymax": float(py[ps >= 0.5].max()) if (ps >= 0.5).any() else 0.0,
                      f"{prefix}_psmax": float((ps * py).max()),
                      f"audit_{prefix}_label_at": m[2]})
            assert m[2] <= cutoff_for(D)
            assert (cand["audit_cutoff"] == cutoff_for(D)).all()
        out.append(r)
    return pd.DataFrame(out)
