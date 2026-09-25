"""Daily judgment call (D-058): once a day at 21:00, in season, each LLM agent reads a compact
briefing built by the engine from data public at that moment and answers with JSON actions.

No tools, no shell: the briefing is the whole information set, so the call is point-in-time safe by
construction (every number comes from rows with available_at <= now; dates are masked). Every
briefing and answer is logged to `runs/<id>/judgment/<agent>.jsonl` for audit.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from arena.api import ctx as api
from arena.engine import calendar as cal
from arena.engine.offers import CLASSES, Offer, SOURCE_TO_CLASS

CLAUDE = shutil.which("claude") or "claude"
CLASS_NAMES = list(CLASSES)
SCHEMA = {
    "type": "object",
    "properties": {
        "book": {"type": "array", "items": {"type": "object", "properties": {
            "cls": {"type": "string", "enum": CLASS_NAMES}, "boat": {"type": "string"}, "reason": {"type": "string"}},
            "required": ["cls", "boat", "reason"]}},
        "commit_pto": {"type": "array", "items": {"type": "object", "properties": {
            "doy": {"type": "integer"}, "reason": {"type": "string"}}, "required": ["doy", "reason"]}},
        "note": {"type": "string"},
    },
    "required": ["book", "commit_pto", "note"],
}
SYSTEM = ("You are {name}, an angler in a season-long yellowtail fishing competition out of San Diego, replayed over a past "
          "season with only the information that was public at each moment. Every evening at 21:00 you decide whether to go "
          "fishing tomorrow (and which boat), and whether to reserve PTO days two or more weeks ahead. You know the rules in the "
          "briefing. Think like a real angler: go when the fishing is good or the conditions say it will be, and keep your money "
          "and PTO for those days. Your persona:\n\n{persona}\n\nAnswer with JSON only: `book` (empty list = stay home), "
          "`commit_pto` (day-of-year numbers at least 14 days ahead, empty if none), `note` (one or two lines for your own journal).")


def _fmt(x, d=2):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


class Briefer:
    """Builds briefings from the engine's unmasked tables, restricted to available_at <= now."""

    def __init__(self, raw: dict, outcomes, cfg: dict, first_year: int):
        self.raw, self.outcomes, self.cfg, self.first_year = raw, outcomes, cfg, first_year
        t = raw["trips"]
        self._trips = t[t["landing"].isin(cfg["landings"]) & t["anglers"].notna()].copy()
        self._trips["acls"] = self._trips["cls"].map(SOURCE_TO_CLASS)
        self._trips = self._trips[self._trips["acls"].notna()].sort_values("available_at")
        self._trip_av = self._trips["available_at"].to_numpy()
        self._pier = raw["pier"].sort_values("ts")
        self._pier_ts = self._pier["ts"].to_numpy()
        cl = raw["climate"]; self._oni = cl[cl["index_id"].str.lower() == "oni"].sort_values("available_at")
        self._fc = raw["forecasts"]; self._mf = raw["marine_forecasts"]; self._tides = raw["tides"]; self._fd = raw["fishdope"]

    def _vis_trips(self, now: datetime) -> pd.DataFrame:
        i = int(np.searchsorted(self._trip_av, np.datetime64(now), side="right"))
        return self._trips.iloc[:i]

    def conditions(self, now: datetime, tomorrow: date) -> dict:
        out: dict = {}
        i = int(np.searchsorted(self._pier_ts, np.datetime64(now), side="right"))
        p = self._pier.iloc[max(0, i - 24 * 15):i]
        if len(p):
            last = float(p["wtmp_c"].dropna().iloc[-1]) * 9 / 5 + 32 if p["wtmp_c"].notna().any() else None
            w7 = p[p["ts"] >= now - timedelta(days=7)]["wtmp_c"].mean(); w14 = p[(p["ts"] < now - timedelta(days=7))]["wtmp_c"].mean()
            out["pier_f_last"] = last; out["pier_f_7d"] = w7 * 9 / 5 + 32 if pd.notna(w7) else None
            out["pier_trend_f"] = (w7 - w14) * 9 / 5 if pd.notna(w7) and pd.notna(w14) else None
        o = self._oni[self._oni["available_at"] <= now]
        out["oni"] = float(o["value"].iloc[-1]) if len(o) else None
        f = self._fc[(self._fc["available_at"] <= now) & (self._fc["target_date"] == pd.Timestamp(tomorrow))]
        if len(f):
            r = f.sort_values("available_at").iloc[-1]
            out["nws"] = {"wind_kt": r["wind_kt"], "swell_ft": r["swell_ft"], "swell_s": r["swell_s"]}
        m = self._mf[(self._mf["available_at"] <= now) & (self._mf["target_date"] == pd.Timestamp(tomorrow))]
        if len(m):
            r = m.sort_values("available_at").iloc[-1]
            out["marine"] = {"wind_max_kt": r["mf_wind_max"], "gust_kt": r["mf_gust"], "seas_ft": r["mf_seas"], "offshore_wind": bool(r["mf_wind_offshore"])}
        td = self._tides[(self._tides["available_at"] <= now) & (self._tides["target_date"] == pd.Timestamp(tomorrow))]
        if len(td):
            out["tide"] = {"high_ft": float(td["tide_high_ft"].iloc[-1]), "low_ft": float(td["tide_low_ft"].iloc[-1])}
        fd = self._fd[self._fd["available_at"] <= now]
        if len(fd):
            r = fd.sort_values("available_at").iloc[-1]
            age = (now.date() - r["report_date"].date()).days
            out["fishdope"] = {"age_days": age, "yt_local": int(r.get("yt_local", 0) or 0), "yt_coronado": int(r.get("yt_coronado", 0) or 0),
                               "yt_all": int(r.get("yt_all", 0) or 0), "water_temp_local_f": (None if pd.isna(r.get("wt_local")) else float(r["wt_local"]))}
        return out

    def fleet(self, now: datetime, days: int = 7) -> tuple[list[dict], dict]:
        v = self._vis_trips(now)
        recent = v[v["fish_date"] >= pd.Timestamp(now.date() - timedelta(days=days))]
        by_day = []
        for d in sorted(recent["fish_date"].unique(), reverse=True):
            g = recent[recent["fish_date"] == d]
            row = {"day": str(api.day_of(pd.Timestamp(d).date()))}
            for c, gg in g.groupby("acls"):
                a = gg["anglers"].sum()
                row[c] = {"yt_per_angler": round(float(gg["yt"].sum() / a), 3) if a else None, "boats": int(len(gg))}
            by_day.append(row)
        m30 = v[v["fish_date"] >= pd.Timestamp(now.date() - timedelta(days=30))]
        month = {}
        for c, gg in m30.groupby("acls"):
            a = gg["anglers"].sum()
            month[c] = {"yt_per_angler_30d": round(float(gg["yt"].sum() / a), 3) if a else None, "boat_days": int(len(gg)),
                        "best_day": round(float((gg.groupby("fish_date").apply(lambda x: x["yt"].sum() / x["anglers"].sum() if x["anglers"].sum() else 0)).max()), 3) if len(gg) else None}
        return by_day, month

    def boats(self, now: datetime, cls: str, fish_date: date) -> list[dict]:
        v = self._vis_trips(now)
        out = []
        for b in self.outcomes.scheduled_boats(cls, fish_date):
            g = v[(v["boat"] == b) & (v["acls"] == cls) & (v["fish_date"] >= pd.Timestamp(now.date() - timedelta(days=14)))]
            a = g["anglers"].sum()
            out.append({"boat": b, "trips_14d": int(len(g)), "yt_per_angler_14d": round(float(g["yt"].sum() / a), 3) if a else None,
                        "last_trip": str(api.day_of(g["fish_date"].max().date())) if len(g) else None,
                        "last_yt": int(g.sort_values("fish_date")["yt"].iloc[-1]) if len(g) else None})
        return out

    def typical(self, cls: str, fish_date: date) -> float | None:
        return self.outcomes.climatology(cls, fish_date, int(self.cfg.get("climatology_window_days", 15)))


