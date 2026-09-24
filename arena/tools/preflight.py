"""Arena Phase 0 preflight (SPEC §11 step 0).

Per trip class and season: trip rows, distinct fishing dates, null-angler rate, share of trips
with >= 1 yellowtail, pooled yellowtail per angler. Also verifies the source's `fished_date`
semantics for OVERNIGHT and DAY_1_5 (SPEC §4.3 #4, recorded in D-050 / D-051).

Run: python3 -m arena.tools.preflight [--out arena/preflight.md]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from yt import events, source

# arena class -> source classes (SPEC §2)
ARENA_CLASSES = {
    "HD_AM": ("hd_am",),
    "HD_PM": ("hd_pm", "hd_unspecified"),
    "TWILIGHT": ("hd_twilight",),
    "THREE_QUARTER": ("three_quarter",),
    "FULL_DAY": ("full_day",),
    "OVERNIGHT": ("overnight",),
    "DAY_1_5": ("day_1_5",),
}


def coverage(trips: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, srcs in ARENA_CLASSES.items():
        t = trips[trips["cls"].isin(srcs)]
        for season, g in t.groupby(t["fish_date"].dt.year):
            ok = g["anglers"].notna()
            ang = g.loc[ok, "anglers"].sum()
            rows.append({
                "class": name, "season": int(season), "trips": len(g),
                "fishing_dates": int(g["fish_date"].nunique()),
                "null_angler_rate": round(float((~ok).mean()), 3),
                "positive_share": round(float((g["yt"] > 0).mean()), 3),
                "yt_per_angler": round(float(g.loc[ok, "yt"].sum() / ang), 3) if ang else float("nan"),
            })
    return pd.DataFrame(rows).sort_values(["class", "season"]).reset_index(drop=True)


def date_semantics(trips: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cls in ("overnight", "day_1_5", "full_day", "three_quarter", "hd_am", "hd_pm", "hd_twilight", "multi_day"):
        g = trips[trips["cls"] == cls]
        if g.empty:
            continue
        off = (g["return_date"] - g["fished_date"]).dt.days
        rows.append({"cls": cls, "rows": len(g), "return_minus_fished_days": off.value_counts().to_dict(),
                     "fish_date_minus_fished_date": (g["fish_date"] - g["fished_date"]).dt.days.value_counts().to_dict(),
                     "publish_time": events.PUBLISH_TIME[cls]})
    return pd.DataFrame(rows)


def render(manifest: dict, cov: pd.DataFrame, sem: pd.DataFrame) -> str:
    out = ["# Arena preflight", "",
           f"Source commit `{manifest['source_commit'][:12]}` ({manifest['source_commit_time']}).",
           "Trips at the four SD landings (D-002), per-boat rows only; `fish_date` = day the boat fished (D-050).", "",
           "## Source date semantics (SPEC §4.3 #4)", "",
           "| cls | rows | return − fished (days: rows) | fish_date − fished_date | posted (PT, return day) |",
           "|---|---|---|---|---|"]
    for r in sem.itertuples():
        out.append(f"| {r.cls} | {r.rows} | {r.return_minus_fished_days} | {r.fish_date_minus_fished_date} | {r.publish_time or 'next day 00:00'} |")
    out += ["", "Finding: the source stores `fished_date = return_date − midnights_away` with `midnights_away = 1` for",
            "both overnight and 1.5-day rows. With the owner-stated schedules (overnight fishes its return day;",
            "1.5-day fishes the day before its 06:00 return) the source's `fished_date` is the **departure date**",
            "for OVERNIGHT and the **main fishing day** for DAY_1_5. The arena keys OVERNIGHT outcomes on",
            "`return_date` (= departure + 1) and DAY_1_5 on `fished_date` (= departure + 1); both equal `fish_date`.", "",
            "## Coverage per class and season", "",
            "| class | season | trips | fishing dates | null-angler rate | positive share | yt / angler |",
            "|---|---|---|---|---|---|---|"]
    for r in cov.itertuples():
        out.append(f"| {r._1} | {r.season} | {r.trips} | {r.fishing_dates} | {r.null_angler_rate} | {r.positive_share} | {r.yt_per_angler} |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "preflight.md"))
    a = ap.parse_args()
    m = source.source_manifest()
    trips = events.load_trips(source.open_db(m))
    cov, sem = coverage(trips), date_semantics(trips)
    text = render(m, cov, sem)
    Path(a.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
