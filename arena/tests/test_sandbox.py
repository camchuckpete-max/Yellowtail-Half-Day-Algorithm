"""Import allowlist and restricted builtins (SPEC §5.2), static and at import time."""
import textwrap
from pathlib import Path

import pytest

from arena.engine import sandbox


def _write(tmp_path, src):
    p = tmp_path / "strategy.py"
    p.write_text(textwrap.dedent(src))
    return p


GOOD = """
    import numpy as np
    from arena.api.ctx import Strategy, Book
    class Strategy(Strategy):
        name = "ok"
        def describe(self): return "ok"
        def decide(self, ctx): return []
"""


def test_good_strategy_loads(tmp_path):
    s = sandbox.load_strategy(_write(tmp_path, GOOD))
    assert s.describe() == "ok"


@pytest.mark.parametrize("bad", [
    "import os", "import sys", "import sqlite3", "import subprocess", "from yt import source", "import socket",
    "import urllib.request", "from pathlib import Path", "x = open('f')", "y = __import__('os')", "z = eval('1')",
    "class A: pass\nq = A.__subclasses__", "g = globals()", "h = getattr(int, '__class__')", "from . import x",
])
def test_static_check_rejects(bad):
    assert sandbox.check_source(bad), bad


def test_import_time_guard(tmp_path):
    src = GOOD + "\n    import importlib\n"
    with pytest.raises(ImportError):
        sandbox.load_strategy(_write(tmp_path, src))
    # a dynamic import that slips past the static check is still refused at import time
    src = GOOD.replace("def decide(self, ctx): return []", "def decide(self, ctx):\n            import os\n            return []")
    assert sandbox.check_source(textwrap.dedent(src))  # static catches it too
    ns = {"__builtins__": {**sandbox.SAFE_BUILTINS, "__import__": sandbox._guarded_import}}
    with pytest.raises(ImportError):
        exec("import os", ns)


def test_no_open_builtin(tmp_path):
    src = GOOD.replace("def decide(self, ctx): return []", "def decide(self, ctx):\n            f = open\n            return []")
    with pytest.raises(ImportError):
        sandbox.load_strategy(_write(tmp_path, src))


def test_baselines_pass_the_check():
    src = (Path(__file__).resolve().parents[1] / "agents" / "_scripted" / "baselines.py").read_text()
    assert sandbox.check_source(src) == []
