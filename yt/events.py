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

import numpy as np
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
            # D-B01: extra species for D-1 species-mix context (surface vs bottom fishing)
            "mackerel": counts.get("mackerel", 0),
            "sand_bass": counts.get("sand_bass", 0),
            "halibut": counts.get("halibut", 0),
            "white_seabass": counts.get("white_seabass", 0),
            "sheephead": counts.get("sheephead", 0),
            "whitefish": counts.get("whitefish", 0),
            "available_at": _available_at(rd, cls, strict),
        })
    df = pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)
    df["is_hd_fishing"] = df["cls"].isin(["hd_am", "hd_pm", "hd_unspecified", "hd_twilight"])
    return df


_ISSUE = re.compile(r"issue_utc=([0-9T:\-+]+)")


def load_forecasts(db: sqlite3.Connection, zone: str = "t_sd_coast") -> pd.DataFrame:
    """NWS coastal forecast for the target day, stamped with its issue time (PT)."""
    rows = []
    q = """SELECT id, condition_date, wind_speed_kt, swell_height_ft, swell_period_s, vintage,
                  wind_dir_deg, swell_dir_deg
           FROM conditions_daily WHERE zone_id=? AND data_kind='forecast' AND source LIKE 'nws%'"""
    for rid, d, wind, sh, sp, vintage, wdir, sdir in db.execute(q, (zone,)):
        m = _ISSUE.search(vintage or "")
        if not m:
            continue  # no provable issue time -> unusable (D-005)
        issued = datetime.fromisoformat(m.group(1))
        if issued.tzinfo is None:
            issued = issued.replace(tzinfo=ZoneInfo("UTC"))
        rows.append({
            "src_id": rid, "target_date": pd.Timestamp(d),
            "wind_kt": wind, "swell_ft": sh, "swell_s": sp, "wind_dir": wdir, "swell_dir": sdir,
            "available_at": pd.Timestamp(issued.astimezone(PT).replace(tzinfo=None)),
        })
    return pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)


# D-034: satellite ocean products (NOAA CoastWatch via the source's conditions_snapshot).
# Availability = data date + lag, applied conservatively: at the D-1 21:00 cutoff SST and
# currents dated <= D-2 are usable; chlorophyll (~3-week publication lag) only if >= 21 days old.
OCEAN_LAG_DAYS = {"noaacwBLENDEDsstDaily": 2, "noaacwBLENDEDNRTcurrentsDaily": 2, "noaacwN20VIIRSchlaDaily": 21}


def load_ocean(db: sqlite3.Connection) -> pd.DataFrame:
    """Long table: one row per (source, tile, data date) with sst_f / chl / current (D-034)."""
    q = f"""SELECT id, source, zone_id, condition_date, sst_f, chl, current_speed_kt, current_dir_deg
            FROM conditions_daily WHERE source IN ({",".join("?" * len(OCEAN_LAG_DAYS))})"""
    rows = []
    for rid, src, zone, d, sst, chl, cs, cd in db.execute(q, tuple(OCEAN_LAG_DAYS)):
        t = pd.Timestamp(d)
        rows.append({"src_id": rid, "source": src, "zone": zone, "target_date": t,
                     "sst_f": sst, "chl": chl, "cur_kt": cs, "cur_dir": cd,
                     # data dated t is public at (t + lag - 1 days) 20:00, i.e. usable for target day
                     # t + lag (cutoff (t + lag - 1) 21:00) and never earlier
                     "available_at": t + pd.Timedelta(days=OCEAN_LAG_DAYS[src] - 1, hours=20)})
    cols = ["src_id", "source", "zone", "target_date", "sst_f", "chl", "cur_kt", "cur_dir", "available_at"]
    return pd.DataFrame(rows, columns=cols).sort_values("available_at", kind="stable").reset_index(drop=True)


TIDE_LEAD_DAYS = 30  # D-029: predicted tides treated as public 30 days ahead (NOAA publishes a year+ ahead)


def load_tides(db: sqlite3.Connection, zone: str = "t_sd_coast") -> pd.DataFrame:
    """NOAA CO-OPS predicted daily high/low tide heights (single station; D-029)."""
    q = """SELECT id, condition_date, tide_high_ft, tide_low_ft FROM conditions_daily
           WHERE source='noaa_coops_tides' AND data_kind='forecast' AND zone_id=?"""
    rows = [{"src_id": rid, "target_date": pd.Timestamp(d), "tide_high_ft": h, "tide_low_ft": lo,
             "available_at": pd.Timestamp(d) - pd.Timedelta(days=TIDE_LEAD_DAYS)}
            for rid, d, h, lo in db.execute(q, (zone,))]
    df = pd.DataFrame(rows, columns=["src_id", "target_date", "tide_high_ft", "tide_low_ft", "available_at"])
    return df.sort_values("available_at", kind="stable").reset_index(drop=True)


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


