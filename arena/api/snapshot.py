"""Materialise the PIT tables an agent may observe (SPEC §4.1) as masked parquet files.

Each source table is loaded ONCE through the repo's own loaders (`yt.events`, `yt.hourly`), which
carry the `available_at` rules and PIT tests, and written with every datetime column replaced by
masked columns:
  <col>_t       fractional days on the arena timeline (comparable with `ctx.now.t`)
  <col>_season  season index (1 = first configured season)
  <col>_doy     day of year
  <col>_hour    hour of day (timestamp columns only)
`available_at` is renamed `avail`. Row order is by `avail_t` so a visible prefix is a slice.
Tables added to the source without an `available_at` rule are not here (§4.1).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from yt import events, hourly
from arena.engine import calendar as cal

DATE_COLS = {"fished_date", "fish_date", "return_date", "target_date", "report_date", "date", "qstart"}
TS_COLS = {"available_at", "ts"}
DROP_COLS = {"src_id", "obs_date", "condition_date", "ts_utc", "quarter_start", "quarter", "month", "release_lag_days"}

TIDE_PRED_LEAD_DAYS = 365   # hourly tide predictions are published more than a year ahead (D-029 spirit)


def _mask_col(df: pd.DataFrame, col: str, first_year: int, ts: bool) -> pd.DataFrame:
    s = pd.to_datetime(df[col])
    epoch = pd.Timestamp(cal.EPOCH)
    t = (s - epoch).dt.total_seconds() / 86400.0
    out = {f"{col}_t": t.astype("float64"), f"{col}_season": (s.dt.year - first_year + 1).astype("Int16"),
           f"{col}_doy": s.dt.dayofyear.astype("Int16")}
    if ts:
        out[f"{col}_hour"] = (s.dt.hour + s.dt.minute / 60.0).astype("float32")
    df = df.drop(columns=[col])
    for k, v in out.items():
        df[k] = v
    return df


def mask_frame(df: pd.DataFrame, first_year: int, mask_years: bool = True) -> pd.DataFrame:
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
    if "available_at" in df.columns:
        df = df.rename(columns={"available_at": "avail"})
    for c in list(df.columns):
        if c in DATE_COLS or c == "avail" or c in TS_COLS:
            if not mask_years:
                df[f"{c}_iso"] = pd.to_datetime(df[c]).dt.strftime("%Y-%m-%d %H:%M")
            df = _mask_col(df, c, first_year, ts=(c == "avail" or c in TS_COLS))
    if "avail_t" in df.columns:
        df = df.sort_values("avail_t", kind="stable").reset_index(drop=True)
    return df


def _fishdope_text(db: sqlite3.Connection) -> pd.DataFrame:
    """Narrative text per report (§4.1: extracted fields AND narrative text)."""
    rows = []
    for rid, nj in db.execute("SELECT report_id, narrative_json FROM fishdope_reports"):
        n = json.loads(nj or "{}")
        text = "\n".join(f"{k}\n{v}" for part in ("highlights", "bait_report", "sections")
                         for k, v in (n.get(part) or {}).items())
        rows.append({"src_id": rid, "text": text})
    return pd.DataFrame(rows)


def load_raw_tables(db: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Unmasked tables with `available_at`, exactly as the repo's loaders define them."""
    t: dict[str, pd.DataFrame] = {}
    trips = events.load_trips(db)
    t["trips"] = trips.drop(columns=["is_hd_fishing"])
    t["forecasts"] = events.load_forecasts(db)
    t["marine_forecasts"] = events.load_marine_forecasts(db)
    t["tides"] = events.load_tides(db)
    t["ocean"] = events.load_ocean(db)
    fd, _ = events.load_fishdope(db)
    t["fishdope"] = fd.merge(_fishdope_text(db), on="src_id", how="left")
    h = hourly.load(db)
    ht = h["tides"].copy(); ht["available_at"] = ht["ts"] - pd.Timedelta(days=TIDE_PRED_LEAD_DAYS)
    t["hourly_tides"] = ht
    p = h["pier"].copy(); p["available_at"] = p["ts"]; t["pier"] = p
    b = pd.concat([g.assign(station=s) for s, g in h["buoy"].items()], ignore_index=True)
    b["available_at"] = b["ts"]; t["buoy"] = b
    m = h["metar"].copy(); m["available_at"] = m["ts"]; t["metar"] = m
    t["upwelling"] = h["upw"]
    t["climate"] = h["climate"]
    t["glider"] = h["glider"]
    t["sla"] = h["sla"]
    t["kelp"] = h["kelp"]
    c = h["chl"].copy(); c["available_at"] = c["date"] + pd.Timedelta(days=hourly.CHL_LAG_DAYS - 1, hours=21)  # D-048
    t["chl"] = c
    return t


TABLES = ("trips", "forecasts", "marine_forecasts", "tides", "ocean", "fishdope", "hourly_tides", "pier",
          "buoy", "metar", "upwelling", "climate", "glider", "sla", "kelp", "chl")


def write_snapshot(raw: dict[str, pd.DataFrame], out_dir: Path, first_year: int, mask_years: bool = True,
                   cutoff: datetime | None = None) -> dict:
    """Write masked parquet tables. With `cutoff`, only rows with available_at <= cutoff are written
    (the physical per-turn snapshot of §5.3)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"first_year": first_year, "mask_years": mask_years, "cutoff": cutoff.isoformat() if cutoff else None, "tables": {}}
    for name in TABLES:
        df = raw[name]
        if cutoff is not None:
            df = df[df["available_at"] <= pd.Timestamp(cutoff)]
        m = mask_frame(df, first_year, mask_years)
        m.to_parquet(out_dir / f"{name}.parquet", index=False)
        meta["tables"][name] = {"rows": int(len(m)), "columns": list(m.columns)}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta
