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
from arena import turns as turnmod
from arena.engine import judgment as jm

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
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


class Agent:
    def __init__(self, name: str, kind: str, path: Path, class_name: str, adversary: str | None = None,
                 persona: str | None = None, model: str | None = None, forum: bool = True):
        self.name, self.kind, self.path, self.class_name = name, kind, Path(path), class_name
        self.adversary, self.persona, self.model = adversary, persona, model
        self.forum = forum   # False: neither reads nor posts (D-053); scripted baselines never use the forum
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
        self.last_strategy_change: dict | None = None
        self.last_turn: dict | None = None
        self.posts_by_month: dict[str, int] = {}     # "YYYY-MM" -> posts
        self.cost_usd = 0.0
        self.forum_cursor = 0                        # forum posts already shown to this agent
        self.trips_all: list[dict] = []              # every settled trip, all seasons (dashboard inspector)
        self.turns_log: list[dict] = []              # every LLM turn (dashboard inspector)
        self.journal: list[str] = []                 # daily judgment notes (D-058)
        self.judgment_calls = 0
        self.judgment_cost = 0.0
        self.failures_cursor = 0                     # failures already shown in a briefing

    def to_json(self) -> dict:
        return {k: getattr(self, k) for k in ("name", "kind", "class_name", "adversary", "persona", "model", "forum", "budget", "pto",
                                              "pto_committed", "bookings", "history", "last_reasons", "failures", "describe",
                                              "strategy_version", "last_strategy_change", "last_turn", "posts_by_month",
                                              "cost_usd", "forum_cursor", "trips_all", "turns_log", "journal", "judgment_calls",
                                              "judgment_cost", "failures_cursor")} | {"path": str(self.path)}

    @classmethod
    def from_json(cls, d: dict) -> "Agent":
        a = cls(d["name"], d["kind"], Path(d["path"]), d["class_name"], d.get("adversary"), d.get("persona"), d.get("model"), d.get("forum", True))
        for k in ("budget", "pto", "pto_committed", "bookings", "history", "last_reasons", "failures", "describe", "strategy_version",
                  "last_strategy_change", "last_turn", "posts_by_month", "cost_usd", "forum_cursor", "trips_all", "turns_log",
                  "journal", "judgment_calls", "judgment_cost", "failures_cursor"):
            if k in d:
                setattr(a, k, d[k])
        return a


