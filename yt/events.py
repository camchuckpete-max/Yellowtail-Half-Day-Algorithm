"""Turn source rows into timestamped observations ("events").

Every event carries `available_at`: the earliest local (America/Los_Angeles)
time at which we assume the observation was publicly knowable. The feature
builder may only see events with available_at <= the 21:00 PT cutoff on D-1.
The timing assumptions below are decisions D-003/D-004 in DECISIONS.md.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

PT = ZoneInfo("America/Los_Angeles")
LANDINGS = ("seaforth", "fishermans", "hm", "point_loma")  # San Diego landings, D-002

# Trip class -> local time on return_date at which the count is assumed public.
# None => not public until 00:00 the day after return (i.e. never visible at
# the 21:00 cutoff of its own return day). Conservative by design (D-003).
PUBLISH_TIME = {
    "hd_am": "14:00",         # returns ~12:30
    "hd_pm": "19:00",         # returns ~17:30-18:00
    "hd_unspecified": "19:00",  # "1/2 Day", "1/2 Day Trip": assume PM
    "hd_twilight": None,      # returns ~22:00-23:00
    "hd_night": None,         # hoop net / lobster, night trips
    "three_quarter": "19:30",  # returns ~17:00-18:30
    "full_day": None,         # returns ~18:00-20:00; too close to cutoff
    "overnight": "12:00",     # returns in the morning
    "multi_day": None,        # 1.5-day+ returns vary; assume late
}


def trip_class(trip_type: str | None, raw: str | None) -> str:
    raw = raw or ""
    if trip_type == "half_day":
        if "Twilight" in raw:
            return "hd_twilight"
        if "Hoop" in raw or "Lobster" in raw:
            return "hd_night"
        if raw.endswith("AM"):
            return "hd_am"
        if raw.endswith("PM"):
            return "hd_pm"
        return "hd_unspecified"
    if trip_type in ("three_quarter", "full_day", "overnight"):
        return trip_type
    return "multi_day"


def _available_at(return_date: str, cls: str, strict: bool) -> pd.Timestamp:
    day = datetime.fromisoformat(return_date)
    t = PUBLISH_TIME[cls]
    if strict or t is None:
        return pd.Timestamp(day + timedelta(days=1))
    h, m = map(int, t.split(":"))
    return pd.Timestamp(day.replace(hour=h, minute=m))


def load_trips(db: sqlite3.Connection, strict: bool = False) -> pd.DataFrame:
    """One row per reported boat-trip at the San Diego landings."""
    q = f"""SELECT id, landing, boat, trip_type, trip_type_raw, fished_date, return_date,
                   anglers, species_json
            FROM landing_counts
            WHERE source_kind='per_boat' AND fished_date IS NOT NULL AND return_date IS NOT NULL
              AND landing IN ({",".join("?" * len(LANDINGS))})"""
    rows = []
    for rid, landing, boat, tt, raw, fd, rd, anglers, sj in db.execute(q, LANDINGS):
        cls = trip_class(tt, raw)
        counts: dict[str, int] = {}
        for s in json.loads(sj or "[]"):
            k = s.get("species_key")
            if k:
                counts[k] = counts.get(k, 0) + int(s.get("kept") or 0) + int(s.get("released") or 0)
        rows.append({
            "src_id": rid, "landing": landing, "boat": boat, "cls": cls,
            "fished_date": pd.Timestamp(fd), "return_date": pd.Timestamp(rd),
            "anglers": anglers if anglers is not None else float("nan"),
            "yt": counts.get("yellowtail", 0),
            "bonito": counts.get("bonito", 0),
            "barracuda": counts.get("barracuda", 0),
            "calico": counts.get("calico_bass", 0),
            "rockfish": counts.get("rockfish", 0),
            "available_at": _available_at(rd, cls, strict),
        })
    df = pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)
    df["is_hd_fishing"] = df["cls"].isin(["hd_am", "hd_pm", "hd_unspecified", "hd_twilight"])
    return df


_ISSUE = re.compile(r"issue_utc=([0-9T:\-+]+)")


def load_forecasts(db: sqlite3.Connection, zone: str = "t_sd_coast") -> pd.DataFrame:
    """NWS coastal forecast for the target day, stamped with its issue time (PT)."""
    rows = []
    q = """SELECT id, condition_date, wind_speed_kt, swell_height_ft, swell_period_s, vintage
           FROM conditions_daily WHERE zone_id=? AND data_kind='forecast' AND source LIKE 'nws%'"""
    for rid, d, wind, sh, sp, vintage in db.execute(q, (zone,)):
        m = _ISSUE.search(vintage or "")
        if not m:
            continue  # no provable issue time -> unusable (D-005)
        issued = datetime.fromisoformat(m.group(1))
        if issued.tzinfo is None:
            issued = issued.replace(tzinfo=ZoneInfo("UTC"))
        rows.append({
            "src_id": rid, "target_date": pd.Timestamp(d),
            "wind_kt": wind, "swell_ft": sh, "swell_s": sp,
            "available_at": pd.Timestamp(issued.astimezone(PT).replace(tzinfo=None)),
        })
    return pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)


def labels(trips: pd.DataFrame) -> pd.DataFrame:
    """Truth for day D: any half-day fishing trip (AM/PM/unspecified/twilight) on D
    caught >=1 yellowtail. Days with no half-day fishing trip reported are not
    evaluable and get no row (D-001)."""
    hd = trips[trips["is_hd_fishing"]]
    g = hd.groupby("fished_date").agg(n_trips=("yt", "size"), yt_total=("yt", "sum"))
    g["y"] = (g["yt_total"] > 0).astype(int)
    g.index.name = "date"
    return g.reset_index()
