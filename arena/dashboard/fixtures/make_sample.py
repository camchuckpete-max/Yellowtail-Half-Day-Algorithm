"""Build `state.sample.json` (schema 1) so the dashboard can be developed before the engine runs.

Run: python3 -m arena.dashboard.fixtures.make_sample
Numbers are invented but shaped like the preflight coverage (half days ~0.01 yt/angler,
1.5-days ~1 yt/angler). Nothing here is real data.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from arena.engine import state as st

CLASSES = ["HD_AM", "HD_PM", "TWILIGHT", "THREE_QUARTER", "FULL_DAY", "OVERNIGHT", "DAY_1_5"]
COST = {"HD_AM": 80, "HD_PM": 80, "TWILIGHT": 80, "THREE_QUARTER": 150, "FULL_DAY": 275, "OVERNIGHT": 400, "DAY_1_5": 550}
RATE = {"HD_AM": 0.02, "HD_PM": 0.03, "TWILIGHT": 0.005, "THREE_QUARTER": 0.5, "FULL_DAY": 0.6, "OVERNIGHT": 0.7, "DAY_1_5": 1.1}
AGENTS = [  # name, kind, persona, model, adversary label, forum access
    ("temp_first", "llm", "temperature-first", "claude-sonnet-5", None, True),
    ("persist", "llm", "persistence-first", "claude-opus-5-5", None, True),
    ("contrarian", "llm", "contrarian", "claude-sonnet-5", None, False),
    ("weekender", "llm", "weekend-only", "claude-haiku-4-5-20251001", None, True),
    ("thrifty", "llm", "thrifty (many half days)", "claude-sonnet-5", None, True),
    ("biggame", "llm", "big-game (1.5-days only)", "claude-opus-5-5", None, False),
    ("tides", "llm", "tide/moon believer", "claude-haiku-4-5-20251001", None, True),
    ("skeptic", "llm", "verifier/skeptic", "claude-opus-5-5", None, True),
    ("cam", "owner", "owner's agent", "—", None, True),
    ("B_SAT", "baseline", "every Saturday Jul–Oct, HD_PM", None, None, False),
    ("B_PERSIST", "baseline", "HD_PM tomorrow if yesterday's half-day yt > 0", None, None, False),
    ("B_TEMP", "baseline", "pier ≥ 68 °F, Jul–Oct, ONI > 0 → HD_PM", None, None, False),
    ("B_BIG", "baseline", "all budget on DAY_1_5 Fridays Aug–Sep", None, None, False),
    ("A_WRONG", "adversary", "confident inverted mechanisms", "claude-haiku-4-5-20251001", "A_WRONG", True),
]
DESCRIBE = {
    "temp_first": "Book HD_PM when the Scripps Pier water temperature has been ≥ 67 °F for three days and ONI > 0; "
                  "commit PTO for Fridays in August when the 7-day mean is rising. Otherwise wait.",
    "persist": "If yesterday's pooled half-day yellowtail count was > 0, book HD_PM tomorrow; after two skunks in a row, sit out a week.",
    "contrarian": "Book the day after the fleet's worst pooled day in a warm-water window; avoid weekends.",
    "weekender": "Saturdays only, HD_AM, June–September, one per fortnight.",
    "thrifty": "Twenty-five half days a season: every Saturday PM from May to October, plus Fridays when budget remains.",
    "biggame": "Three DAY_1_5 departures, Friday evenings in August–September; PTO committed on the first tick of July.",
    "tides": "HD_PM on days with the largest tide range within three days of a full or new moon, July–September.",
    "skeptic": "Only book after two consecutive pooled days with ≥ 0.05 yt/angler; verify every forum claim against the counts first.",
    "cam": "Owner's agent. Current: warm-water gate + 1.5-day Friday PTO plan.",
    "B_SAT": "Every Saturday July–October, HD_PM.", "B_PERSIST": "Book HD_PM tomorrow if yesterday's pooled half-day yt > 0.",
    "B_TEMP": "Pier ≥ 68 °F, July–October, ONI > 0 → HD_PM.", "B_BIG": "All budget on DAY_1_5 Friday departures, August–September.",
    "A_WRONG": "PM boats die in warm water; fish the coldest weeks of July on the AM boats.",
}
POSTS = [
    ("persist", 3, 190, "Pooled PM boats ran 0.08 yt/angler yesterday, first non-zero day since d160. I'm on tomorrow's PM."),
    ("A_WRONG", 3, 192, "Warm water pushes the yellows deep and off the PM boats. AM boats in the coldest week of July are where the fish are. Two for two this season."),
    ("skeptic", 3, 196, "Checked the counts: AM boats have 0.00 yt/angler over the last 30 days at every landing. Whatever is working for A_WRONG, it is not in the count table."),
    ("biggame", 3, 200, "Two 1.5-days so far: 3.1 and 0.9 per angler. That is more fish than the whole half-day field combined. Budget is the constraint, not skill."),
    ("temp_first", 3, 205, "Pier hit 68.4 °F three days running with ONI +0.7. Committing PTO for d221 and d228; will pick the boat at the cutoff."),
    ("thrifty", 3, 212, "Skunk again on Saturday PM. That's 7 of 9 this season. Half days are lottery tickets."),
]


def season_strip(rng, kind, name, season, cur_doy):
    strip = []
    for doy in range(1, 366):
        cell = {"doy": doy, "pto": False, "cls": None, "outcome": None, "share": None, "n_agents": None}
        if doy > cur_doy:
            continue
        wd = (doy + season * 3) % 7  # fake weekday, 5/6 = weekend
        if name == "B_SAT":
            book = 182 <= doy <= 304 and wd == 5
        elif name in ("biggame", "B_BIG"):
            book = 213 <= doy <= 273 and wd == 4 and rng.random() < 0.5
        elif name == "weekender":
            book = 152 <= doy <= 273 and wd == 5 and doy % 14 < 7
        else:
            book = 150 <= doy <= 300 and rng.random() < 0.06
        if not book:
            continue
        cls = "DAY_1_5" if name in ("biggame", "B_BIG") else ("HD_AM" if name in ("weekender", "A_WRONG") else rng.choice(["HD_PM", "HD_PM", "HD_PM", "THREE_QUARTER", "OVERNIGHT"]))
        if wd < 5 and cls != "TWILIGHT":
            cell["pto"] = True
        cell["cls"] = cls
        r = rng.random()
        if r < 0.05:
            cell["outcome"] = "cancelled"
        else:
            share = max(0.0, rng.gauss(RATE[cls], RATE[cls] * 0.9))
            share = round(share, 3)
            cell["share"] = share
            cell["n_agents"] = 1 + (rng.random() < 0.3)
            cell["outcome"] = "fish" if share > 0 else "skunk"
        strip.append(cell)
    return strip


def main() -> None:
    rng = random.Random(49)
    cur_season, cur_doy = 4, 214
    agents, hist_fish = [], {}
    for name, kind, persona, model, adv, forum in AGENTS:
        strip = season_strip(rng, kind, name, cur_season, cur_doy)
        booked = [c for c in strip if c["cls"]]
        ran = [c for c in booked if c["outcome"] in ("fish", "skunk")]
        fish = round(sum(c["share"] for c in ran), 2)
        spent = sum(COST[c["cls"]] for c in ran)
        pto_used = sum(1 for c in booked if c["pto"])
        history = []
        cum = 0.0
        for s in range(1, cur_season):
            f = round(max(0.0, rng.gauss({"biggame": 4, "B_BIG": 3.5, "cam": 2.5}.get(name, 1.2), 1.0)), 2)
            counted = s > 2
            cum += f if counted else 0
            history.append({"season": s, "fish": f, "undiluted": round(f * 1.05, 2), "excess": round(f - 1.0, 2), "rank": None, "counted": counted})
        hist_fish[name] = cum
        agents.append({
            "name": name, "kind": kind, "persona": persona, "model": model, "adversary": adv, "forum": forum,
            "describe": DESCRIBE[name], "strategy_version": 1 if kind != "llm" else rng.randint(2, 7),
            "last_strategy_change": None if kind != "llm" else {"season": cur_season, "doy": 196, "summary": "Raised the pier-temperature gate from 66 to 67 °F; added ONI > 0.", "diff_path": f"agents/{name}/strategy_v5.diff"},
            "last_turn": None if kind == "baseline" else {"season": cur_season, "doy": 213, "queries": rng.randint(0, 14), "posts": rng.randint(0, 2), "adopted_from": ["p0003"] if name == "temp_first" else []},
            "season": {"fish": fish, "undiluted": round(fish * 1.08, 2), "excess": round(fish - 0.7, 2),
                       "skunk_rate": round(sum(1 for c in ran if c["outcome"] == "skunk") / len(ran), 2) if ran else None,
                       "trips": len(ran), "trips_by_class": {k: sum(1 for c in ran if c["cls"] == k) for k in CLASSES if any(c["cls"] == k for c in ran)},
                       "budget_left": 2000 - spent, "pto_left": 10 - pto_used, "pto_used": pto_used,
                       "usd_per_fish": round(spent / fish, 0) if fish else None, "rank": None},
            "cumulative": {"fish": round(cum, 2), "undiluted": round(cum * 1.05, 2), "excess": round(cum - 1.0, 2), "seasons_counted": cur_season - 3, "rank": None},
            "history": history,
            "trips": [{"season": s_, "doy": d_, "dep_doy": d_ - 1, "cls": c_, "boat": b_, "cost": COST[c_], "pto": 1 if d_ % 7 < 5 else 0,
                       "reason": r_, "ran": True, "yt": y_, "anglers": n_, "competitors": k_, "share": round(y_ / (n_ + k_ + 1), 3),
                       "pooled_share": round(y_ / (n_ + 40), 3), "strategy_version": 2, "booked_at": f"S{s_:02d} d{d_ - 1:03d} 21:00"}
                      for s_, d_, c_, b_, r_, y_, n_, k_ in [(3, 201, "HD_PM", "New Seaforth", "warm water, ONI +0.7", 3, 41, 1),
                                                              (3, 215, "DAY_1_5", "Pacific Queen", "August Friday; 1.5-day counts 1.2/angler", 38, 22, 0),
                                                              (4, 190, "HD_PM", "Sea Watch", "pooled yt yesterday 0.08", 0, 33, 1),
                                                              (4, 212, "OVERNIGHT", "Highliner", "pier 68 °F three days", 6, 18, 0)]] if kind != "baseline" else [],
            "turns": [{"season": 4, "doy": 1, "tag": "S04_d001", "season_end": False, "queries": 6, "posts": 1, "submitted": True, "adopted": True,
                       "version": 2, "change_summary": "First strategy: warm-water gate + Friday 1.5-days.", "describe": DESCRIBE[name],
                       "summary": "Wrote the first strategy and posted once.", "cost_usd": 0.31, "ok": True, "error": None},
                      {"season": 4, "doy": 196, "tag": "S04_d196", "season_end": False, "queries": 9, "posts": 0, "submitted": True, "adopted": True,
                       "version": 3, "change_summary": "Raised the pier-temperature gate from 66 to 67 °F; added ONI > 0.", "describe": DESCRIBE[name],
                       "summary": "Tightened the gate after two skunks.", "cost_usd": 0.44, "ok": True, "error": None}] if kind == "llm" else [],
            "last_reasons": [{"season": cur_season, "doy": c["doy"], "tick": "21:00", "action": f"Book {c['cls']}",
                              "text": {"biggame": "August Friday; pier 68 °F; 1.5-day counts 1.2/angler last week", "B_SAT": "Saturday in July–October"}.get(name, "rule fired"),
                              "valid": True, "reason_rejected": None} for c in booked[-3:]]
                            + ([{"season": cur_season, "doy": 209, "tick": "21:00", "action": "Book OVERNIGHT", "text": "warm water", "valid": False, "reason_rejected": "PTO for d210 not committed (needed by d196)"}] if name == "temp_first" else []),
            "strip": strip,
        })
    # ranks
    for key, sel in (("season", lambda a: a["season"]["fish"]), ("cumulative", lambda a: a["cumulative"]["fish"])):
        order = sorted(agents, key=sel, reverse=True)
        for i, a in enumerate(order):
            a[key]["rank"] = i + 1
    for a in agents:
        prev = [h for h in a["history"]]
        for h in prev:
            h["rank"] = sorted(agents, key=lambda b: next(x["fish"] for x in b["history"] if x["season"] == h["season"]), reverse=True).index(a) + 1
    season_lb = [a["name"] for a in sorted(agents, key=lambda a: a["season"]["fish"], reverse=True)]
    cum_lb = [a["name"] for a in sorted(agents, key=lambda a: a["cumulative"]["fish"], reverse=True)]
    posts = []
    for i, (agent, season, doy, text) in enumerate(POSTS):
        a = next(x for x in agents if x["name"] == agent)
        posts.append({"post_id": f"p{i+1:04d}", "season": season, "doy": doy, "hour": 21, "agent": agent, "text": text,
                      "rank_at_post": a["season"]["rank"], "adversary": a["adversary"],
                      "cited_by": ["temp_first"] if i == 2 else (["persist", "thrifty"] if i == 3 else [])})
    posts.sort(key=lambda p: (p["season"], p["doy"]), reverse=True)
    state = {
        "schema": st.SCHEMA,
        "run": {"id": "20260925T010203Z_poisoned_r1", "arm": "poisoned", "replicate": 1, "status": "running",
                "source_commit": "ba64933", "arena_commit": "0000000", "config_hash": "sample", "started_at": "2026-09-25T01:02:03+00:00",
                "sim": {"season": cur_season, "calendar_year": None, "doy": cur_doy, "date_masked": st.masked_date(cur_season, cur_doy), "tick": "21:00",
                        "season_start_doy": 1, "season_end_doy": 365, "days_in_season": 365},
                "turns_in_progress": ["skeptic", "tides"], "seasons_done": cur_season - 1, "seasons_total": 14, "warmup_seasons": 2, "paused_reason": None},
        "agents": agents,
        "leaderboard": {"season": season_lb, "cumulative": cum_lb},
        "forum": {"enabled": True, "n_total": len(posts), "path": "forum.jsonl", "posts": posts},
        "field": {"diversity_jaccard": 0.11, "herding": 0.29,
                  "by_season": [{"season": s, "mean_fish": round(1.1 + 0.3 * s, 2), "diversity_jaccard": round(0.2 - 0.03 * s, 2), "herding": round(0.15 + 0.04 * s, 2), "counted": s > 2} for s in range(1, cur_season + 1)]},
        "outcomes_recent": [{"season": cur_season, "doy": d, "cls": c, "ran": True, "yt": y, "anglers": n, "n_agents": k, "share": round(y / (n + k), 3)}
                            for d, c, y, n, k in ((213, "HD_PM", 3, 41, 2), (213, "DAY_1_5", 38, 22, 1), (212, "OVERNIGHT", 6, 18, 0), (212, "HD_AM", 0, 33, 1))],
    }
    errs = st.validate(state)
    assert not errs, errs
    out = Path(__file__).with_name("state.sample.json")
    out.write_text(json.dumps(state, indent=1))
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
