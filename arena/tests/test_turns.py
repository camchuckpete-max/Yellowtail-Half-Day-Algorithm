"""Offline tests of the turn machinery: the arena MCP server (JSON-RPC over stdio) bound to a
snapshot, submit_strategy validation, forum quota, and the prompt/settings builders. No LLM."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from arena import turns
from arena.engine import calendar as cal
from arena.tests.test_pit_arena import snapshot_dir

ROOT = Path(__file__).resolve().parents[2]

GOOD = textwrap.dedent('''
    from arena.api.ctx import Strategy, Book
    class Strategy(Strategy):
        name = "sat"
        def describe(self): return "PM half day every Saturday in July-October."
        def decide(self, ctx):
            if ctx.now.hour != 21: return []
            d = ctx.tomorrow
            o = ctx.offer("HD_PM")
            if d.weekday == 5 and 182 <= d.doy <= 304 and o and o.bookable:
                boat = ctx.pick_boat("HD_PM", d)
                return [Book(o.id, "saturday", boat=boat)] if boat else []
            return []
''')
LEAK = GOOD.replace("182 <= d.doy <= 304", "182 <= d.doy <= 304 and ctx.season == 3")
PEEK = textwrap.dedent('''
    from arena.api.ctx import Strategy, Book
    class Strategy(Strategy):
        name = "peek"
        def describe(self): return "cheats"
        def decide(self, ctx):
            t = ctx.observe("trips")
            o = ctx.offer("HD_PM")
            if ctx.now.hour != 21 or o is None: return []
            # tries to read tomorrow's count through the visible prefix: nothing is there, so it uses avail_t bound
            fut = t[t["fish_date_t"] >= ctx.now.t]
            return [Book(o.id, "x")] if len(fut) else []
''')


class Client:
    def __init__(self, turn_dir: Path):
        env = {**os.environ, "ARENA_TURN_DIR": str(turn_dir)}
        self.p = subprocess.Popen([sys.executable, str(ROOT / "arena" / "mcp_server.py")], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        self.n = 0
        self.send({"method": "initialize", "params": {"protocolVersion": "2024-11-05"}})
        self.notify("notifications/initialized")

    def send(self, msg):
        self.n += 1
        msg = {"jsonrpc": "2.0", "id": self.n, **msg}
        self.p.stdin.write(json.dumps(msg) + "\n"); self.p.stdin.flush()
        line = self.p.stdout.readline()
        assert line, self.p.stderr.read()
        return json.loads(line)

    def notify(self, method):
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n"); self.p.stdin.flush()

    def call(self, name, **args):
        r = self.send({"method": "tools/call", "params": {"name": name, "arguments": args}})
        res = r["result"]
        return res["content"][0]["text"], res.get("isError", False)

    def close(self):
        self.p.stdin.close(); self.p.wait(5)


@pytest.fixture(scope="module")
def turn(tmp_path_factory):
    d = tmp_path_factory.mktemp("turn")
    sb = d / "sandbox"; sb.mkdir()
    snap = snapshot_dir()
    now_t = cal.t_of(__import__("datetime").datetime(2015, 8, 1, 21))
    (d / "turn.json").write_text(json.dumps({"agent": "tester", "sandbox": str(sb), "snapshot": str(snap), "forum_path": str(d / "forum.jsonl"),
                                             "forum": True, "forum_quota_left": 1, "now": {"season": 6, "doy": 213, "hour": 21, "t": now_t},
                                             "first_year": 2010, "mask_years": True}))
    (d / "forum.jsonl").write_text(json.dumps({"post_id": "p00001", "season": 6, "doy": 200, "hour": 21, "agent": "other", "text": "hello", "t": now_t - 13, "rank_at_post": 2}) + "\n"
                                   + json.dumps({"post_id": "p00002", "season": 6, "doy": 220, "hour": 21, "agent": "other", "text": "future", "t": now_t + 7, "rank_at_post": 2}) + "\n")
    return d


def test_tools_list_and_describe(turn):
    c = Client(turn)
    r = c.send({"method": "tools/list"})
    names = {t["name"] for t in r["result"]["tools"]}
    assert {"describe_tables", "arena_query", "arena_eval", "forum_read", "forum_post", "submit_strategy", "write_notes"} <= names
    txt, err = c.call("describe_tables")
    assert not err and "trips" in txt and "season 6" in txt
    c.close()


def test_query_and_eval(turn):
    c = Client(turn)
    txt, err = c.call("arena_query", sql="SELECT cls, count(*) n FROM trips GROUP BY cls ORDER BY n DESC")
    assert not err and "hd_am" in txt
    txt, err = c.call("arena_query", sql="SELECT * FROM read_parquet('/etc/passwd')")
    assert err
    txt, err = c.call("arena_query", sql="DROP TABLE trips")
    assert err
    txt, err = c.call("arena_eval", code="t = tables['trips']\nresult = t.groupby('cls')['yt'].sum().sort_values()")
    assert not err and "day_1_5" in txt
    txt, err = c.call("arena_eval", code="import os\nresult = 1")
    assert err and "not allowed" in txt
    txt, err = c.call("arena_eval", code="result = open('/etc/passwd').read()")
    assert err
    log = [json.loads(l) for l in (turn / "queries.jsonl").read_text().splitlines()]
    assert sum(1 for r in log if r.get("tool") == "arena_query") >= 1
    c.close()


def test_forum_visibility_and_quota(turn):
    c = Client(turn)
    txt, err = c.call("forum_read", limit=10)
    assert not err and "hello" in txt and "future" not in txt          # posts after now are invisible
    txt, err = c.call("forum_post", text="I found something. " * 3)
    assert not err
    txt, err = c.call("forum_post", text="second")
    assert err and "quota" in txt
    txt, err = c.call("forum_post", text="w " * 301)
    assert err
    c.close()


def test_submit_strategy(turn):
    c = Client(turn)
    txt, err = c.call("submit_strategy", code=LEAK, summary="leaky")
    assert err and "calendar" in txt
    txt, err = c.call("submit_strategy", code="import os\n" + GOOD, summary="bad import")
    assert err and "disallowed" in txt
    txt, err = c.call("submit_strategy", code=GOOD.replace('"PM half day every Saturday in July-October."', '"' + "word " * 201 + '"'), summary="long")
    assert err and "200" in txt
    txt, err = c.call("submit_strategy", code=GOOD, summary="saturday PM", adopted_from=["p00001"])
    assert not err, txt
    assert (turn / "strategy_submitted.py").exists()
    sub = json.loads((turn / "submission.json").read_text())
    assert sub["adopted_from"] == ["p00001"] and "Saturday" in sub["describe"]
    txt, err = c.call("write_notes", text="remember: saturdays")
    assert not err and (turn / "sandbox" / "notes.md").read_text() == "remember: saturdays"
    c.close()


def test_prompt_and_settings():
    p = turns.build_prompt({"name": "x"}, {"season": 3, "doy": 182, "hour": 21, "season_end": False, "first_turn": False, "results": [],
                                           "failures": [], "leaderboard": [], "forum_new": [], "quota_left": 2, "budget_left": 1200.0,
                                           "pto_left": 6, "season_counted": True})
    assert "forum_post" in p and "submit_strategy" in p
    for bad in ("adversar", "honest", "mislead", "poison", "SPEC"):
        assert bad not in p.lower() and bad not in (ROOT / "arena" / "RULES.md").read_text().lower()
    s = turns._settings(Path("/src/repo"))
    assert any("SPEC.md" in d for d in s["permissions"]["deny"]) and any("src/repo" in d for d in s["permissions"]["deny"])
    assert "Bash" in s["permissions"]["deny"]


def test_mcp_healthcheck(turn, tmp_path):
    (turn / "mcp.json").write_text(json.dumps({"mcpServers": {"arena": {"command": sys.executable, "args": [str(ROOT / "arena" / "mcp_server.py")],
                                                                        "env": {"ARENA_TURN_DIR": str(turn)}}}}))
    assert turns.mcp_healthcheck(turn) is None
    bad = tmp_path / "bad"; (bad / "sandbox").mkdir(parents=True)
    (bad / "turn.json").write_text(json.dumps({"agent": "x", "sandbox": str(bad / "sandbox"), "snapshot": "relative/does/not/exist",
                                              "forum_path": str(bad / "f.jsonl"), "forum": False, "forum_quota_left": 0,
                                              "now": {"season": 1, "doy": 1, "hour": 21, "t": 0.0}, "first_year": 2010, "mask_years": True}))
    (bad / "mcp.json").write_text(json.dumps({"mcpServers": {"arena": {"command": sys.executable, "args": [str(ROOT / "arena" / "mcp_server.py")],
                                                                       "env": {"ARENA_TURN_DIR": str(bad)}}}}))
    err = turns.mcp_healthcheck(bad)
    assert err and "failed to start" in err
    r = turns.run_claude(bad, "x", "claude-haiku-4-5-20251001", 1, 0.01, 10)
    assert r["exit"] == -2 and turns.collect(bad)["error"]       # spends nothing, turn marked failed