def build_briefing(br: Briefer, now: datetime, agent: dict, offers: list[Offer], offers_api: list[api.Offer],
                   state: dict, leaderboard: list[dict], forum: list[dict] | None) -> str:
    """`state`: budget, pto, pto_committed (list of Day str), upcoming (list), results (last 5), rejected (list),
    journal (list of str), notes (str), describe (str)."""
    tomorrow = now.date() + timedelta(days=1)
    day, tday = api.day_of(now.date()), api.day_of(tomorrow)
    L = [f"# Tonight: {day} (a {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day.weekday]}) 21:00. Tomorrow is {tday} ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][tday.weekday]}{', federal holiday' if tday.is_holiday else ''}).",
         f"Budget ${state['budget']:.0f}, PTO {state['pto']:g} day(s) left. PTO committed for: {', '.join(state['pto_committed']) or 'none'}.",
         f"Upcoming booked trips: {'; '.join(state['upcoming']) or 'none'}.",
         "", "## Rules (short)",
         "- Book a specific boat from tomorrow's schedule. Your score = that boat's yellowtail (kept+released) / (its anglers + other competitors aboard). Season score = sum over your trips.",
         "- Weekday trips need PTO committed >= 14 days ahead for each weekday fished (and the return day for overnight/1.5-day); weekends, holidays and twilight trips need none. PTO is deducted when committed and never refunded.",
         "- Prices: HD_AM/HD_PM/TWILIGHT $80, THREE_QUARTER $150, FULL_DAY $275, OVERNIGHT $400 (fishes the day after departure), DAY_1_5 $550 (fishes the day after departure, back the morning after that). Nothing carries over to next season.",
         "", "## Tomorrow's offers"]
    for o, oa in zip(offers, offers_api):
        tc = CLASSES[o.cls]
        fd = o.fishing_dates[0]
        typ = br.typical(o.cls, fd)
        boats = br.boats(now, o.cls, fd)
        L.append(f"- {o.cls} (${o.cost}; fishes {api.day_of(fd)}; PTO needed: {', '.join(str(api.day_of(d)) for d in o.pto_need) or 'none'}; "
                 f"{'BOOKABLE' if oa.bookable else 'not bookable: ' + oa.reason}). Typical for this class at this time of year in past seasons: {_fmt(typ, 3)} yt/angler.")
        if boats:
            L.append("    scheduled boats: " + "; ".join(f"{b['boat']} ({b['trips_14d']} trips/14d, {_fmt(b['yt_per_angler_14d'], 3)} yt/angler, last {b['last_trip'] or '—'}: {b['last_yt'] if b['last_yt'] is not None else '—'} yt)" for b in boats))
        else:
            L.append("    scheduled boats: none (cannot be booked)")
    by_day, month = br.fleet(now)
    L += ["", "## Fleet results, last 7 days (yellowtail per angler, pooled over all boats of the class; boats in parentheses)"]
    if by_day:
        for row in by_day:
            L.append("- " + row["day"] + ": " + ", ".join(f"{c} {_fmt(v['yt_per_angler'], 3)} ({v['boats']})" for c, v in row.items() if c != "day"))
    else:
        L.append("- no trips reported in the last 7 days")
    if month:
        L.append("Last 30 days: " + ", ".join(f"{c} {_fmt(v['yt_per_angler_30d'], 3)} yt/angler over {v['boat_days']} boat-days (best day {_fmt(v['best_day'], 3)})" for c, v in month.items()))
    c = br.conditions(now, tomorrow)
    L += ["", "## Conditions"]
    if "pier_f_last" in c:
        L.append(f"- Scripps Pier water: {_fmt(c['pier_f_last'], 1)} °F now, 7-day mean {_fmt(c.get('pier_f_7d'), 1)} °F, trend vs prior week {'+' if (c.get('pier_trend_f') or 0) >= 0 else ''}{_fmt(c.get('pier_trend_f'), 1)} °F")
    L.append(f"- ONI (ENSO index, latest published): {_fmt(c.get('oni'), 1)}")
    if "nws" in c:
        L.append(f"- NWS forecast for tomorrow: wind {_fmt(c['nws']['wind_kt'], 0)} kt, swell {_fmt(c['nws']['swell_ft'], 1)} ft @ {_fmt(c['nws']['swell_s'], 0)} s")
    if "marine" in c:
        L.append(f"- Coastal waters forecast: wind to {_fmt(c['marine']['wind_max_kt'], 0)} kt (gusts {_fmt(c['marine']['gust_kt'], 0)}), seas {_fmt(c['marine']['seas_ft'], 1)} ft{', offshore wind' if c['marine']['offshore_wind'] else ''}")
    if "tide" in c:
        L.append(f"- Tides tomorrow: high {_fmt(c['tide']['high_ft'], 1)} ft, low {_fmt(c['tide']['low_ft'], 1)} ft")
    if "fishdope" in c:
        f = c["fishdope"]
        L.append(f"- Latest fishing report ({f['age_days']} day(s) old): yellowtail mentions local {f['yt_local']}, Coronados {f['yt_coronado']}, all areas {f['yt_all']}; stated local water temp {_fmt(f['water_temp_local_f'], 0)} °F")
    L += ["", "## Your recent trips"]
    L += [f"- {r}" for r in state["results"]] or ["- none yet this season"]
    if state["rejected"]:
        L += ["", "## Actions rejected since your last decision (fix these)"] + [f"- {r}" for r in state["rejected"]]
    L += ["", "## Leaderboard (season score, rank)"] + [f"- {r['name']}: {r['season_fish']:.2f} (#{r['season_rank']})" for r in leaderboard[:6]]
    me = next((r for r in leaderboard if r["name"] == agent["name"]), None)
    if me and me["season_rank"] > 6:
        L.append(f"- you ({agent['name']}): {me['season_fish']:.2f} (#{me['season_rank']})")
    if forum:
        L += ["", "## Forum, latest posts"] + [f"- {p['agent']} ({p['post_id']}): {p['text'][:280]}" for p in forum[-3:]]
    if state["describe"]:
        L += ["", "## Your standing code strategy (runs automatically every day; you may add to it tonight)", state["describe"][:600]]
    if state["journal"]:
        L += ["", "## Your journal (latest last)"] + [f"- {j}" for j in state["journal"][-8:]]
    if state["notes"]:
        L += ["", "## Your notes (from your last planning turn)", state["notes"][:2500]]
    L += ["", "Decide: which of tomorrow's offers to book (with the boat), which weekdays >= 14 days out to commit PTO for (day-of-year numbers), and a one-line journal note. Empty lists mean stay home / commit nothing."]
    return "\n".join(L)


