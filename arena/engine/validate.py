"""`submit_strategy` validation (SPEC §5.3): allowlist + syntax + describe() + calendar audit +
crash/poison test on a sample of past ticks against the turn's PIT snapshot."""
from __future__ import annotations

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from arena.api import ctx as api
from arena.engine import calendar as cal, offers as off
from arena.engine.pit import Tables
from arena.engine.sandbox import check_source, load_strategy
from arena.tools.audit_strategy import audit

MAX_DESCRIBE_WORDS = 200
PRICES = {"HD_AM": 80, "HD_PM": 80, "TWILIGHT": 80, "THREE_QUARTER": 150, "FULL_DAY": 275, "OVERNIGHT": 400, "DAY_1_5": 550}


def make_ctx(tables: Tables, now: datetime, seed: int = 1, prices: dict | None = None) -> api.Ctx:
    """A plain ctx (full budget, empty calendar) at `now` over `tables`; used by tests and validation."""
    prices = prices or PRICES
    day = api.day_of(now.date())
    tick = now.strftime("%H:%M")
    offers = []
    for o in off.offers_at(now.date(), tick, prices, 1.0):
        need = list(o.pto_need.items())
        offers.append(api.Offer(o.id, o.cls, api.day_of(o.departure), tuple(api.day_of(f) for f in o.fishing_dates),
                                api.day_of(o.return_at.date()), o.return_at.hour, o.cost, tuple(api.day_of(d) for d, _ in need),
                                need[0][1] if need else 0.0, not need, "PTO not committed" if need else ""))
    t = cal.t_of(now)
    return api.Ctx(api.Now(day, now.hour, t), offers, 2000.0, 10.0, api.Calendar(), lambda n: tables.visible(n, t),
                   lambda d: {}, lambda limit=50: [], [], [], np.random.default_rng(seed), tables.names, 2000.0, 10.0)


def sample_ticks(now_t: float, n: int, rng: np.random.Generator, span_days: int = 730) -> list[datetime]:
    """Random past ticks within `span_days` before now (never after now)."""
    out = []
    for k in rng.uniform(1, span_days, n):
        d = cal.from_day_number(int(now_t - k))
        out.append(datetime.combine(d, cal.parse_tick("16:00" if rng.random() < 0.5 else "21:00")))
    return sorted(out)


def validate_strategy(code: str, snapshot: Path, cfg: dict, n_ticks: int = 8, seed: int = 3) -> dict:
    api.configure(int(cfg["first_year"]), bool(cfg.get("mask_years", True)))
    errs = check_source(code)
    if errs:
        return {"ok": False, "reason": "disallowed code", "details": errs}
    hard, warns = audit(code)
    if hard:
        return {"ok": False, "reason": "calendar leakage", "details": hard}
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = Path(f.name)
    try:
        strat = load_strategy(path, "Strategy")
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"could not load: {type(e).__name__}: {e}"}
    finally:
        path.unlink(missing_ok=True)
    try:
        desc = str(strat.describe())
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"describe() raised {type(e).__name__}: {e}"}
    if not desc.strip():
        return {"ok": False, "reason": "describe() is empty"}
    if len(desc.split()) > MAX_DESCRIBE_WORDS:
        return {"ok": False, "reason": f"describe() has {len(desc.split())} words; the limit is {MAX_DESCRIBE_WORDS}"}
    tables = Tables(Path(snapshot))
    rng = np.random.default_rng(seed)
    ticks = sample_ticks(float(cfg["now"]["t"]), n_ticks, rng)
    try:
        strat.on_turn(make_ctx(tables, ticks[0]))
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"on_turn() raised {type(e).__name__}: {e}"}
    for now in ticks:
        try:
            acts = strat.decide(make_ctx(tables, now))
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reason": f"decide() raised {type(e).__name__}: {e} at season {api.day_of(now.date()).season} day {api.day_of(now.date()).doy} {now.hour:02d}:00"}
        if acts is not None and not isinstance(acts, (list, tuple)):
            return {"ok": False, "reason": f"decide() must return a list of actions, got {type(acts).__name__}"}
        for a in acts or []:
            if not isinstance(a, (api.Book, api.CommitPTO)):
                return {"ok": False, "reason": f"decide() returned a non-action: {a!r}"}
        # no-lookahead: poisoning every row public after `now` must not change the actions
        pois = tables.poisoned(cal.t_of(now), rng)
        try:
            acts2 = strat.decide(make_ctx(pois, now))
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reason": f"decide() depends on data not yet public (raised {type(e).__name__} when future rows were poisoned)"}
        if list(acts or []) != list(acts2 or []):
            return {"ok": False, "reason": "decide() changed its actions when rows not yet public were poisoned: it reads beyond available_at <= now"}
    return {"ok": True, "describe": desc, "warnings": warns}
