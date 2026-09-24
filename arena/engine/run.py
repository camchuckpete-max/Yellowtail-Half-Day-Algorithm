"""Arena engine: the tick loop (SPEC §2–§4, §8, §9).

    python -m arena.run --config arena/configs/default.yaml --arm isolated --replicate 1
    python -m arena.run --resume arena/runs/<id>

The run pauses at every season end (`status: paused_season_end`) until resumed; `--no-pause`
plays every configured season in one go (development). Runs from uncommitted code are refused
unless `--dev` (run dir under `arena/runs/dev_*`, git-ignored).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from yt import events, features, source
from arena.api import ctx as api
from arena.api import snapshot
from arena.engine import calendar as cal
from arena.engine import offers as off
from arena.engine import scoring, state as st
from arena.engine.sandbox import Worker

ROOT = Path(__file__).resolve().parents[2]
ARENA = ROOT / "arena"
SCRIPTED = ARENA / "agents" / "_scripted"
HOLDOUT_START = date(2024, 1, 1)  # D-033


def _git(*args) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def _hash_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _hash_dir(p: Path, pattern: str = "*.md") -> str:
    h = hashlib.sha256()
    for f in sorted(p.glob(pattern)) if p.exists() else []:
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _jsonl(path: Path, rec: dict) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


class Agent:
    def __init__(self, name: str, kind: str, path: Path, class_name: str, adversary: str | None = None,
                 persona: str | None = None, model: str | None = None):
        self.name, self.kind, self.path, self.class_name = name, kind, Path(path), class_name
        self.adversary, self.persona, self.model = adversary, persona, model
        self.budget = 0.0
        self.pto = 0.0
        self.pto_committed: dict[str, float] = {}      # iso date -> amount
        self.bookings: list[dict] = []                 # this season
        self.history: list[dict] = []                  # per season
        self.last_reasons: list[dict] = []
        self.failures: list[dict] = []                 # engine rejections / exceptions since last turn
        self.describe = ""
        self.strategy_version = 1
        self.worker: Worker | None = None

    def to_json(self) -> dict:
        return {k: getattr(self, k) for k in ("name", "kind", "class_name", "adversary", "persona", "model", "budget", "pto",
                                              "pto_committed", "bookings", "history", "last_reasons", "failures", "describe",
                                              "strategy_version")} | {"path": str(self.path)}

    @classmethod
    def from_json(cls, d: dict) -> "Agent":
        a = cls(d["name"], d["kind"], Path(d["path"]), d["class_name"], d.get("adversary"), d.get("persona"), d.get("model"))
        for k in ("budget", "pto", "pto_committed", "bookings", "history", "last_reasons", "failures", "describe", "strategy_version"):
            setattr(a, k, d[k])
        return a


class Engine:
    def __init__(self, run_dir: Path, cfg: dict, arm: str, replicate: int, publish_every: float | None = None,
                 no_pause: bool = False, quiet: bool = False, tables_from: Path | None = None):
        self.dir = Path(run_dir)
        self.cfg, self.arm, self.replicate = cfg, arm, replicate
        self.publish_every, self.no_pause, self.quiet = publish_every, no_pause, quiet
        self.first_year = int(cfg["seasons"]["first"])
        self.first_start = pd.Timestamp(cfg["seasons"]["first_start"]).date()
        self.last_year = int(cfg["seasons"]["last"])
        self.tick_times = [cal.parse_tick(t) for t in cfg["ticks"]]
        self.prices = cfg["prices"]
        api.configure(self.first_year, bool(cfg.get("mask_years", True)))
        self.agents: list[Agent] = []
        self.forum: list[dict] = []
        self.season_year = self.first_year
        self.cursor: tuple[str, str] | None = None     # (iso date, tick) of the NEXT tick to play
        self.status = "running"
        self.paused_reason = None
        self.interventions: list[dict] = []
        self.last_publish = 0.0
        self.outcomes_recent: list[dict] = []
        self.field_by_season: list[dict] = []
        self._raw = None
        self._features_cache: dict = {}
        self.tables_from = tables_from

    # ---------------------------------------------------------------- setup
    def load_data(self) -> dict:
        manifest = source.source_manifest()
        db = source.open_db(manifest)
        self._raw = snapshot.load_raw_tables(db)
        db.close()
        landings = list(self.cfg["landings"])
        self.outcomes = scoring.Outcomes(self._raw["trips"], landings, self.cfg.get("pooled_boats", "all"),
                                         bool(self.cfg.get("count_released", True)))
        snap = self.dir / "tables"
        if self.tables_from and not snap.exists():
            snap.symlink_to(Path(self.tables_from).resolve())   # dev shortcut: reuse an existing snapshot
        if not (snap / "meta.json").exists():
            snapshot.write_snapshot(self._raw, snap, self.first_year, bool(self.cfg.get("mask_years", True)))
        # unmasked frames for features_day (engine side only)
        self._fd_inputs = (self._raw["trips"].assign(is_hd_fishing=self._raw["trips"]["cls"].isin(features.HD_FISH_CLASSES)),
                           self._raw["forecasts"], self._raw["fishdope"].drop(columns=["text"]),
                           self._raw["marine_forecasts"], self._raw["tides"], self._raw["ocean"])
        return manifest

    def build_field(self) -> None:
        labels = json.loads((SCRIPTED / "labels.json").read_text())
        f = self.cfg["field"]
        for n in f.get("baselines", []):
            self.agents.append(Agent(n, "baseline", SCRIPTED / "baselines.py", n))
        if self.cfg["arms"][self.arm].get("adversaries"):
            adv_path = SCRIPTED / "adversaries.py"
            if not adv_path.exists():
                raise SystemExit("poisoned arm needs arena/agents/_scripted/adversaries.py (Phase 4)")
            for n in f.get("adversaries", []):
                self.agents.append(Agent(n, "adversary", adv_path, n, adversary=labels[n]["adversary"]))
        for n in list(f.get("agents", [])) + ([f["owner"]] if f.get("owner") else []):
            d = ARENA / "agents" / n
            meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
            self.agents.append(Agent(n, "owner" if n == f.get("owner") else "llm", d / "strategy.py", "Strategy",
                                     persona=meta.get("persona"), model=meta.get("model")))
        for a in self.agents:
            a.budget, a.pto = float(self.cfg["budget"]), float(self.cfg["pto"])

    def start_workers(self) -> None:
        seed = int(self.cfg.get("seed", 0)) * 1000 + self.replicate
        for a in self.agents:
            aseed = int(hashlib.sha256(f"{seed}:{a.name}".encode()).hexdigest()[:8], 16)
            a.worker = Worker(a.name, a.path, a.class_name, self.dir / "tables", aseed, self.first_year,
                              bool(self.cfg.get("mask_years", True)), self.features_day, self.cfg["timeouts"])
            a.describe = a.worker.describe
            (self.dir / "agents" / a.name).mkdir(parents=True, exist_ok=True)
            shutil.copy(a.path, self.dir / "agents" / a.name / f"strategy_v{a.strategy_version}.py")

    def stop_workers(self) -> None:
        for a in self.agents:
            if a.worker:
                a.worker.stop()

    # ---------------------------------------------------------------- helpers
    def features_day(self, day: api.Day) -> dict:
        d = pd.Timestamp(api.to_date(day))
        if d not in self._features_cache:
            row = features.build(self._fd_inputs[0], self._fd_inputs[1], pd.DatetimeIndex([d]), *self._fd_inputs[2:]).iloc[0].to_dict()
            self._features_cache = {d: {k: v for k, v in row.items() if k in features.FEATURES}}  # masked: no date/audit columns
        return self._features_cache[d]

    def _api_offer(self, o: off.Offer, a: Agent, bookable_now: dict) -> api.Offer:
        ok, why = True, ""
        need = list(o.pto_need.items())
        if self.cfg["pto_mode"] == "commit_day":
            missing = [d for d, amt in need if a.pto_committed.get(d.isoformat(), 0.0) + 1e-9 < amt]
            if missing:
                ok, why = False, "PTO not committed for " + ", ".join(str(api.day_of(d)) for d in missing)
        else:  # commit_trip: PTO deducted at booking; trips needing PTO must be booked >= lead days ahead
            total = sum(amt for _, amt in need)
            if total > 0 and (o.departure - bookable_now["today"]).days < int(self.cfg["pto_lead_days"]):
                ok, why = False, f"needs {total:g} PTO day(s): must be booked ≥ {self.cfg['pto_lead_days']} days ahead"
            elif total > a.pto + 1e-9:
                ok, why = False, "not enough PTO"
        if ok and o.cost > a.budget + 1e-9:
            ok, why = False, f"budget ${a.budget:.0f} < ${o.cost}"
        if ok:
            fds = {f.isoformat() for f in o.fishing_dates}
            booked = [b for b in a.bookings if set(b["fishing_dates"]) & fds]
            if len(booked) >= int(self.cfg["max_trips_per_day"]):
                ok, why = False, "already booked for that fishing date"
        return api.Offer(id=o.id, cls=o.cls, departure=api.day_of(o.departure),
                         fishing_dates=tuple(api.day_of(f) for f in o.fishing_dates),
                         return_day=api.day_of(o.return_at.date()), return_hour=o.return_at.hour + o.return_at.minute / 60,
                         cost=o.cost, pto_dates=tuple(api.day_of(d) for d, _ in need),
                         pto_need=need[0][1] if need else 0.0, bookable=ok, reason=why)

    def _booking_api(self, b: dict) -> api.Booking:
        return api.Booking(offer_id=b["offer_id"], cls=b["cls"], departure=api.day_of(date.fromisoformat(b["departure"])),
                           fishing_dates=tuple(api.day_of(date.fromisoformat(f)) for f in b["fishing_dates"]), cost=b["cost"],
                           settled=b["settled"], ran=b.get("ran"), yt=b.get("yt"), anglers=b.get("anglers"),
                           n_agents=b.get("n_agents"), share=b.get("share"))

    def _calendar_api(self, a: Agent) -> api.Calendar:
        return api.Calendar(pto_committed={api.day_of(date.fromisoformat(d)): v for d, v in a.pto_committed.items()},
                            booked=[self._booking_api(b) for b in a.bookings])

    def _leaderboard(self) -> list[dict]:
        rows = []
        for a in self.agents:
            sf = sum(b["share"] for b in a.bookings if b["settled"] and b["ran"])
            cf = sum(h["fish"] for h in a.history if h["counted"])
            rows.append({"name": a.name, "season_fish": round(sf, 4), "cumulative_fish": round(cf, 4)})
        rows.sort(key=lambda r: r["season_fish"], reverse=True)
        for i, r in enumerate(rows):
            r["season_rank"] = i + 1
        for i, r in enumerate(sorted(rows, key=lambda r: r["cumulative_fish"], reverse=True)):
            r["cumulative_rank"] = i + 1
        return rows

    def _masked_results(self, a: Agent) -> list[dict]:
        out = []
        for b in a.bookings:
            if b["settled"]:
                out.append({"offer_id": b["offer_id"], "cls": b["cls"], "departure": str(api.day_of(date.fromisoformat(b["departure"]))),
                            "ran": b["ran"], "yt": b["yt"], "anglers": b["anglers"], "n_agents": b["n_agents"], "share": b["share"]})
        return out

    def _forum_visible(self, t: float) -> list[dict]:
        if not self.cfg["arms"][self.arm].get("forum"):
            return []
        return [p for p in self.forum if p["t"] <= t]

    # ---------------------------------------------------------------- tick
    def settle(self, now: datetime) -> None:
        w = float(self.cfg["agent_angler_weight"])
        for a in self.agents:
            for b in a.bookings:
                if b["settled"] or datetime.fromisoformat(b["return_at"]) > now:
                    continue
                key = (b["cls"], b["departure"])
                n_agents = sum(1 for x in self.agents for y in x.bookings if (y["cls"], y["departure"]) == key)
                po = self.outcomes.pooled_outcome(b["cls"], date.fromisoformat(b["fishing_dates"][0]))
                b["settled"] = True
                b["n_agents"] = n_agents
                if po is None:
                    b["ran"] = False
                    a.budget += b["cost"]   # fare refunded, PTO stays spent (§3.3)
                    b["yt"] = b["anglers"] = b["share"] = None
                else:
                    yt, anglers, _ = po
                    b["ran"], b["yt"], b["anglers"] = True, yt, anglers
                    b["share"] = round(scoring.share(yt, anglers, n_agents, w), 6)
                fd = date.fromisoformat(b["fishing_dates"][0])
                rec = {"season": self.season_year, "season_idx": api.day_of(fd).season, "doy": api.day_of(fd).doy,
                       "date": fd.isoformat(), "agent": a.name, "cls": b["cls"], "ran": b["ran"], "yt": b["yt"],
                       "anglers": b["anglers"], "n_agents": n_agents, "share": b["share"]}
                _jsonl(self.dir / "outcomes.jsonl", rec)
                self.outcomes_recent = ([rec] + self.outcomes_recent)[:20]

    def tick(self, today: date, tick: str) -> None:
        now = datetime.combine(today, cal.parse_tick(tick))
        t = cal.t_of(now)
        self.settle(now)
        day = api.day_of(today)
        nowobj = api.Now(day=day, hour=now.hour, t=t)
        lb = self._leaderboard()
        raw_offers = off.offers_at(today, tick, self.prices, float(self.cfg["half_day_pto"]))
        is_turn = tick == "21:00" and (today.day in self.cfg["turn_days"] or today == cal.season_bounds(self.season_year, self.first_year, self.first_start)[0])
        for a in self.agents:
            if a.worker is None:
                continue
            offers = [self._api_offer(o, a, {"today": today}) for o in raw_offers]
            msg = {"now": nowobj, "offers": offers, "budget_left": a.budget, "pto_left": a.pto,
                   "calendar": self._calendar_api(a), "forum": self._forum_visible(t), "leaderboard": lb,
                   "my_results": self._masked_results(a), "budget_total": float(self.cfg["budget"]), "pto_total": float(self.cfg["pto"])}
            if is_turn:
                res, err = a.worker.call("on_turn", msg)
                if err:
                    a.failures.append({"date": str(day), "tick": tick, "kind": "on_turn", "error": err})
                    _jsonl(self.dir / "decisions.jsonl", {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name, "kind": "on_turn", "error": err})
                elif res:
                    a.describe = res
            acts, err = a.worker.call("decide", msg)
            if err:
                a.failures.append({"date": str(day), "tick": tick, "kind": "decide", "error": err})
                _jsonl(self.dir / "decisions.jsonl", {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name, "kind": "decide", "error": err})
                continue
            for act in acts:
                self.apply(a, act, today, tick, day, {o.id: o for o in raw_offers})
        self.write_state(now, tick)

    def apply(self, a: Agent, act, today: date, tick: str, day: api.Day, raw_offers: dict) -> None:
        valid, why, label = True, "", ""
        if isinstance(act, api.CommitPTO):
            label = f"CommitPTO {act.day}"
            d = api.to_date(act.day)
            if self.cfg["pto_mode"] != "commit_day":
                valid, why = False, "pto_mode is commit_trip: PTO is charged at booking"
            elif (d - today).days < int(self.cfg["pto_lead_days"]):
                valid, why = False, f"must commit ≥ {self.cfg['pto_lead_days']} days ahead"
            elif d.year != self.season_year:
                valid, why = False, "outside this season"
            elif not cal.is_weekday(d):
                valid, why = False, "not a weekday (no PTO needed)"
            elif act.amount <= 0 or act.amount > a.pto + 1e-9:
                valid, why = False, f"PTO left {a.pto:g} < {act.amount:g}"
            else:
                a.pto -= act.amount
                a.pto_committed[d.isoformat()] = a.pto_committed.get(d.isoformat(), 0.0) + act.amount
        elif isinstance(act, api.Book):
            label = f"Book {act.offer_id}"
            o = raw_offers.get(act.offer_id)
            if o is None:
                valid, why = False, "no such offer at this tick"
            else:
                ao = self._api_offer(o, a, {"today": today})
                if not ao.bookable:
                    valid, why = False, ao.reason
                else:
                    a.budget -= o.cost
                    if self.cfg["pto_mode"] == "commit_trip":
                        a.pto -= sum(o.pto_need.values())
                    a.bookings.append({"offer_id": o.id, "cls": o.cls, "departure": o.departure.isoformat(),
                                       "fishing_dates": [f.isoformat() for f in o.fishing_dates], "return_at": o.return_at.isoformat(),
                                       "cost": o.cost, "pto": sum(o.pto_need.values()), "settled": False, "reason": act.reason,
                                       "booked_at": f"{today.isoformat()} {tick}"})
        else:
            valid, why, label = False, "unknown action", str(act)
        rec = {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name, "action": label,
               "reason": getattr(act, "reason", ""), "valid": valid, "rejected": why or None}
        _jsonl(self.dir / "decisions.jsonl", rec)
        a.last_reasons = (a.last_reasons + [{"season": day.season, "doy": day.doy, "tick": tick, "action": label,
                                             "text": getattr(act, "reason", ""), "valid": valid, "reason_rejected": why or None}])[-8:]
        if not valid:
            a.failures.append({"date": str(day), "tick": tick, "kind": "rejected", "action": label, "error": why})

    # ---------------------------------------------------------------- season
    def season_end(self) -> None:
        self.settle(datetime(self.season_year + 1, 12, 31))  # every booked trip of this season has returned
        counted = self.season_year - self.first_year >= int(self.cfg["warmup_seasons"])
        picks, per_trip = {}, {}
        for a in self.agents:
            picks[a.name] = {(b["cls"], b["departure"]) for b in a.bookings if b["ran"]}
            for k in picks[a.name]:
                per_trip[k] = per_trip.get(k, 0) + 1
        field = scoring.field_metrics(picks, per_trip)
        rows = []
        for a in self.agents:
            m = scoring.season_metrics(a.bookings, lambda c, d: self.outcomes.climatology(c, date.fromisoformat(d), int(self.cfg["climatology_window_days"])),
                                       float(self.cfg["budget"]), float(self.cfg["pto"]))
            m.update({"season": self.season_year, "season_idx": self.season_year - self.first_year + 1, "counted": counted,
                      "pto_used": round(float(self.cfg["pto"]) - a.pto, 2), "budget_left": round(a.budget, 2), "agent": a.name})
            rows.append(m)
        rows.sort(key=lambda r: r["fish"], reverse=True)
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        for a in self.agents:
            r = next(x for x in rows if x["agent"] == a.name)
            a.history.append(r)
        mean_fish = float(np.mean([r["fish"] for r in rows])) if rows else None
        self.field_by_season.append({"season": self.season_year - self.first_year + 1, "mean_fish": round(mean_fish, 4) if mean_fish is not None else None, **field, "counted": counted})
        (self.dir / "results").mkdir(exist_ok=True)
        (self.dir / "results" / f"season_{self.season_year}.json").write_text(json.dumps({"season": self.season_year, "counted": counted, "agents": rows, "field": field}, indent=1))
        self.write_metrics()

    def season_reset(self) -> None:
        """Budget and PTO reset; notes / strategies / history carry over (§3.5)."""
        for a in self.agents:
            a.bookings, a.pto_committed = [], {}
            a.budget, a.pto = float(self.cfg["budget"]), float(self.cfg["pto"])
        self.outcomes_recent = []

    def write_metrics(self) -> None:
        names = [a.name for a in self.agents]
        by = {a.name: [h["fish"] for h in a.history if h["counted"]] for a in self.agents}
        cis = {}
        base = [a.name for a in self.agents if a.kind == "baseline"]
        for n in names:
            for b in base:
                if n != b and by[n] and len(by[n]) == len(by[b]):
                    cis[f"{n}-{b}"] = scoring.bootstrap_diff_ci(by[n], by[b], seed=int(self.cfg.get("seed", 0)))
        out = {"run": self.dir.name, "arm": self.arm, "replicate": self.replicate, "seasons_counted": len(next(iter(by.values()), [])),
               "cumulative": {n: round(sum(v), 4) for n, v in by.items()},
               "leaderboard_cumulative": sorted(names, key=lambda n: sum(by[n]), reverse=True),
               "ci_vs_baselines": cis, "field_by_season": self.field_by_season}
        (self.dir / "results" / "metrics.json").write_text(json.dumps(out, indent=1))

    # ---------------------------------------------------------------- state / checkpoint
    def write_state(self, now: datetime, tick: str, status: str | None = None) -> None:
        status = status or self.status
        lb = self._leaderboard()
        rank = {r["name"]: r for r in lb}
        day = api.day_of(now.date())
        start, end = cal.season_bounds(self.season_year, self.first_year, self.first_start)
        agents = []
        for a in self.agents:
            settled = [b for b in a.bookings if b["settled"] and b["ran"]]
            fish = sum(b["share"] for b in settled)
            spent = sum(b["cost"] for b in settled)
            cum = sum(h["fish"] for h in a.history if h["counted"])
            strip = []
            for d, amt in a.pto_committed.items():
                dd = api.day_of(date.fromisoformat(d))
                if dd.season == day.season and not any(d in b["fishing_dates"] for b in a.bookings):
                    strip.append({"doy": dd.doy, "pto": True, "cls": None, "outcome": None, "share": None, "n_agents": None})
            for b in a.bookings:
                dd = api.day_of(date.fromisoformat(b["fishing_dates"][0]))
                strip.append({"doy": dd.doy, "pto": b["pto"] > 0, "cls": b["cls"],
                              "outcome": ("fish" if b.get("yt") else "skunk") if b["settled"] and b["ran"] else ("cancelled" if b["settled"] else "pending"),
                              "share": b.get("share"), "n_agents": b.get("n_agents")})
            by_cls: dict[str, int] = {}
            for b in settled:
                by_cls[b["cls"]] = by_cls.get(b["cls"], 0) + 1
            agents.append({
                "name": a.name, "kind": a.kind, "persona": a.persona, "model": a.model, "adversary": a.adversary,
                "describe": a.describe, "strategy_version": a.strategy_version, "last_strategy_change": None, "last_turn": None,
                "season": {"fish": round(fish, 4), "undiluted": round(sum(b["yt"] / b["anglers"] for b in settled if b["anglers"]), 4),
                           "excess": round(sum(b["share"] - (self.outcomes.climatology(b["cls"], date.fromisoformat(b["fishing_dates"][0])) or 0.0) for b in settled), 4),
                           "skunk_rate": round(sum(1 for b in settled if not b["yt"]) / len(settled), 4) if settled else None,
                           "trips": len(settled), "trips_by_class": by_cls, "budget_left": round(a.budget, 2), "pto_left": round(a.pto, 2),
                           "pto_used": round(float(self.cfg["pto"]) - a.pto, 2), "usd_per_fish": round(spent / fish, 1) if fish > 0 else None,
                           "rank": rank[a.name]["season_rank"]},
                "cumulative": {"fish": round(cum, 4), "undiluted": round(sum(h["undiluted"] for h in a.history if h["counted"]), 4),
                               "excess": round(sum(h["excess"] for h in a.history if h["counted"]), 4),
                               "seasons_counted": sum(1 for h in a.history if h["counted"]), "rank": rank[a.name]["cumulative_rank"]},
                "history": [{"season": h["season_idx"], "fish": h["fish"], "undiluted": h["undiluted"], "excess": h["excess"], "rank": h["rank"], "counted": h["counted"]} for h in a.history],
                "last_reasons": a.last_reasons, "strip": strip})
        state = {
            "schema": st.SCHEMA,
            "run": {"id": self.dir.name, "arm": self.arm, "replicate": self.replicate, "status": status,
                    "source_commit": self.manifest.get("source_commit", ""), "arena_commit": self.manifest.get("arena_commit", ""),
                    "config_hash": self.manifest.get("config_hash", ""), "started_at": self.manifest.get("started_at", ""),
                    "sim": {"season": day.season, "calendar_year": now.year,
                            "doy": day.doy, "date_masked": str(day), "tick": tick, "season_start_doy": start.timetuple().tm_yday,
                            "season_end_doy": end.timetuple().tm_yday, "days_in_season": cal.days_in_year(self.season_year)},
                    "turns_in_progress": [], "seasons_done": self.season_year - self.first_year, "seasons_total": self.last_year - self.first_year + 1,
                    "warmup_seasons": int(self.cfg["warmup_seasons"]), "paused_reason": self.paused_reason, "interventions": self.interventions},
            "agents": agents,
            "leaderboard": {"season": [r["name"] for r in lb], "cumulative": [r["name"] for r in sorted(lb, key=lambda r: r["cumulative_rank"])]},
            "forum": {"enabled": bool(self.cfg["arms"][self.arm].get("forum")), "n_total": len(self.forum), "path": "forum.jsonl",
                      "posts": list(reversed(self.forum[-st.FORUM_INLINE_POSTS:]))},
            "field": {**(self.field_by_season[-1] if self.field_by_season else {"diversity_jaccard": None, "herding": None}), "by_season": self.field_by_season},
            "outcomes_recent": [{"season": o["season_idx"], "doy": o["doy"], "cls": o["cls"], "ran": o["ran"], "yt": o["yt"], "anglers": o["anglers"], "n_agents": o["n_agents"], "share": o["share"], "agent": o["agent"]} for o in self.outcomes_recent],
        }
        state["field"].pop("season", None); state["field"].pop("mean_fish", None); state["field"].pop("counted", None)
        st.write_atomic(self.dir / "live" / "state.json", state)
        self.maybe_publish(force=status != "running")

    def maybe_publish(self, force: bool = False) -> None:
        if self.publish_every is None:
            return
        if not force and time.time() - self.last_publish < self.publish_every * 60:
            return
        self.last_publish = time.time()
        rel = str((self.dir / "live" / "state.json").relative_to(ROOT))
        for cmd in (["add", rel], ["commit", "-q", "-m", f"arena live state {self.dir.name}", "--", rel], ["push", "-q"]):
            r = subprocess.run(["git", "-C", str(ROOT), *cmd], capture_output=True, text=True)
            if r.returncode and cmd[0] != "commit":
                print("publish:", cmd[0], r.stderr.strip()[:200], file=sys.stderr)
                return

    def checkpoint(self) -> None:
        data = {"season_year": self.season_year, "cursor": self.cursor, "status": self.status, "paused_reason": self.paused_reason,
                "agents": [a.to_json() for a in self.agents], "forum": self.forum, "interventions": self.interventions,
                "outcomes_recent": self.outcomes_recent, "field_by_season": self.field_by_season, "arm": self.arm,
                "replicate": self.replicate, "publish_every": self.publish_every}
        tmp = self.dir / "checkpoint.tmp"
        tmp.write_text(json.dumps(data, default=str))
        tmp.replace(self.dir / "checkpoint.json")

    def restore(self) -> None:
        data = json.loads((self.dir / "checkpoint.json").read_text())
        self.season_year = data["season_year"]
        self.cursor = tuple(data["cursor"]) if data["cursor"] else None
        self.status, self.paused_reason = data["status"], data["paused_reason"]
        self.agents = [Agent.from_json(a) for a in data["agents"]]
        self.forum, self.interventions = data["forum"], data["interventions"]
        self.outcomes_recent, self.field_by_season = data["outcomes_recent"], data["field_by_season"]
        self.manifest = json.loads((self.dir / "manifest.json").read_text())

    # ---------------------------------------------------------------- main loop
    def play(self) -> str:
        """Play until the next season end (or the end of the last season). Returns the final status."""
        try:
            while self.season_year <= self.last_year:
                ticks = list(cal.ticks_of_season(self.season_year, self.first_year, self.first_start, self.tick_times))
                if self.cursor:
                    cd, ct = date.fromisoformat(self.cursor[0]), self.cursor[1]
                    ticks = [(d, t) for d, t in ticks if (d, t.strftime("%H:%M")) >= (cd, ct)]
                elif self.season_year > self.first_year:
                    self.season_reset()   # a fresh season starts (also right after a resume from a season-end pause)
                t0 = time.time()
                for i, (d, t) in enumerate(ticks):
                    self.tick(d, t.strftime("%H:%M"))
                    self.cursor = (d.isoformat(), t.strftime("%H:%M"))
                    if not self.quiet and i % 200 == 0:
                        print(f"  {d} {t.strftime('%H:%M')}  ({time.time() - t0:.0f}s)", flush=True)
                self.season_end()
                done_year = self.season_year
                self.season_year += 1
                self.cursor = None
                self.status = "finished" if self.season_year > self.last_year else "paused_season_end"
                self.paused_reason = None if self.status == "finished" else f"season {done_year - self.first_year + 1} ({done_year}) ended; resume with --resume {self.dir.name}"
                self.write_state(datetime(done_year, 12, 31, 21), "21:00", status=self.status)
                self.checkpoint()
                if not self.quiet:
                    print(f"season {done_year} done: " + ", ".join(f"{h['agent']} {h['fish']:.2f}" for h in sorted((a.history[-1] for a in self.agents), key=lambda h: -h["fish"])), flush=True)
                if self.status == "paused_season_end" and not self.no_pause:
                    return self.status
                self.status = "running"
            return "finished"
        finally:
            self.stop_workers()


def load_config(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text())


def new_run(cfg_path: Path, arm: str, replicate: int, dev: bool, seasons: str | None, holdout: bool) -> tuple[Path, dict]:
    cfg = load_config(cfg_path)
    if arm not in cfg["arms"]:
        raise SystemExit(f"unknown arm {arm}; arms: {list(cfg['arms'])}")
    if seasons:
        a, b = seasons.split("-")
        cfg["seasons"]["first"], cfg["seasons"]["last"] = int(a), int(b)
    if int(cfg["seasons"]["last"]) >= HOLDOUT_START.year and not holdout:
        raise SystemExit(f"seasons.last >= {HOLDOUT_START.year} touches the holdout (D-033); pass --holdout to log the access (SPEC §12 #1)")
    head, dirty = _git("rev-parse", "HEAD"), bool(_git("status", "--porcelain", "arena", "yt"))
    if (not head or dirty) and not dev:
        raise SystemExit("refusing to run from uncommitted code (commit arena/ and yt/ first, or use --dev)")
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = ARENA / "runs" / (("dev_" if dev else "") + f"{ts}_{arm}_r{replicate}")
    run_dir.mkdir(parents=True)
    (run_dir / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))   # effective config, overrides applied
    if holdout:
        with open(ROOT / "holdout_access.log", "a") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z arena {run_dir.name} seasons {cfg['seasons']['first']}-{cfg['seasons']['last']}\n")
    return run_dir, cfg


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ARENA / "configs" / "default.yaml"))
    ap.add_argument("--arm", default="isolated")
    ap.add_argument("--replicate", type=int, default=1)
    ap.add_argument("--resume", help="run id or path under arena/runs to resume")
    ap.add_argument("--seasons", help="override, e.g. 2010-2012")
    ap.add_argument("--no-pause", action="store_true", help="do not pause at season ends")
    ap.add_argument("--publish-every", type=float, help="minutes between git commit+push of live/state.json")
    ap.add_argument("--dev", action="store_true", help="allow uncommitted code; run dir prefixed dev_")
    ap.add_argument("--holdout", action="store_true", help="allow seasons >= 2024 (logged in holdout_access.log)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--tables", help="dev: reuse the parquet snapshot of another run dir (symlinked)")
    a = ap.parse_args(argv)

    if a.resume:
        run_dir = Path(a.resume) if Path(a.resume).exists() else ARENA / "runs" / a.resume
        cfg = load_config(run_dir / "config.yaml")
        ck = json.loads((run_dir / "checkpoint.json").read_text())
        eng = Engine(run_dir, cfg, ck["arm"], ck["replicate"], a.publish_every if a.publish_every is not None else ck.get("publish_every"), a.no_pause, a.quiet)
        eng.restore()
        if eng.status == "finished":
            raise SystemExit("run is finished")
        eng.status = "running"
        eng.load_data()
        eng.start_workers()
    else:
        run_dir, cfg = new_run(Path(a.config), a.arm, a.replicate, a.dev, a.seasons, a.holdout)
        if a.tables and not a.dev:
            raise SystemExit("--tables is a --dev option")
        eng = Engine(run_dir, cfg, a.arm, a.replicate, a.publish_every, a.no_pause, a.quiet, Path(a.tables) if a.tables else None)
        print("run dir", run_dir, flush=True)
        manifest = eng.load_data()
        eng.manifest = {**manifest, "arena_commit": _git("rev-parse", "HEAD"), "arena_dirty": bool(_git("status", "--porcelain", "arena", "yt")),
                        "config_hash": _hash_file(run_dir / "config.yaml"), "config_source": str(a.config),
                        "personas_hash": _hash_dir(ARENA / "personas"),
                        "started_at": datetime.utcnow().isoformat() + "Z", "dev": a.dev, "arm": a.arm, "replicate": a.replicate,
                        "seasons": cfg["seasons"], "python": sys.version.split()[0]}
        (run_dir / "manifest.json").write_text(json.dumps(eng.manifest, indent=1, default=str))
        eng.build_field()
        eng.start_workers()
    status = eng.play()
    print("status:", status, "run:", eng.dir.name)


if __name__ == "__main__":
    main()
