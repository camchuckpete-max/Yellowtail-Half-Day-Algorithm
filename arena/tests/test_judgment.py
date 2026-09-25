"""Daily judgment (D-058): the briefing is built only from rows public at `now` (poison test), and
JSON answers map to validated actions."""
from __future__ import annotations

from datetime import date, datetime

import numpy as np
import pandas as pd
import pytest

from arena.api import ctx as api, snapshot
from arena.engine import judgment as jm, offers as off, scoring
from yt import source

CFG = {"landings": ["seaforth", "fishermans", "hm", "point_loma"], "climatology_window_days": 15}
PRICES = {"HD_AM": 80, "HD_PM": 80, "TWILIGHT": 80, "THREE_QUARTER": 150, "FULL_DAY": 275, "OVERNIGHT": 400, "DAY_1_5": 550}


@pytest.fixture(scope="module")
def raw():
    db = source.open_db(source.source_manifest())
    return snapshot.load_raw_tables(db)


def _state():
    return {"budget": 1500.0, "pto": 8.0, "pto_committed": [], "upcoming": [], "results": [], "rejected": [], "journal": [], "notes": "", "describe": ""}


def _offers(now):
    raw_offers = off.offers_for_judgment(now.date(), PRICES, 1.0)
    offers_api = [api.Offer(o.id, o.cls, api.day_of(o.departure), tuple(api.day_of(f) for f in o.fishing_dates), api.day_of(o.return_at.date()),
                            o.return_at.hour, o.cost, tuple(api.day_of(d) for d in o.pto_need), 1.0 if o.pto_need else 0.0, not o.pto_need,
                            "PTO not committed" if o.pto_need else "") for o in raw_offers]
    return raw_offers, offers_api


def _poison(raw, now, rng):
    out = {}
    for name, df in raw.items():
        df = df.copy()
        after = df["available_at"] > pd.Timestamp(now)
        for c in df.columns:
            if c in ("available_at",) or not after.any():
                continue
            if pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c]):
                df.loc[after, c] = pd.Series(rng.uniform(1, 400, after.sum()), index=df.index[after]).astype(df[c].dtype)
            elif df[c].dtype == object:
                df.loc[after, c] = "POISON"
        out[name] = df
    return out


def test_briefing_is_point_in_time(raw):
    api.configure(2010, True)
    outcomes = scoring.Outcomes(raw["trips"], CFG["landings"], "all")
    rng = np.random.default_rng(3)
    for now in (datetime(2015, 8, 1, 21), datetime(2011, 6, 15, 21), datetime(2019, 10, 3, 21)):
        raw_offers, offers_api = _offers(now)
        lb = [{"name": "x", "season_fish": 1.0, "season_rank": 1}]
        a = jm.build_briefing(jm.Briefer(raw, outcomes, CFG, 2010), now, {"name": "x"}, raw_offers, offers_api, _state(), lb, None)
        b = jm.build_briefing(jm.Briefer(_poison(raw, now, rng), outcomes, CFG, 2010), now, {"name": "x"}, raw_offers, offers_api, _state(), lb, None)
        assert a == b, now
        assert "20" not in "".join(ch for ch in a if ch.isdigit())[:0]  # placeholder; explicit check below
        assert "2015" not in a and "2011" not in a and "2019" not in a   # masked
        assert "Tomorrow's offers" in a and "scheduled boats" in a and "Typical for this class" in a


def test_answer_to_actions():
    api.configure(2010, True)
    now = datetime(2015, 8, 1, 21)
    raw_offers, _ = _offers(now)
    ans = {"book": [{"cls": "HD_PM", "boat": "New Seaforth", "reason": "hot"}, {"cls": "NOPE", "boat": "x", "reason": ""}],
           "commit_pto": [{"doy": 240, "reason": "fall"}, {"doy": "bad", "reason": ""}, {"doy": 400, "reason": ""}], "note": "n"}
    acts = jm.answer_to_actions(ans, raw_offers, now.date())
    assert len(acts) == 2 and isinstance(acts[0], api.Book) and acts[0].boat == "New Seaforth" and acts[0].offer_id.startswith("HD_PM:")
    assert isinstance(acts[1], api.CommitPTO) and acts[1].day.doy == 240 and acts[1].day.season == 6
    assert jm.answer_to_actions(None, raw_offers, now.date()) == []
