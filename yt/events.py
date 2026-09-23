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


# ------------------------------------------------------------------ FishDope (D-020)
ET = ZoneInfo("America/New_York")
BULK_MIGRATION_DAY = "2013-08-26"  # 1429 pre-2013 reports share this updated_at; site migration
REGIONS = {
    "local": ["La Jolla", "Point Loma", "Mission Bay", "San Diego Bay", "Imperial Beach", "Del Mar",
              "Pacific Beach", "Ocean Beach"],
    "coronado": ["Coronado Islands", "Coronados"],
    "north": ["Oceanside", "Carlsbad", "Dana Point", "San Onofre", "Newport", "Laguna"],
    "other": ["LA Harbor", "Catalina", "San Clemente Island", "Channel Islands", "Ensenada", "Todos Santos",
              "Colonet", "OFFSHORE", "Offshore", "9 Mile Bank", "Marina Del Rey", "King Harbor",
              "Santa Monica", "San Nicolas", "Redondo", "Mexican waters", "Mexican Waters", "MEXICO"],
}
_REGION_RE = re.compile("|".join(re.escape(k) for ks in REGIONS.values() for k in sorted(ks, key=len, reverse=True)))
_KEY2REG = {k: r for r, ks in REGIONS.items() for k in ks}
_YT_RE = re.compile(r"(?i:yellowtail|\byellows\b)|\bYT\b")
_TITLE_DATE = re.compile(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)")
_NWS_STAMP = re.compile(r"\b[AP]M P[SD]T (?:MON|TUE|WED|THU|FRI|SAT|SUN) ([A-Z]{3}) (\d{1,2}) (20\d\d)")


def _stamp(s: str | None) -> datetime | None:
    try:
        return datetime.strptime(s.strip(), "%B %d, %Y at %I:%M %p")
    except (AttributeError, ValueError):
        return None


def yt_mentions_by_region(text: str) -> dict[str, int]:
    """Attribute text to the most recent region keyword; count yellowtail mentions."""
    out = {r: 0 for r in REGIONS}
    out["all"] = len(_YT_RE.findall(text))
    marks = [(m.start(), _KEY2REG[m.group(0)]) for m in _REGION_RE.finditer(text)]
    for i, (st, reg) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[reg] += len(_YT_RE.findall(text, st, end))
    return out


def load_fishdope(db: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (usable reports, rejected reports with reason)."""
    rows, rejected = [], []
    q = "SELECT report_id, report_date, title, published_at, updated_at, narrative_json FROM fishdope_reports"
    for rid, rd, title, pub, upd, nj in db.execute(q):
        try:
            day = datetime.fromisoformat(rd)
        except (TypeError, ValueError):
            rejected.append((rid, rd, "unparseable report_date")); continue
        m = _TITLE_DATE.search(title or "")
        if m and m.group(1) != day.strftime("%A"):
            rejected.append((rid, rd, f"title weekday {m.group(1)} != {day.strftime('%A')}")); continue
        n = json.loads(nj or "{}")
        text = "\n".join(f"{k}\n{v}" for part in ("highlights", "bait_report", "sections")
                         for k, v in (n.get(part) or {}).items())
        stamps = []
        for mon, dd, yy in _NWS_STAMP.findall(text):
            try:
                stamps.append(datetime.strptime(f"{mon} {dd} {yy}", "%b %d %Y"))
            except ValueError:
                pass
        if stamps and max(stamps) > day + timedelta(days=1):
            rejected.append((rid, rd, f"embedded NWS stamp {max(stamps).date()} after report date")); continue
        # Availability: stamps are US/Eastern (user: reports go live 6-7pm PT, stamps cluster 9-10pm).
        # Missing stamp -> 19:00 PT on report day (user-stated). A non-migration edit later than
        # publication delays availability to the edit time.
        p, u = _stamp(pub), _stamp(upd)
        t = None
        for cand in (p, None if (u is None or u.date().isoformat() == BULK_MIGRATION_DAY) else u):
            if cand is not None:
                c = cand.replace(tzinfo=ET).astimezone(PT).replace(tzinfo=None)
                t = c if t is None else max(t, c)
        if t is None:
            t = day.replace(hour=19)
        c = yt_mentions_by_region(text)
        rows.append({"src_id": rid, "report_date": pd.Timestamp(day), "available_at": pd.Timestamp(t),
                     "stamp_kind": "published" if p else "assumed_19pt", "migrated": bool(u and u.date().isoformat() == BULK_MIGRATION_DAY),
                     **{f"yt_{k}": v for k, v in c.items()}})
    df = pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)
    return df, pd.DataFrame(rejected, columns=["src_id", "report_date", "reason"])
