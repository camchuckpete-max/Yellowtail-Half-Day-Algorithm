"""Arena no-lookahead proof (SPEC §4.4): poisoning every row with available_at > now must not
change any strategy's actions. Extends the method of tests/test_pit.py to the arena's ctx.

pytest: 20 random ticks per season over PIT_SEASONS (default 2012-2013) for every scripted baseline.
CLI:    python3 -m arena.tests.test_pit_arena --run arena/runs/<id> [--ticks 20]   (every strategy of a run, all its seasons)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pytest

from arena.api import ctx as api
from arena.engine import calendar as cal, offers as off
from arena.engine.pit import Tables
from arena.engine.sandbox import load_strategy

ROOT = Path(__file__).resolve().parents[2]
PRICES = {"HD_AM": 80, "HD_PM": 80, "TWILIGHT": 80, "THREE_QUARTER": 150, "FULL_DAY": 275, "OVERNIGHT": 400, "DAY_1_5": 550}


def snapshot_dir() -> Path:
    """Reuse the newest run snapshot if one exists; otherwise build one under cache/."""
    cands = sorted(p for p in (ROOT / "arena" / "runs").glob("*/tables/meta.json"))
    if cands:
        return cands[-1].parent
    out = ROOT / "cache" / "arena_snapshot"
    if not (out / "meta.json").exists():
        from yt import source
        from arena.api import snapshot
        db = source.open_db(source.source_manifest())
        snapshot.write_snapshot(snapshot.load_raw_tables(db), out, 2010, True)
    return out


def make_ctx(tables: Tables, now: datetime, rng_seed: int) -> api.Ctx:
    day = api.day_of(now.date())
    tick = now.strftime("%H:%M")
    offers = []
    for o in off.offers_at(now.date(), tick, PRICES, 1.0):
        need = list(o.pto_need.items())
        offers.append(api.Offer(o.id, o.cls, api.day_of(o.departure), tuple(api.day_of(f) for f in o.fishing_dates),
                                api.day_of(o.return_at.date()), o.return_at.hour, o.cost, tuple(api.day_of(d) for d, _ in need),
                                need[0][1] if need else 0.0, not need, "PTO not committed" if need else ""))
    t = cal.t_of(now)
    return api.Ctx(api.Now(day, now.hour, t), offers, 2000.0, 10.0, api.Calendar(), lambda n: tables.visible(n, t),
                   lambda d: {}, lambda limit=50: [], [], [], np.random.default_rng(rng_seed), tables.names, 2000.0, 10.0)


def random_ticks(years, n, rng):
    out = []
    for y in years:
        start = date(y, 5, 1) if y == 2010 else date(y, 1, 1)
        days = (date(y, 12, 31) - start).days
        for k in rng.choice(days, n, replace=False):
            d = start + __import__("datetime").timedelta(days=int(k))
            out.append(datetime.combine(d, cal.parse_tick("16:00" if rng.random() < 0.5 else "21:00")))
    return out


def check(strategies: dict, tables: Tables, ticks, seed: int = 7) -> int:
    api.configure(2010, True)
    rng = np.random.default_rng(seed)
    n = 0
    for now in ticks:
        t = cal.t_of(now)
        pois = tables.poisoned(t, rng)
        for name, s in strategies.items():
            a = s.decide(make_ctx(tables, now, 1))
            b = s.decide(make_ctx(pois, now, 1))
            assert a == b, f"{name} at {now}: {a} != {b}"
            n += 1
    return n


@pytest.fixture(scope="module")
def tables():
    return Tables(snapshot_dir())


def test_baselines_are_pit(tables):
    years = [int(y) for y in os.environ.get("PIT_SEASONS", "2012-2013").split("-")]
    years = list(range(years[0], years[-1] + 1))
    src = ROOT / "arena" / "agents" / "_scripted" / "baselines.py"
    strategies = {n: load_strategy(src, n) for n in ("B_SAT", "B_PERSIST", "B_TEMP", "B_BIG")}
    ticks = random_ticks(years, 20, np.random.default_rng(11))
    assert check(strategies, tables, ticks) == len(ticks) * len(strategies)


def test_visible_prefix_is_strict(tables):
    t = cal.t_of(datetime(2015, 8, 1, 21))
    for name in tables.names:
        v = tables.visible(name, t)
        assert (v["avail_t"] <= t).all()
        rest = tables.table(name).iloc[len(v):]
        assert (rest["avail_t"] > t).all()


def test_masked_columns_only(tables):
    for name in tables.names:
        cols = tables.table(name).columns
        assert not any(c.endswith("_iso") or c in ("available_at", "ts", "fished_date", "fish_date", "return_date", "date") for c in cols), (name, list(cols))
        assert "avail_t" in cols and "avail_season" in cols


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ticks", type=int, default=20)
    a = ap.parse_args(argv)
    run = Path(a.run) if Path(a.run).exists() else ROOT / "arena" / "runs" / a.run
    cfg = __import__("yaml").safe_load((run / "config.yaml").read_text())
    ck = json.loads((run / "checkpoint.json").read_text())
    strategies = {ag["name"]: load_strategy(Path(ag["path"]), ag["class_name"]) for ag in ck["agents"]}
    years = list(range(int(cfg["seasons"]["first"]), min(ck["season_year"], int(cfg["seasons"]["last"])) + 1))
    tables = Tables(run / "tables")
    ticks = random_ticks(years, a.ticks, np.random.default_rng(11))
    n = check(strategies, tables, ticks)
    print(f"PIT ok: {n} strategy-ticks, {len(strategies)} strategies, seasons {years[0]}-{years[-1]}")


if __name__ == "__main__":
    main()
