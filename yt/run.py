"""CLI: python -m yt.run <experiment> [--holdout] [--strict]

Runs one named experiment from yt/experiments.py, writes runs/<id>/ and
appends one line to LOG.md.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from . import dataset, evaluate, experiments


def fmt(x: float) -> str:
    return "nan" if x != x else f"{x:.3f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--strict", action="store_true", help="strict timing: nothing returning on D-1 is visible")
    ap.add_argument("--no-save", action="store_true")
    a = ap.parse_args()

    spec = experiments.get(a.experiment)
    df, manifest = dataset.build(strict=a.strict)
    df = evaluate.eligible(df)
    if a.holdout:
        with open(evaluate.ROOT / "holdout_access.log", "a") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} {spec.name} strict={a.strict} "
                    f"source={manifest['source_commit']}\n")
    pred, info = evaluate.run_spec(df, spec, holdout=a.holdout)
    s = evaluate.summarize(pred)
    m, b, bo, dd = s["model"], s["baselines"], s["breakout"], s["mcc_diff_vs_best_baseline"]
    line = (f"| {spec.name}{' (strict)' if a.strict else ''} | {'HOLDOUT' if a.holdout else 'dev'} | "
            f"{len(spec.features)} | {fmt(m['mcc'])} | {fmt(m.get('auc', float('nan')))} | "
            f"{fmt(b['B1_yesterday']['mcc'])} / {fmt(b['B2_last7']['mcc'])} | "
            f"[{fmt(dd['lo95'])}, {fmt(dd['hi95'])}] | {bo['hits']}/{bo['calls']} = {fmt(bo['precision'])} "
            f"(lo95 {fmt(bo['precision_wilson_lo95'])}) |")
    print(json.dumps(s, indent=1, default=str))
    if not a.no_save:
        d = evaluate.write_run(spec, df, dict(manifest, strict_timing=a.strict), pred, info, s, a.holdout)
        with open(evaluate.ROOT / "LOG.md", "a") as f:
            f.write(line.replace("| ", f"| `{d.name}` | ", 1) + "\n")
        print("wrote", d)
    print(line)


if __name__ == "__main__":
    main()