class Engine:
    def __init__(self, run_dir: Path, cfg: dict, arm: str, replicate: int, publish_every: float | None = None,
                 no_pause: bool = False, quiet: bool = False, tables_from: Path | None = None):
        self.dir = Path(run_dir).resolve()   # absolute: turn.json paths are read by processes with another cwd
        self.cfg, self.arm, self.replicate = cfg, arm, replicate
        self.publish_every, self.no_pause, self.quiet = publish_every, no_pause, quiet
        self.first_year = int(cfg["seasons"]["first"])          # masking base: season index = year - first + 1
        self.first_start = pd.Timestamp(cfg["seasons"]["first_start"]).date()
        self.years = cal.season_years(cfg["seasons"])           # seasons actually played (D-058: may be a list)
        self.last_year = self.years[-1]
        self.tick_times = [cal.parse_tick(t) for t in cfg["ticks"]]
        self.prices = cfg["prices"]
        api.configure(self.first_year, bool(cfg.get("mask_years", True)))
        self.agents: list[Agent] = []
        self.forum: list[dict] = []
        self.season_year = self.years[0]
        self.briefer = None
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
        self.cost_usd = 0.0
        self.turns_in_progress: list[str] = []
        self.source_repo = Path(source.SOURCE_REPO)

    # ---------------------------------------------------------------- setup
    def load_data(self) -> dict:
        manifest = source.source_manifest()
        db = source.open_db(manifest)
        self._raw = snapshot.load_raw_tables(db)
        db.close()
        landings = list(self.cfg["landings"])
        self.outcomes = scoring.Outcomes(self._raw["trips"], landings, self.cfg.get("pooled_boats", "all"),
                                         bool(self.cfg.get("count_released", True)))
        if self.cfg.get("judgment", {}).get("mode", "off") != "off":
            self.briefer = jm.Briefer(self._raw, self.outcomes, self.cfg, self.first_year)
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
            self.agents.append(Agent(n, "baseline", SCRIPTED / "baselines.py", n, forum=False))
        if self.cfg["arms"][self.arm].get("adversaries"):
            adv_path = SCRIPTED / "adversaries.py"
            if not adv_path.exists():
                raise SystemExit("poisoned arm needs arena/agents/_scripted/adversaries.py (Phase 4)")
            for n in f.get("adversaries", []):
                self.agents.append(Agent(n, "adversary", adv_path, n, adversary=labels[n]["adversary"]))
        roster = {r["name"]: r for r in f.get("roster", [])}
        models = f.get("models", {})
        for n in list(f.get("agents", [])) + ([f["owner"]] if f.get("owner") else []):
            d = ARENA / "agents" / n
            meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
            r = roster.get(n, {})
            model = meta.get("model") or models.get(r.get("model"), r.get("model"))
            if not (d / "strategy.py").exists():
                raise SystemExit(f"agent {n}: no {d / 'strategy.py'} (run python3 -m arena.tools.seed_agents)")
            run_d = self.dir / "agents" / n
            run_d.mkdir(parents=True, exist_ok=True)
            for fn in ("persona.md", "strategy.py", "notes.md", "meta.json"):
                if (d / fn).exists() and not (run_d / fn).exists():
                    shutil.copy(d / fn, run_d / fn)       # carry_agents: false -> start from the seed (§3.5)
            self.agents.append(Agent(n, "owner" if n == f.get("owner") else "llm", run_d / "strategy.py", "Strategy",
                                     persona=meta.get("persona") or r.get("persona"), model=model,
                                     forum=bool(meta.get("forum", r.get("forum", True)))))
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
            v = self.dir / "agents" / a.name / f"strategy_v{a.strategy_version}.py"
            if not v.exists():
                shutil.copy(a.path, v)

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
                           boat=b.get("boat", ""), settled=b["settled"], ran=b.get("ran"), yt=b.get("yt"), anglers=b.get("anglers"),
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
                out.append({"offer_id": b["offer_id"], "cls": b["cls"], "boat": b.get("boat", ""), "departure": str(api.day_of(date.fromisoformat(b["departure"]))),
                            "ran": b["ran"], "yt": b["yt"], "anglers": b["anglers"], "n_agents": b["n_agents"], "share": b["share"],
                            "pooled_share": b.get("pooled_share")})
        return out

    def _forum_visible(self, t: float, agent: "Agent | None" = None) -> list[dict]:
        if not self.cfg["arms"][self.arm].get("forum") or (agent is not None and not agent.forum):
            return []
        return [p for p in self.forum if p["t"] <= t]

    # ---------------------------------------------------------------- tick
    def settle(self, now: datetime) -> None:
        w = float(self.cfg["agent_angler_weight"])
        for a in self.agents:
            for b in a.bookings:
                if b["settled"] or datetime.fromisoformat(b["return_at"]) > now:
                    continue
                fd = date.fromisoformat(b["fishing_dates"][0])
                by_boat = self.cfg.get("booking_unit", "boat") == "boat"
                key = (b["cls"], b["departure"], b.get("boat", "") if by_boat else "")
                n_agents = sum(1 for x in self.agents for y in x.bookings
                               if (y["cls"], y["departure"], y.get("boat", "") if by_boat else "") == key)
                po = self.outcomes.pooled_outcome(b["cls"], fd)
                out = self.outcomes.boat_outcome(b["cls"], b.get("boat", ""), fd) if by_boat else (po[:2] if po else None)
                b["settled"] = True
                b["n_agents"] = n_agents
                b["pooled_share"] = round(po[0] / po[1], 6) if po and po[1] else None
                if out is None:
                    b["ran"] = False
                    a.budget += b["cost"]   # fare refunded, PTO stays spent (§3.3)
                    b["yt"] = b["anglers"] = b["share"] = None
                else:
                    yt, anglers = out
                    b["ran"], b["yt"], b["anglers"] = True, yt, anglers
                    b["share"] = round(scoring.share(yt, anglers, n_agents, w), 6)
                rec = {"season": self.season_year, "season_idx": api.day_of(fd).season, "doy": api.day_of(fd).doy,
                       "date": fd.isoformat(), "agent": a.name, "cls": b["cls"], "boat": b.get("boat", ""), "ran": b["ran"],
                       "yt": b["yt"], "anglers": b["anglers"], "n_agents": n_agents, "share": b["share"], "pooled_share": b["pooled_share"]}
                _jsonl(self.dir / "outcomes.jsonl", rec)
                self.outcomes_recent = ([rec] + self.outcomes_recent)[:20]
                a.trips_all.append({"season": rec["season_idx"], "doy": rec["doy"], "dep_doy": api.day_of(date.fromisoformat(b["departure"])).doy,
                                    "cls": b["cls"], "boat": b.get("boat", ""), "cost": b["cost"], "pto": b["pto"], "reason": b.get("reason", ""),
                                    "ran": b["ran"], "yt": b["yt"], "anglers": b["anglers"], "competitors": n_agents - 1, "share": b["share"],
                                    "pooled_share": b["pooled_share"], "strategy_version": b.get("strategy_version"), "booked_at": b.get("booked_at_masked", ""),
                                    "via": b.get("via", "code")})

    def tick(self, today: date, tick: str) -> None:
        now = datetime.combine(today, cal.parse_tick(tick))
        t = cal.t_of(now)
        self.settle(now)
        day = api.day_of(today)
        nowobj = api.Now(day=day, hour=now.hour, t=t)
        lb = self._leaderboard()
        raw_offers = off.offers_at(today, tick, self.prices, float(self.cfg["half_day_pto"]))
        is_turn = tick == "21:00" and (today.day in self.cfg["turn_days"] or today == cal.season_bounds(self.season_year, self.first_year, self.first_start)[0])
        if is_turn and any(a.kind in ("llm", "owner") for a in self.agents):
            self.llm_turns(now, season_end=False)
            lb = self._leaderboard()
        jcfg = self.cfg.get("judgment", {})
        if (jcfg.get("mode", "off") == "daily" and tick == jcfg.get("tick", "21:00") and jcfg["months"][0] <= today.month <= jcfg["months"][1]
                and any(a.kind in ("llm", "owner") for a in self.agents)):
            self.judgment(now, today, tick, day, lb)
            lb = self._leaderboard()
        for a in self.agents:
            if a.worker is None:
                continue
            offers = [self._api_offer(o, a, {"today": today}) for o in raw_offers]
            msg = {"now": nowobj, "offers": offers, "budget_left": a.budget, "pto_left": a.pto,
                   "calendar": self._calendar_api(a), "forum": self._forum_visible(t, a), "leaderboard": lb,
                   "my_results": self._masked_results(a), "budget_total": float(self.cfg["budget"]), "pto_total": float(self.cfg["pto"])}
            if is_turn:
                res, err = a.worker.call("on_turn", msg)
                if err:
                    a.failures.append({"date": str(day), "tick": tick, "kind": "on_turn", "error": err})
                    _jsonl(self.dir / "decisions.jsonl", {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name, "kind": "on_turn", "error": err})
                elif res:
                    a.describe = res
            if a.kind in ("llm", "owner") and not self.cfg.get("judgment", {}).get("code_strategies", True):
                continue   # D-058: LLM agents decide only through the nightly call; no standing code
            acts, err = a.worker.call("decide", msg)
            if err:
                a.failures.append({"date": str(day), "tick": tick, "kind": "decide", "error": err})
                _jsonl(self.dir / "decisions.jsonl", {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name, "kind": "decide", "error": err})
                continue
            for act in acts:
                self.apply(a, act, today, tick, day, {o.id: o for o in raw_offers})
        self.write_state(now, tick)

    def apply(self, a: Agent, act, today: date, tick: str, day: api.Day, raw_offers: dict, via: str = "code") -> None:
        try:
            self._apply(a, act, today, tick, day, raw_offers, via)
        except Exception as e:  # noqa: BLE001  (an agent's action must never stop the engine)
            why = f"malformed action {act!r}: {type(e).__name__}: {e}"
            _jsonl(self.dir / "decisions.jsonl", {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name,
                                                  "action": str(act)[:80], "valid": False, "rejected": why[:300]})
            a.failures.append({"date": str(day), "tick": tick, "kind": "rejected", "action": str(act)[:80], "error": why[:300]})

    def _apply(self, a: Agent, act, today: date, tick: str, day: api.Day, raw_offers: dict, via: str = "code") -> None:
        valid, why, label = True, "", ""
        if isinstance(act, api.CommitPTO) and not isinstance(act.day, api.Day):
            valid, why, label = False, f"CommitPTO.day must be a Day (e.g. ctx.today.plus(14)), got {type(act.day).__name__}", f"CommitPTO {act.day!r}"[:60]
        elif isinstance(act, api.Book) and not isinstance(act.offer_id, str):
            valid, why, label = False, f"Book.offer_id must be an offer id string, got {type(act.offer_id).__name__}", f"Book {act.offer_id!r}"[:60]
        elif isinstance(act, api.CommitPTO):
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
            boat = (getattr(act, "boat", "") or "").strip()
            by_boat = self.cfg.get("booking_unit", "boat") == "boat"
            if o is None:
                valid, why = False, "no such offer at this tick"
            elif by_boat and not boat:
                valid, why = False, "no boat given: Book(offer_id, reason, boat=...) with a boat from ctx.scheduled_boats()"
            elif by_boat and boat not in self.outcomes.scheduled_boats(o.cls, o.fishing_dates[0]):
                sched = self.outcomes.scheduled_boats(o.cls, o.fishing_dates[0])
                valid, why = False, f"{boat!r} is not scheduled for {o.cls} on {api.day_of(o.fishing_dates[0])}; scheduled: {', '.join(sched) or 'none'}"
            else:
                label = f"Book {act.offer_id} {boat}".strip()
                ao = self._api_offer(o, a, {"today": today})
                if not ao.bookable:
                    valid, why = False, ao.reason
                else:
                    a.budget -= o.cost
                    if self.cfg["pto_mode"] == "commit_trip":
                        a.pto -= sum(o.pto_need.values())
                    a.bookings.append({"offer_id": o.id, "cls": o.cls, "boat": boat, "departure": o.departure.isoformat(),
                                       "fishing_dates": [f.isoformat() for f in o.fishing_dates], "return_at": o.return_at.isoformat(),
                                       "cost": o.cost, "pto": sum(o.pto_need.values()), "settled": False, "reason": act.reason,
                                       "booked_at": f"{today.isoformat()} {tick}", "booked_at_masked": f"{day} {tick}",
                                       "strategy_version": a.strategy_version, "via": via})
        else:
            valid, why, label = False, "unknown action", str(act)
        rec = {"date": today.isoformat(), "masked": str(day), "tick": tick, "agent": a.name, "action": label,
               "reason": getattr(act, "reason", ""), "valid": valid, "rejected": why or None, "via": via}
        _jsonl(self.dir / "decisions.jsonl", rec)
        a.last_reasons = (a.last_reasons + [{"season": day.season, "doy": day.doy, "tick": tick, "action": label,
                                             "text": getattr(act, "reason", ""), "valid": valid, "reason_rejected": why or None}])[-8:]
        if not valid:
            a.failures.append({"date": str(day), "tick": tick, "kind": "rejected", "action": label, "error": why})

    # ---------------------------------------------------------------- daily judgment (D-058)
    def judgment(self, now: datetime, today: date, tick: str, day: api.Day, lb: list[dict]) -> None:
        jcfg = self.cfg["judgment"]
        agents = [a for a in self.agents if a.kind in ("llm", "owner") and a.worker is not None]
        raw_offers = off.offers_for_judgment(today, self.prices, float(self.cfg["half_day_pto"]))
        jobs, meta = [], {}
        forum_on = bool(self.cfg["arms"][self.arm].get("forum"))
        cheapest = min(self.prices.values())
        done_today = set()
        for a in agents:   # resume safety: a night already logged for this agent is not called again
            f = self.dir / "judgment" / f"{a.name}.jsonl"
            if f.exists():
                for line in f.read_text().splitlines()[-3:]:
                    try:
                        if json.loads(line).get("date") == today.isoformat():
                            done_today.add(a.name)
                    except json.JSONDecodeError:
                        pass
        agents = [a for a in agents if a.name not in done_today]
        for a in agents:
            if a.budget < cheapest and a.pto <= 0:
                _jsonl(self.dir / "judgment" / f"{a.name}.jsonl", {"date": today.isoformat(), "masked": str(day), "skipped": "nothing affordable: budget below the cheapest trip and no PTO left"})
                continue
            run_d = self.dir / "agents" / a.name
            offers_api = [self._api_offer(o, a, {"today": today}) for o in raw_offers]
            settled = [b for b in a.bookings if b["settled"]][-5:]
            state = {"budget": a.budget, "pto": a.pto,
                     "pto_committed": sorted(str(api.day_of(date.fromisoformat(d))) for d in a.pto_committed),
                     "upcoming": [f"{b['cls']} on {b.get('boat', '')} fishing {api.day_of(date.fromisoformat(b['fishing_dates'][0]))}" for b in a.bookings if not b["settled"]],
                     "results": [f"{api.day_of(date.fromisoformat(b['fishing_dates'][0]))} {b['cls']} on {b.get('boat', '')}: "
                                 + (f"{int(b['yt'])} yt / {int(b['anglers'])} anglers, share {b['share']:.3f}" if b["ran"] else "did not run (refunded)")
                                 + (f" (you: {b.get('reason', '')[:80]})" if b.get("reason") else "") for b in settled],
                     "rejected": [f"{f.get('action', '')}: {f.get('error', '')}" for f in a.failures[a.failures_cursor:]][-6:],
                     "journal": a.journal, "notes": (run_d / "notes.md").read_text() if (run_d / "notes.md").exists() else "",
                     "describe": a.describe if a.strategy_version > 1 else ""}
            forum = [self._public_post(p) for p in self.forum if p["t"] <= cal.t_of(now)] if (forum_on and a.forum) else None
            prompt = jm.build_briefing(self.briefer, now, {"name": a.name}, raw_offers, offers_api, state, lb, forum)
            persona = (run_d / "persona.md").read_text() if (run_d / "persona.md").exists() else ""
            system = jm.SYSTEM.format(name=a.name, persona=persona.strip())
            model = self.cfg["field"].get("models", {}).get(a.model, a.model)
            work = turnmod.SANDBOXES / self.dir.name / "judgment" / a.name
            work.mkdir(parents=True, exist_ok=True)
            jobs.append({"name": a.name, "prompt": prompt, "system": system, "model": model, "work_dir": str(work)})
            meta[a.name] = (prompt, a)
        results = jm.run_calls(jobs, int(jcfg.get("parallel", 8)), float(jcfg.get("budget_usd", 0.1)), int(jcfg.get("timeout_s", 180)))
        by_id = {o.id: o for o in raw_offers}
        for name, r in results.items():
            prompt, a = meta[name]
            a.judgment_calls += 1
            a.judgment_cost += r["cost_usd"]; a.cost_usd += r["cost_usd"]; self.cost_usd += r["cost_usd"]
            a.failures_cursor = len(a.failures)
            acts = jm.answer_to_actions(r.get("answer"), raw_offers, today) if r.get("answer") else []
            n_before = len(a.failures)
            for act in acts:
                self.apply(a, act, today, tick, day, by_id, via="judgment")
            note = str((r.get("answer") or {}).get("note", ""))[:300].replace("\n", " ")
            if note:
                a.journal = (a.journal + [f"{day}: {note}"])[-60:]
                with open(self.dir / "agents" / a.name / "journal.md", "a") as f:
                    f.write(f"- {day}: {note}\n")
            _jsonl(self.dir / "judgment" / f"{a.name}.jsonl", {"date": today.isoformat(), "masked": str(day), "model": a.model,
                                                                 "cost_usd": r["cost_usd"], "seconds": r.get("seconds"), "error": r.get("error"),
                                                                 "answer": r.get("answer"), "actions": [str(x) for x in acts],
                                                                 "rejected": [f["error"] for f in a.failures[n_before:]], "prompt": prompt})
            if r.get("error") and not self.quiet:
                print(f"  judgment {day} {a.name}: {r['error'][:120]}", file=sys.stderr, flush=True)
        shutil.rmtree(turnmod.SANDBOXES / self.dir.name / "judgment", ignore_errors=True)
        if jobs:
            self.checkpoint()

    # ---------------------------------------------------------------- LLM turns (Phase 3)
    def _results_for_turn(self, a: Agent, lb_rows: list[dict]) -> dict:
        me = next(r for r in lb_rows if r["name"] == a.name)
        return {"season": api.day_of(date(self.season_year, 12, 31)).season, "budget_left": round(a.budget, 2), "pto_left": a.pto,
                "season_score": me["season_fish"], "season_rank": me["season_rank"], "cumulative_score": me["cumulative_fish"],
                "cumulative_rank": me["cumulative_rank"],
                "pto_committed": sorted(str(api.day_of(date.fromisoformat(d))) for d in a.pto_committed),
                "bookings": [{"offer_id": b["offer_id"], "cls": b["cls"], "departure": str(api.day_of(date.fromisoformat(b["departure"]))),
                              "fishing_date": str(api.day_of(date.fromisoformat(b["fishing_dates"][0]))), "cost": b["cost"], "pto": b["pto"],
                              "settled": b["settled"], "ran": b.get("ran"), "yt": b.get("yt"), "anglers": b.get("anglers"),
                              "competitors_aboard": (b.get("n_agents") or 1) - 1, "share": b.get("share"), "your_reason": b.get("reason")}
                             for b in a.bookings],
                "rejected_actions_and_errors_since_last_turn": a.failures[-40:],
                "seasons": [{"season": h["season_idx"], "score": h["fish"], "rank": h["rank"], "counted": h["counted"]} for h in a.history]}

    def _leaderboard_for_turn(self, lb_rows: list[dict]) -> list[dict]:
        desc = {a.name: a.describe for a in self.agents}
        return [{**r, "strategy": desc.get(r["name"], "")} for r in lb_rows]

    def llm_turns(self, now: datetime, season_end: bool) -> None:
        tcfg = self.cfg.get("turns", {})
        day = api.day_of(now.date())
        t = cal.t_of(now)
        tag = f"S{day.season:02d}_d{day.doy:03d}" + ("_end" if season_end else "")
        agents = [a for a in self.agents if a.kind in ("llm", "owner") and a.worker is not None]
        if not agents:
            return
        done = self.dir / "turns" / tag
        if all((done / a.name / "claude.json").exists() for a in agents):
            if not self.quiet:
                print(f"  turn {tag}: already played (resume); skipped", flush=True)
            return   # idempotent: a resume after a crash later in the same tick must not re-spend the turn
        self.turns_in_progress = [a.name for a in agents]
        self.write_state(now, now.strftime("%H:%M"))
        snap = self.dir / "snapshots" / tag
        if not (snap / "meta.json").exists():
            snapshot.write_snapshot(self._raw, snap, self.first_year, bool(self.cfg.get("mask_years", True)), cutoff=now)
        lb_rows = self._leaderboard()
        lb_pub = self._leaderboard_for_turn(lb_rows)
        forum_on = bool(self.cfg["arms"][self.arm].get("forum"))
        month_key = now.strftime("%Y-%m")
        counted = self.years.index(self.season_year) >= int(self.cfg["warmup_seasons"])
        first_turn = now.date() == cal.season_bounds(self.season_year, self.first_year, self.first_start)[0]
        jobs = []
        for a in agents:
            turn_dir = turnmod.turn_dir_for(self.dir.name, tag, a.name)
            agent_forum = forum_on and a.forum
            quota_left = max(0, int(self.cfg["forum"]["max_posts_per_month"]) - a.posts_by_month.get(month_key, 0)) if agent_forum else 0
            forum_new = [self._public_post(p) for p in self.forum[a.forum_cursor:] if p["t"] <= t] if agent_forum else None
            turnmod.prepare_turn(turn_dir, {"name": a.name, "model": a.model}, self.dir / "agents" / a.name, snap,
                                 self.dir / "forum.jsonl", agent_forum, quota_left,
                                 {"season": day.season, "doy": day.doy, "hour": now.hour, "t": t},
                                 self.first_year, bool(self.cfg.get("mask_years", True)), self.source_repo,
                                 self._results_for_turn(a, lb_rows), lb_pub, forum_new,
                                 code_strategies=bool(self.cfg.get("judgment", {}).get("code_strategies", True)),
                                 nightly=self.cfg.get("judgment", {}).get("mode", "off") == "daily")
            prompt = turnmod.build_prompt({"name": a.name}, {"season": day.season, "doy": day.doy, "hour": now.hour,
                                                              "season_end": season_end, "first_turn": first_turn and not season_end,
                                                              "forum_new": forum_new, "quota_left": quota_left if agent_forum else None,
                                                              "budget_left": a.budget, "pto_left": a.pto, "season_counted": counted,
                                                              "code_strategies": bool(self.cfg.get("judgment", {}).get("code_strategies", True)),
                                                              "nightly": self.cfg.get("judgment", {}).get("mode", "off") == "daily"})
            jobs.append({"turn_dir": str(turn_dir), "agent": {"name": a.name, "model": a.model}, "prompt": prompt})
        if not self.quiet:
            print(f"  turn {tag}: {len(jobs)} agent(s) ...", flush=True)
        results = turnmod.run_turns(jobs, int(tcfg.get("parallel", 4)), self.cfg["field"].get("models", {}),
                                    int(tcfg.get("max_tool_turns", 40)), float(tcfg.get("budget_usd", 1.0)), int(tcfg.get("timeout_s", 1200)))
        for a in agents:
            r = results.get(a.name, {})
            if r.get("error"):
                print(f"  turn {tag} {a.name}: FAILED: {r['error'][:200]}", file=sys.stderr, flush=True)
            self._apply_turn(a, r, tag, day, now, t, month_key, lb_rows)
            turnmod.archive_turn(turnmod.turn_dir_for(self.dir.name, tag, a.name), self.dir, tag, a.name)
        shutil.rmtree(turnmod.SANDBOXES / self.dir.name, ignore_errors=True)
        self.turns_in_progress = []
        shutil.rmtree(snap, ignore_errors=True)   # the physical snapshot is rebuilt per turn; ~70 MB each
        self.checkpoint()

    def _public_post(self, p: dict) -> dict:
        return {k: p[k] for k in ("post_id", "season", "doy", "hour", "agent", "text", "rank_at_post")}

    def _apply_turn(self, a: Agent, r: dict, tag: str, day: api.Day, now: datetime, t: float, month_key: str, lb_rows: list[dict]) -> None:
        run_d = self.dir / "agents" / a.name
        a.cost_usd += float(r.get("cost_usd") or 0.0)
        self.cost_usd += float(r.get("cost_usd") or 0.0)
        sub = r.get("submission")
        changed = False
        if sub:
            a.strategy_version += 1
            new_path = run_d / f"strategy_v{a.strategy_version}.py"
            new_path.write_text(sub["code"])
            import difflib
            old_code = a.path.read_text() if a.path.exists() else ""
            diff = "".join(difflib.unified_diff(old_code.splitlines(True), sub["code"].splitlines(True),
                                                f"strategy_v{a.strategy_version - 1}.py", f"strategy_v{a.strategy_version}.py"))
            (run_d / f"strategy_v{a.strategy_version}.diff").write_text(diff)
            a.path.write_text(sub["code"])
            try:
                a.worker.stop()
                a.worker = Worker(a.name, a.path, a.class_name, self.dir / "tables", a.worker.seed, self.first_year,
                                  bool(self.cfg.get("mask_years", True)), self.features_day, self.cfg["timeouts"])
                a.describe = a.worker.describe
                changed = True
            except Exception as e:  # noqa: BLE001  (validated in the turn; should not happen)
                a.failures.append({"date": str(day), "kind": "strategy_load", "error": str(e)})
                a.path.write_text(old_code)
                a.worker = Worker(a.name, a.path, a.class_name, self.dir / "tables", a.worker.seed if a.worker else 0, self.first_year,
                                  bool(self.cfg.get("mask_years", True)), self.features_day, self.cfg["timeouts"])
            if changed:
                a.last_strategy_change = {"season": day.season, "doy": day.doy, "summary": sub.get("summary", ""),
                                          "diff_path": f"agents/{a.name}/strategy_v{a.strategy_version}.diff", "version": a.strategy_version}
                _jsonl(self.dir / "strategy_changes.jsonl", {"date": now.date().isoformat(), "masked": str(day), "agent": a.name,
                                                              "version": a.strategy_version, "summary": sub.get("summary", ""),
                                                              "adopted_from": sub.get("adopted_from", []), "describe": a.describe})
                for pid in sub.get("adopted_from", []) or []:
                    for p in self.forum:
                        if p["post_id"] == pid and a.name not in p["cited_by"]:
                            p["cited_by"].append(a.name)
        me = next(x for x in lb_rows if x["name"] == a.name)
        for text in r.get("posts", []):
            pid = f"p{len(self.forum) + 1:05d}"
            post = {"post_id": pid, "season": day.season, "doy": day.doy, "hour": now.hour, "agent": a.name, "text": text,
                    "t": t, "rank_at_post": me["season_rank"], "adversary": a.adversary, "cited_by": [], "date": now.date().isoformat()}
            self.forum.append(post)
            _jsonl(self.dir / "forum.jsonl", post)
            a.posts_by_month[month_key] = a.posts_by_month.get(month_key, 0) + 1
        a.forum_cursor = len(self.forum)
        if r.get("notes") is not None:
            (run_d / "notes.md").write_text(r["notes"])
        a.last_turn = {"season": day.season, "doy": day.doy, "tag": tag, "queries": r.get("queries", 0),
                       "queries_before_submit": r.get("queries_before_submit"), "posts": len(r.get("posts", [])),
                       "adopted_from": (sub or {}).get("adopted_from", []), "submitted": bool(sub), "adopted": changed,
                       "cost_usd": round(float(r.get("cost_usd") or 0.0), 4), "ok": r.get("ok"), "error": r.get("error")}
        _jsonl(self.dir / "turns.jsonl", {"tag": tag, "agent": a.name, "model": a.model, **a.last_turn,
                                          "num_turns": r.get("num_turns"), "seconds": r.get("seconds"), "summary": r.get("summary")})
        a.turns_log.append({**{k: a.last_turn[k] for k in ("season", "doy", "tag", "queries", "posts", "submitted", "adopted", "cost_usd", "ok")},
                            "season_end": tag.endswith("_end"), "version": a.strategy_version if changed else None,
                            "change_summary": (sub or {}).get("summary") if changed else None, "describe": a.describe if changed else None,
                            "summary": (r.get("summary") or "")[:600], "error": (r.get("error") or "")[:300] or None})
        a.failures = []

    # ---------------------------------------------------------------- season
    def season_end(self) -> None:
        self.settle(datetime(self.season_year + 1, 12, 31))  # every booked trip of this season has returned
        counted = self.years.index(self.season_year) >= int(self.cfg["warmup_seasons"])
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
        llm = [a for a in self.agents if a.kind in ("llm", "owner")]
        on = [sum(by[a.name]) for a in llm if a.forum]
        off = [sum(by[a.name]) for a in llm if not a.forum]
        pairs = {}
        for a in llm:
            for b in llm:
                if a.persona and a.persona == b.persona and a.forum and not b.forum:
                    pairs[f"{a.name}-{b.name}"] = round(sum(by[a.name]) - sum(by[b.name]), 4)
        forum_effect = {"forum_on_mean": round(float(np.mean(on)), 4) if on else None, "forum_off_mean": round(float(np.mean(off)), 4) if off else None,
                        "diff": round(float(np.mean(on) - np.mean(off)), 4) if on and off else None, "persona_matched_pairs": pairs}
        provenance = {p["post_id"]: {"agent": p["agent"], "cited_by": p["cited_by"], "adversary": p.get("adversary")} for p in self.forum if p["cited_by"]}
        out = {"run": self.dir.name, "arm": self.arm, "replicate": self.replicate, "seasons_counted": len(next(iter(by.values()), [])),
               "cumulative": {n: round(sum(v), 4) for n, v in by.items()},
               "leaderboard_cumulative": sorted(names, key=lambda n: sum(by[n]), reverse=True),
               "ci_vs_baselines": cis, "field_by_season": self.field_by_season, "forum_effect_within_run": forum_effect,
               "posts_cited": provenance, "cost_usd": round(self.cost_usd, 2),
               "per_agent": {a.name: {"kind": a.kind, "model": a.model, "forum": a.forum, "strategy_version": a.strategy_version, "cost_usd": round(a.cost_usd, 2),
                                      "judgment_calls": a.judgment_calls, "judgment_cost_usd": round(a.judgment_cost, 2),
                                      "trips_via": {v: sum(1 for t in a.trips_all if t.get("via", "code") == v) for v in ("judgment", "code")}} for a in self.agents}}
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
                strip.append({"doy": dd.doy, "pto": b["pto"] > 0, "cls": b["cls"], "boat": b.get("boat", ""),
                              "outcome": ("fish" if b.get("yt") else "skunk") if b["settled"] and b["ran"] else ("cancelled" if b["settled"] else "pending"),
                              "share": b.get("share"), "n_agents": b.get("n_agents")})
            by_cls: dict[str, int] = {}
            for b in settled:
                by_cls[b["cls"]] = by_cls.get(b["cls"], 0) + 1
            agents.append({
                "name": a.name, "kind": a.kind, "persona": a.persona, "model": a.model, "adversary": a.adversary, "forum": a.forum,
                "describe": a.describe, "strategy_version": a.strategy_version, "last_strategy_change": a.last_strategy_change,
                "last_turn": a.last_turn, "cost_usd": round(a.cost_usd, 2),
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
                "last_reasons": a.last_reasons, "strip": strip, "trips": a.trips_all, "turns": a.turns_log,
                "journal": a.journal[-40:], "judgment": {"calls": a.judgment_calls, "cost_usd": round(a.judgment_cost, 2)}})
        state = {
            "schema": st.SCHEMA,
            "run": {"id": self.dir.name, "arm": self.arm, "replicate": self.replicate, "status": status,
                    "source_commit": self.manifest.get("source_commit", ""), "arena_commit": self.manifest.get("arena_commit", ""),
                    "config_hash": self.manifest.get("config_hash", ""), "started_at": self.manifest.get("started_at", ""),
                    "sim": {"season": day.season, "calendar_year": now.year,
                            "doy": day.doy, "date_masked": str(day), "tick": tick, "season_start_doy": start.timetuple().tm_yday,
                            "season_end_doy": end.timetuple().tm_yday, "days_in_season": cal.days_in_year(self.season_year)},
                    "turns_in_progress": list(self.turns_in_progress), "cost_usd": round(self.cost_usd, 2),
                    "seasons_done": self.years.index(self.season_year) if self.season_year in self.years else len(self.years),
                    "seasons_total": len(self.years), "seasons_played": [y - self.first_year + 1 for y in self.years],
                    "warmup_seasons": int(self.cfg["warmup_seasons"]), "paused_reason": self.paused_reason, "interventions": self.interventions},
            "agents": agents,
            "leaderboard": {"season": [r["name"] for r in lb], "cumulative": [r["name"] for r in sorted(lb, key=lambda r: r["cumulative_rank"])]},
            "forum": {"enabled": bool(self.cfg["arms"][self.arm].get("forum")), "n_total": len(self.forum), "path": "forum.jsonl",
                      "posts": [{k: p[k] for k in ("post_id", "season", "doy", "hour", "agent", "text", "rank_at_post", "adversary", "cited_by")}
                                for p in reversed(self.forum[-st.FORUM_INLINE_POSTS:])]},
            "field": {**(self.field_by_season[-1] if self.field_by_season else {"diversity_jaccard": None, "herding": None}), "by_season": self.field_by_season},
            "outcomes_recent": [{"season": o["season_idx"], "doy": o["doy"], "cls": o["cls"], "boat": o.get("boat", ""), "ran": o["ran"], "yt": o["yt"], "anglers": o["anglers"], "n_agents": o["n_agents"], "share": o["share"], "agent": o["agent"]} for o in self.outcomes_recent],
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
                "replicate": self.replicate, "publish_every": self.publish_every, "cost_usd": self.cost_usd}
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
        self.cost_usd = float(data.get("cost_usd", 0.0))
        self.manifest = json.loads((self.dir / "manifest.json").read_text())

    # ---------------------------------------------------------------- main loop
    def play(self) -> str:
        """Play until the next season end (or the end of the last season). Returns the final status."""
        try:
            while self.season_year in self.years:
                ticks = list(cal.ticks_of_season(self.season_year, self.first_year, self.first_start, self.tick_times))
                if self.cursor:
                    cd, ct = date.fromisoformat(self.cursor[0]), self.cursor[1]
                    ticks = [(d, t) for d, t in ticks if (d, t.strftime("%H:%M")) >= (cd, ct)]
                elif self.season_year != self.years[0]:
                    self.season_reset()   # a fresh season starts (also right after a resume from a season-end pause)
                t0 = time.time()
                for i, (d, t) in enumerate(ticks):
                    self.tick(d, t.strftime("%H:%M"))
                    self.cursor = (d.isoformat(), t.strftime("%H:%M"))
                    if not self.quiet and i % 200 == 0:
                        print(f"  {d} {t.strftime('%H:%M')}  ({time.time() - t0:.0f}s)", flush=True)
                self.season_end()
                if any(a.kind in ("llm", "owner") for a in self.agents):
                    self.llm_turns(datetime(self.season_year, 12, 31, 21), season_end=True)
                done_year = self.season_year
                i = self.years.index(self.season_year)
                self.season_year = self.years[i + 1] if i + 1 < len(self.years) else self.last_year + 1
                self.cursor = None
                self.status = "finished" if self.season_year not in self.years else "paused_season_end"
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
        cfg["seasons"]["years"] = list(range(int(a), int(b) + 1))
        cfg["seasons"].pop("last", None)
    if max(cal.season_years(cfg["seasons"])) >= HOLDOUT_START.year and not holdout:
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
        run_dir = (Path(a.resume) if Path(a.resume).exists() else ARENA / "runs" / a.resume).resolve()
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