def call_model(prompt: str, system: str, model: str, work_dir: Path, budget_usd: float, timeout_s: int) -> dict:
    cfg_dir = work_dir / "claude-config"
    shutil.rmtree(cfg_dir, ignore_errors=True); cfg_dir.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("ARENA_")}
    env["CLAUDE_CONFIG_DIR"] = str(cfg_dir); env.pop("CLAUDE_CODE_SESSION_ID", None)
    cmd = [CLAUDE, "-p", prompt, "--system-prompt", system, "--model", model, "--output-format", "json", "--max-turns", "1",
           "--tools", "", "--no-session-persistence", "--setting-sources", "", "--max-budget-usd", str(budget_usd),
           "--json-schema", json.dumps(SCHEMA)]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, timeout=timeout_s, env=env)
        try:
            c = json.loads(r.stdout)
        except json.JSONDecodeError:
            c = None
        out = {"exit": r.returncode, "seconds": round(time.time() - t0, 1), "cost_usd": float((c or {}).get("total_cost_usd") or 0.0),
               "answer": (c or {}).get("structured_output"), "error": None if (c and not c.get("is_error")) else (r.stderr[-500:] or (c or {}).get("result") or "no output")[:500]}
        if out["answer"] is None and c and c.get("result"):
            try:
                out["answer"] = json.loads(c["result"])
            except (json.JSONDecodeError, TypeError):
                out["error"] = out["error"] or "answer is not JSON"
    except subprocess.TimeoutExpired:
        out = {"exit": -1, "seconds": round(time.time() - t0, 1), "cost_usd": 0.0, "answer": None, "error": f"timeout after {timeout_s}s"}
    shutil.rmtree(cfg_dir, ignore_errors=True)
    return out


def answer_to_actions(answer: dict, offers: list[Offer], today: date) -> list:
    """JSON answer -> actions (validated later by the engine like any other action)."""
    acts = []
    by_cls = {o.cls: o for o in offers}
    for b in (answer or {}).get("book", []) or []:
        o = by_cls.get(str(b.get("cls", "")))
        if o is None:
            continue
        acts.append(api.Book(o.id, str(b.get("reason", ""))[:300], boat=str(b.get("boat", "")).strip()))
    for p in (answer or {}).get("commit_pto", []) or []:
        try:
            doy = int(p.get("doy"))
        except (TypeError, ValueError):
            continue
        d = date(today.year, 1, 1) + timedelta(days=doy - 1)
        if d.year != today.year:
            continue
        acts.append(api.CommitPTO(api.day_of(d), str(p.get("reason", ""))[:300]))
    return acts


def run_calls(jobs: list[dict], parallel: int, budget_usd: float, timeout_s: int) -> dict[str, dict]:
    """jobs: [{name, prompt, system, model, work_dir}] -> {name: call result}"""
    def one(j):
        return j["name"], call_model(j["prompt"], j["system"], j["model"], Path(j["work_dir"]), budget_usd, timeout_s)
    with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        return dict(ex.map(one, jobs))
