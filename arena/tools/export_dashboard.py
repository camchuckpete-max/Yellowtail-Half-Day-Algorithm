"""Build a publishable dashboard directory from a run: index.html, state.json and one detail file
per agent (`agents/<name>.json`) with every nightly decision (briefing, reasoning, actions,
rejections, outcome) and every planning turn.

    python3 -m arena.tools.export_dashboard --run arena/runs/<id> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ARENA = Path(__file__).resolve().parents[1]


def export(run: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    (out / "agents").mkdir(exist_ok=True)
    shutil.copy(ARENA / "dashboard" / "index.html", out / "index.html")
    state = json.loads((run / "live" / "state.json").read_text())
    shutil.copy(run / "live" / "state.json", out / "state.json")
    turns_all = [json.loads(l) for l in (run / "turns.jsonl").read_text().splitlines()] if (run / "turns.jsonl").exists() else []
    sizes = {}
    # Briefings are split into "## " sections and deduplicated two ways: a section shared by several
    # agents on the same night is stored once in nights/<masked>.json; a section an agent repeats
    # across nights (notes, journal) is stored once in its own file. Agents keep a list of
    # (section hash, where) per night and the dashboard reassembles the text on demand.
    import hashlib, re
    (out / "nights").mkdir(exist_ok=True)
    per_night: dict[str, dict[str, str]] = {}          # masked -> {hash: text}
    per_night_count: dict[str, dict[str, int]] = {}    # masked -> {hash: agents using it}
    raw_sections: dict[str, dict[str, list[tuple[str, str]]]] = {}   # agent -> masked -> [(hash, text)]

    def sections_of(text: str) -> list[tuple[str, str]]:
        parts = re.split(r"(?=\n## )", text)
        return [(hashlib.sha1(pt.encode()).hexdigest()[:12], pt) for pt in parts if pt]

    # pass 1: count section usage per night
    night_logs: dict[str, list[dict]] = {}
    for a in state["agents"]:
        f = run / "judgment" / f"{a['name']}.jsonl"
        recs = []
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        night_logs[a["name"]] = recs
        for r in recs:
            if r.get("prompt"):
                secs = sections_of(r["prompt"])
                raw_sections.setdefault(a["name"], {})[r["masked"]] = secs
                cnt = per_night_count.setdefault(r["masked"], {})
                for h, _ in secs:
                    cnt[h] = cnt.get(h, 0) + 1

    def encode_briefing(name: str, masked: str, own_blobs: dict[str, str]) -> list | None:
        secs = raw_sections.get(name, {}).get(masked)
        if not secs:
            return None
        out_list = []
        for h, text in secs:
            if per_night_count[masked].get(h, 0) >= 2:
                per_night.setdefault(masked, {})[h] = text
                out_list.append([h, "n"])
            else:
                own_blobs[h] = text
                out_list.append([h, "a"])
        return out_list

    for a in state["agents"]:
        name = a["name"]
        nights = []
        own_blobs: dict[str, str] = {}
        if True:
            for r in night_logs.get(name, []):
                if "skipped" in r:
                    nights.append({"masked": r["masked"], "date": r["date"], "skipped": r["skipped"]})
                    continue
                ans = r.get("answer") or {}
                nights.append({"masked": r["masked"], "date": r["date"], "model": r.get("model"), "cost_usd": r.get("cost_usd"),
                               "seconds": r.get("seconds"), "error": r.get("error"), "reasoning": ans.get("reasoning"),
                               "note": ans.get("note"), "book": ans.get("book") or [], "commit_pto": ans.get("commit_pto") or [],
                               "actions": r.get("actions") or [], "rejected": r.get("rejected") or [], "briefing": encode_briefing(name, r["masked"], own_blobs)})
        turns = [{k: t.get(k) for k in ("tag", "season", "doy", "queries", "posts", "submitted", "adopted", "cost_usd", "ok", "error", "summary", "num_turns", "seconds")}
                 for t in turns_all if t.get("agent") == name]
        detail = {"name": name, "kind": a["kind"], "model": a.get("model"), "persona": a.get("persona"), "forum": a.get("forum"),
                  "nights": nights, "turns": turns, "trips": a.get("trips", []), "blobs": own_blobs}
        p = out / "agents" / f"{name}.json"
        p.write_text(json.dumps(detail, separators=(",", ":")))
        sizes[name] = p.stat().st_size
    buckets: dict[str, dict] = {}   # one file per season-month bucket keeps the published file count low
    for masked, blobs in per_night.items():
        season, doy = masked[1:3], int(masked[5:8])
        buckets.setdefault(f"S{season}_b{(doy - 1) // 31:02d}", {})[masked] = blobs
    for key, d in buckets.items():
        (out / "nights" / f"{key}.json").write_text(json.dumps(d, separators=(",", ":")))
    (out / "agents" / "index.json").write_text(json.dumps({"agents": sorted(sizes), "run": state["run"]["id"], "nights": len(per_night)}))
    sizes["_nights"] = sum(p.stat().st_size for p in (out / "nights").glob("*.json"))
    return sizes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sizes = export(Path(a.run), Path(a.out))
    print(f"exported {len(sizes)} agent files, {sum(sizes.values()) / 1e6:.1f} MB total, largest {max(sizes.values()) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