_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_NEG = re.compile(r"(?i)\b(no|not|nothing|none|zero|without|haven'?t|hasn'?t|didn'?t|isn'?t|aren'?t|wasn'?t|"
                  r"weren'?t|never|lack|slow|quiet|dead|absent)\b|n't\b")
_CATCH = re.compile(r"(?i)\b(caught|catch(?:ing|es)?|landed|land(?:ing)?|scor(?:ed|ing)|boated|hook(?:ed|ing)|"
                    r"got|limits?|pick(?:ed)?|bit|biting|bite|took|stuck|gaffed|fish(?:ed)? for|counts?|"
                    r"\d+\s*(?:lb|pound)s?)\b")
_SIGHT = re.compile(r"(?i)\b(seen|saw|see|showing|showed|puddling|boiling|breezing|spotted|marked|metered|around|here)\b")


def classify_yt_sentences(text: str) -> dict[str, int]:
    """Sentence-level yellowtail evidence in one region's text (D-022):
    catch = yt + catch verb, no negation; sight = yt + sighting word, no negation,
    not a catch; neg = yt + negation."""
    out = {"catch": 0, "sight": 0, "neg": 0}
    for sent in _SENT_SPLIT.split(text):
        if not _YT_RE.search(sent):
            continue
        if _NEG.search(sent):
            out["neg"] += 1
        elif _CATCH.search(sent):
            out["catch"] += 1
        elif _SIGHT.search(sent):
            out["sight"] += 1
    return out


# Water temperature stated in report text (D-C01). A value is a 50-79 F number followed by a degree
# marker, in a sentence that talks about water and not about air.
_TEMP = re.compile(r"(?<![\d.])([5-7]\d(?:\.\d)?)(?:\s*(?:-|\u2013|to|/)\s*([5-7]\d(?:\.\d)?))?\s*"
                   r"(?:\u00b0\s*F?|\u00ba|degrees?|degree[\u2019'`]?s|deg\b|F\b(?=\s*(?:water|temp)))", re.I)
_WATER = re.compile(r"(?i)water|temp|WTMP|SST|green|blue|clean|color|break|surface")
_NOTWATER = re.compile(r"(?i)\bair\b|ATMP|deg true|high of|\bhighs?\b|outside temp|at the dock|\blows?\b|fever")
# Markers of offshore / non-local water inside a "local" region passage (bank numbers, GPS,
# mileage, tuna, station tables); such sentences are not counted as inshore temperatures.
_OFFSHORE = re.compile(r"(?i)\b\d{2}\.\d{2}(?:\.\d+)?\s*[x\u00d7]|\bx\s*11[78]\b|\b(?:209|302|267|238|1010|425|371|181|"
                       r"178|182|224|290|312|43|500|mile|miles|bank|tuna|bluefin|yellowfin|YFT|BFT|dorado|"
                       r"albacore|pens|canyon|Water Temps|Hueneme|Ventura|Anacapa|San Pedro|Santa Monica)\b")


def water_temps(text: str, inshore: bool = False) -> list[float]:
    """Water temperatures (F) stated in `text`; a range 'a-b' counts as its midpoint."""
    out = []
    for sent in _SENT_SPLIT.split(text):
        if _NOTWATER.search(sent) or not _WATER.search(sent) or (inshore and _OFFSHORE.search(sent)):
            continue
        for m in _TEMP.finditer(sent):
            a = float(m.group(1)); b = float(m.group(2)) if m.group(2) else a
            out.append((a + b) / 2 if a <= b <= a + 5 else a)
    return out


# Bait availability in local passages (incl. SD / Mission Bay bait-barge lines), D-C01.
_BAIT = {"sardine": re.compile(r"(?i)\bsardines?\b"), "squid": re.compile(r"(?i)\bsquid\b"),
         "anchovy": re.compile(r"(?i)\banchov(?:y|ies)\b"), "mackerel": re.compile(r"(?i)\bmackerel\b")}


def bait_mentions(text: str) -> dict[str, int]:
    """Sentences mentioning each bait, excluding negated ones ('no squid')."""
    out = {k: 0 for k in _BAIT}
    for sent in _SENT_SPLIT.split(text):
        for k, r in _BAIT.items():
            if r.search(sent) and not _NEG.search(sent):
                out[k] += 1
    return out


