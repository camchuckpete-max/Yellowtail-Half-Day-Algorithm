"""Outcomes, shares, climatology, season and field metrics, bootstrap CIs (SPEC §3.3, §3.4, §7)."""
from __future__ import annotations

from datetime import date
from itertools import combinations

import numpy as np
import pandas as pd

from .offers import CLASSES


class Outcomes:
    """Pooled outcomes from the UNMASKED trips table (engine side only)."""

    def __init__(self, trips: pd.DataFrame, landings: list[str], pooled_boats, count_released: bool = True):
        t = trips[trips["landing"].isin(landings) & trips["anglers"].notna()]
        if isinstance(pooled_boats, (list, tuple)):
            t = t[t["boat"].isin(pooled_boats)]
        t = t.copy()
        t["arena_cls"] = t["cls"].map({s: c.name for c in CLASSES.values() for s in c.source_cls})
        t = t[t["arena_cls"].notna()]
        if not count_released:
            raise NotImplementedError("count_released=false needs kept/released split in load_trips")
        g = t.groupby(["arena_cls", "fish_date"]).agg(yt=("yt", "sum"), anglers=("anglers", "sum"), n_boats=("yt", "size"))
        self.pooled = {(c, d.date()): (float(y), float(a), int(n)) for (c, d), y, a, n in
                       zip(g.index, g["yt"], g["anglers"], g["n_boats"])}
        self.by_cls = {c: grp.assign(doy=grp["fish_date"].dt.dayofyear, year=grp["fish_date"].dt.year)
                       for c, grp in t.groupby("arena_cls")}
        self._clim: dict = {}

    def pooled_outcome(self, cls: str, fish_date: date) -> tuple[float, float, int] | None:
        return self.pooled.get((cls, fish_date))

    def climatology(self, cls: str, fish_date: date, window: int = 15) -> float | None:
        """Pooled yt per angler for (cls, doy +- window) over seasons strictly before fish_date.year."""
        key = (cls, fish_date.year, fish_date.timetuple().tm_yday)
        if key not in self._clim:
            g = self.by_cls.get(cls)
            val = None
            if g is not None:
                doy = key[2]
                dd = (g["doy"] - doy).abs()
                dd = np.minimum(dd, 365 - dd)
                m = (dd <= window) & (g["year"] < fish_date.year)
                a = float(g.loc[m, "anglers"].sum())
                val = float(g.loc[m, "yt"].sum()) / a if a > 0 else None
            self._clim[key] = val
        return self._clim[key]


def share(yt: float, anglers: float, n_agents: int, w: float) -> float:
    return yt / (anglers + w * n_agents)


def season_metrics(bookings: list[dict], climatology, budget: float, pto: float) -> dict:
    ran = [b for b in bookings if b["settled"] and b["ran"]]
    fish = sum(b["share"] for b in ran)
    undiluted = sum(b["yt"] / b["anglers"] for b in ran if b["anglers"])
    clim = [climatology(b["cls"], b["fishing_dates"][0]) for b in ran]
    excess = sum(b["share"] - (c if c is not None else 0.0) for b, c in zip(ran, clim))
    spent = sum(b["cost"] for b in ran)
    by_cls: dict[str, int] = {}
    for b in ran:
        by_cls[b["cls"]] = by_cls.get(b["cls"], 0) + 1
    return {"fish": round(fish, 4), "undiluted": round(undiluted, 4), "excess": round(excess, 4),
            "skunk_rate": round(sum(1 for b in ran if b["yt"] == 0) / len(ran), 4) if ran else None,
            "trips": len(ran), "trips_by_class": by_cls, "cancelled": sum(1 for b in bookings if b["settled"] and not b["ran"]),
            "usd_per_fish": round(spent / fish, 1) if fish > 0 else None, "spent": spent}


def field_metrics(picks: dict[str, set], n_agents_per_trip: dict) -> dict:
    """picks: agent -> set of (cls, departure) this season; n_agents_per_trip: (cls, departure) -> count."""
    names = [n for n in picks]
    jac = []
    for a, b in combinations(names, 2):
        u = picks[a] | picks[b]
        jac.append(len(picks[a] & picks[b]) / len(u) if u else 0.0)
    herd = max(n_agents_per_trip.values(), default=0) / len(names) if names else None
    return {"diversity_jaccard": round(float(np.mean(jac)), 4) if jac else None, "herding": round(herd, 4) if herd is not None else None}


def bootstrap_diff_ci(a: list[float], b: list[float], n: int = 4000, seed: int = 0) -> dict:
    """Resample seasons with replacement (paired) for mean(a - b)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(a) != len(b):
        return {"mean": None, "lo95": None, "hi95": None, "n_seasons": int(len(a))}
    rng = np.random.default_rng(seed)
    d = a - b
    idx = rng.integers(0, len(d), (n, len(d)))
    means = d[idx].mean(axis=1)
    return {"mean": float(d.mean()), "lo95": float(np.percentile(means, 2.5)), "hi95": float(np.percentile(means, 97.5)), "n_seasons": int(len(d))}
