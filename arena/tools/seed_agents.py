"""Create `arena/agents/<name>/` for every roster entry (SPEC §5.1): persona.md, strategy.py
(no-op until the agent's first turn), notes.md, meta.json.  Existing agent dirs are left alone.

    python3 -m arena.tools.seed_agents [--config arena/configs/default.yaml] [--force]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import yaml

ARENA = Path(__file__).resolve().parents[1]

INITIAL_STRATEGY = '''"""Initial strategy: do nothing until you write one. Replace this whole file via submit_strategy."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "no strategy yet"

    def describe(self):
        return "No strategy yet: books nothing."

    def decide(self, ctx):
        return []
'''


def seed(cfg_path: Path, force: bool = False) -> list[str]:
    cfg = yaml.safe_load(cfg_path.read_text())
    made = []
    for r in cfg["field"]["roster"]:
        d = ARENA / "agents" / r["name"]
        if d.exists() and not force:
            continue
        d.mkdir(parents=True, exist_ok=True)
        persona = (ARENA / "personas" / f"{r['persona']}.md").read_text()
        (d / "persona.md").write_text(persona)
        (d / "strategy.py").write_text(INITIAL_STRATEGY)
        (d / "notes.md").write_text("# Notes\n\n(private; nothing yet)\n")
        (d / "meta.json").write_text(json.dumps({"model": cfg["field"]["models"][r["model"]], "model_tier": r["model"],
                                                 "persona": r["persona"], "forum": bool(r["forum"]),
                                                 "created_at": datetime.utcnow().isoformat() + "Z"}, indent=1))
        made.append(r["name"])
    return made


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ARENA / "configs" / "default.yaml"))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    print("seeded:", ", ".join(seed(Path(a.config), a.force)) or "(nothing new)")


if __name__ == "__main__":
    main()
