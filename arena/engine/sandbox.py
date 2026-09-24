"""Strategy sandbox (SPEC §4.4, §5.2): import allowlist (static + import-time), restricted builtins,
and a worker process per strategy that never opens the source DB — its only data path is the
masked parquet snapshot behind `ctx.observe`.
"""
from __future__ import annotations

import ast
import builtins
import multiprocessing as mp
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np

from arena.api import ctx as api

ALLOWED_MODULES = ("numpy", "pandas", "sklearn", "scipy", "statsmodels", "math", "statistics", "collections",
                   "dataclasses", "typing", "itertools", "functools", "datetime", "enum", "arena.api.ctx", "__future__")
BANNED_NAMES = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars", "breakpoint", "input",
                "getattr", "setattr", "delattr", "memoryview", "exit", "quit", "help"}
SAFE_BUILTINS = {k: getattr(builtins, k) for k in dir(builtins)
                 if not k.startswith("_") and k not in BANNED_NAMES}


def _allowed(name: str) -> bool:
    return any(name == m or name.startswith(m + ".") for m in ALLOWED_MODULES)


def check_source(src: str) -> list[str]:
    """Static check: returns a list of violations (empty = ok)."""
    errs = []
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"syntax error: {e}"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if not _allowed(a.name):
                    errs.append(f"import of {a.name!r} not allowed")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level or not _allowed(mod):
                errs.append(f"import from {mod!r} not allowed")
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            errs.append(f"use of {node.id!r} not allowed")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            errs.append(f"dunder attribute {node.attr!r} not allowed")
    return errs


def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level or not _allowed(name):
        raise ImportError(f"import of {name!r} not allowed in a strategy")
    return builtins.__import__(name, globals, locals, fromlist, level)


def load_strategy(path: Path, class_name: str = "Strategy") -> api.Strategy:
    """Exec `path` with restricted builtins and return an instance of `class_name`."""
    src = Path(path).read_text()
    errs = check_source(src)
    if errs:
        raise ImportError("; ".join(errs))
    ns: dict[str, Any] = {"__builtins__": {**SAFE_BUILTINS, "__import__": _guarded_import, "__build_class__": builtins.__build_class__, "__name__": "strategy"}}
    exec(compile(src, str(path), "exec"), ns)
    cls = ns.get(class_name)
    if cls is None:
        raise ImportError(f"{path} defines no {class_name}")
    inst = cls()
    for m in ("describe", "decide"):
        if not callable(getattr(inst, m, None)):
            raise ImportError(f"{class_name} has no {m}()")
    return inst


# ------------------------------------------------------------------ worker process
def _worker_main(conn, path: str, class_name: str, snapshot_dir: str, seed: int, first_year: int, mask: bool) -> None:
    from arena.engine.pit import Tables  # imported here: the child never imports yt.source
    api.configure(first_year, mask)
    tables = Tables(Path(snapshot_dir))
    rng = np.random.default_rng(seed)
    try:
        strat = load_strategy(Path(path), class_name)
    except Exception as e:  # noqa: BLE001
        conn.send(("init_error", f"{type(e).__name__}: {e}"))
        return
    conn.send(("ready", strat.describe()))

    def features_day(day):
        conn.send(("req_features", day))
        kind, payload = conn.recv()
        if kind != "features":
            raise RuntimeError("bad reply")
        return payload

    def forum(limit, posts):
        return posts[-limit:] if limit else list(posts)

    while True:
        kind, msg = conn.recv()
        if kind == "stop":
            return
        try:
            m = msg
            c = api.Ctx(now=m["now"], offers=m["offers"], budget_left=m["budget_left"], pto_left=m["pto_left"],
                        calendar=m["calendar"], observe=lambda name: tables.visible(name, m["now"].t),
                        features_day=features_day, forum=lambda limit=50: forum(limit, m["forum"]),
                        leaderboard=m["leaderboard"], my_results=m["my_results"], rng=rng, tables=tables.names,
                        budget_total=m["budget_total"], pto_total=m["pto_total"])
            if kind == "decide":
                acts = strat.decide(c)
                if acts is None:
                    acts = []
                acts = [a for a in acts if isinstance(a, (api.Book, api.CommitPTO))]
                conn.send(("done", acts))
            elif kind == "on_turn":
                strat.on_turn(c)
                conn.send(("done", strat.describe()))
            else:
                conn.send(("error", f"unknown request {kind}"))
        except Exception:  # noqa: BLE001
            conn.send(("error", traceback.format_exc(limit=3)))


class Worker:
    """One strategy in its own process. `call` enforces the wall-clock caps; a timeout kills and
    restarts the worker (its in-memory caches are lost; `on_turn` rebuilds them)."""

    def __init__(self, name: str, path: Path, class_name: str, snapshot_dir: Path, seed: int,
                 first_year: int, mask: bool, features_day_fn, timeouts: dict):
        self.name, self.path, self.class_name = name, Path(path), class_name
        self.snapshot_dir, self.seed, self.first_year, self.mask = Path(snapshot_dir), seed, first_year, mask
        self.features_day_fn = features_day_fn
        self.timeouts = timeouts
        self.describe = ""
        self.proc = None
        self.conn = None
        self.restarts = 0
        self.start()

    def start(self) -> None:
        ctx = mp.get_context("spawn")
        self.conn, child = ctx.Pipe()
        self.proc = ctx.Process(target=_worker_main, name=f"strategy-{self.name}", daemon=True,
                                args=(child, str(self.path), self.class_name, str(self.snapshot_dir), self.seed,
                                      self.first_year, self.mask))
        self.proc.start()
        child.close()
        if not self.conn.poll(120):
            self.kill()
            raise RuntimeError(f"{self.name}: worker did not start")
        kind, payload = self.conn.recv()
        if kind != "ready":
            self.kill()
            raise ImportError(f"{self.name}: {payload}")
        self.describe = payload

    def kill(self) -> None:
        if self.proc is not None and self.proc.is_alive():
            self.proc.kill()
            self.proc.join(5)
        self.proc = None

    def stop(self) -> None:
        try:
            if self.conn is not None:
                self.conn.send(("stop", None))
        except (BrokenPipeError, OSError):
            pass
        self.kill()

    def call(self, kind: str, msg: dict) -> tuple[Any, str | None]:
        """Returns (result, error). error is a string on exception/timeout, result None then."""
        timeout = self.timeouts["decide_s"] if kind == "decide" else self.timeouts["on_turn_s"]
        deadline = time.monotonic() + timeout
        try:
            self.conn.send((kind, msg))
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not self.conn.poll(remaining):
                    self.kill(); self.restarts += 1; self.start()
                    return None, f"timeout after {timeout}s ({kind}); worker restarted"
                k, payload = self.conn.recv()
                if k == "req_features":
                    self.conn.send(("features", self.features_day_fn(payload)))
                elif k == "done":
                    return payload, None
                elif k == "error":
                    return None, payload
        except (EOFError, BrokenPipeError, OSError) as e:
            self.kill(); self.restarts += 1; self.start()
            return None, f"worker crashed ({e}); restarted"