def region_texts(text: str) -> dict[str, str]:
    marks = [(m.start(), _KEY2REG[m.group(0)]) for m in _REGION_RE.finditer(text)]
    out = {r: [] for r in REGIONS}
    for i, (st, reg) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[reg].append(text[st:end])
    return {r: "\n".join(v) for r, v in out.items()}


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
        rt = region_texts(text)
        for reg in ("local", "coronado", "north"):
            for k, v in classify_yt_sentences(rt[reg]).items():
                c[f"{reg}_{k}"] = v
        wt_all, wt_loc = water_temps(text), water_temps(rt["local"], inshore=True)
        env = {"wt_all": float(np.median(wt_all)) if wt_all else np.nan, "wt_all_n": len(wt_all),
               "wt_local": float(np.median(wt_loc)) if wt_loc else np.nan,
               **{f"bait_local_{k}": v for k, v in bait_mentions(rt["local"]).items()}}
        rows.append({"src_id": rid, "report_date": pd.Timestamp(day), "available_at": pd.Timestamp(t), **env,
                     "stamp_kind": "published" if p else "assumed_19pt", "migrated": bool(u and u.date().isoformat() == BULK_MIGRATION_DAY),
                     **{f"yt_{k}": v for k, v in c.items()}})
    df = pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)
    return df, pd.DataFrame(rejected, columns=["src_id", "report_date", "reason"])


# ------------------------------------------------------------------ NWS coastal waters forecast (D-C02)
MF_ZONE = "PZZ750"  # coastal waters San Mateo Pt to Mexican border, out 30 nm (2005-2019 zone code)
_DISPLAY = re.compile(r"(\d{1,2})(\d\d) (AM|PM) (P[SD]T) \w{3} (\w{3}) (\d{1,2}) (\d{4})")
_SOUTH = {"S", "SSW", "SW", "SSE"}
_OFFSHORE_WIND = {"NE", "ENE", "E", "ESE", "SE", "NNE"}


def _display_time(s: str | None) -> datetime | None:
    """Issue time as printed in the product header, as naive PT."""
    m = _DISPLAY.search(s or "")
    if not m:
        return None
    try:
        d = datetime.strptime(f"{m[5]} {m[6]} {m[7]}", "%b %d %Y")
    except ValueError:
        return None
    return d.replace(hour=int(m[1]) % 12 + (12 if m[3] == "PM" else 0), minute=int(m[2]))


def load_marine_forecasts(db: sqlite3.Connection, zone: str = MF_ZONE) -> pd.DataFrame:
    """Daytime periods of the NWS CWF for `zone`, one row per (product, valid_date).
    available_at = the later of the archived as-issued time (IEM utcvalid) and the
    issue time printed in the product header (they disagree on 4 of 7,987 2010-14 products)."""
    q = """SELECT m.id, p.issue_time_utc, p.issue_local_display, m.period_label, m.valid_date, m.wind_dir,
                  m.wind_max_kt, m.gust_kt, m.seas_max_ft, m.wind_waves_max_ft, m.swell_json
           FROM marine_forecasts m JOIN marine_forecast_products p USING (product_id)
           WHERE m.zone_code=? AND m.parse_status != 'failed'"""
    rows = []
    for rid, iu, disp, lab, vd, wdir, wmax, gust, seas, ww, sj in db.execute(q, (zone,)):
        if "NIGHT" in lab.upper():
            continue  # daytime periods only (.TODAY / .MON ...): the half-day fishing window
        issued = datetime.fromisoformat(iu)
        if issued.tzinfo is None:
            issued = issued.replace(tzinfo=ZoneInfo("UTC"))
        t = issued.astimezone(PT).replace(tzinfo=None)
        dt = _display_time(disp)
        if dt is not None:
            t = max(t, dt)
        sw = json.loads(sj or "[]")
        h = lambda c: max([x.get("height_max_ft") or 0.0 for x in c] or [0.0])
        rows.append({
            "src_id": rid, "target_date": pd.Timestamp(vd), "available_at": pd.Timestamp(t),
            "mf_wind_max": wmax, "mf_gust": gust if gust is not None else 0.0,
            "mf_seas": seas if seas is not None else (h(sw) if ww is None else max(ww, h(sw))),
            "mf_wind_offshore": int((wdir or "") in _OFFSHORE_WIND),
            "mf_wind_south": int((wdir or "") in _SOUTH),
            "mf_swell_south": h([x for x in sw if x.get("dir") in _SOUTH]),
            "mf_swell_west": h([x for x in sw if x.get("dir") not in _SOUTH]),
        })
    return pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)
