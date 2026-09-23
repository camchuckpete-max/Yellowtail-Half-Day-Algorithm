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


def region_texts(text: str) -> dict[str, str]:
    marks = [(m.start(), _KEY2REG[m.group(0)]) for m in _REGION_RE.finditer(text)]
    out = {r: [] for r in REGIONS}
    for i, (st, reg) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[reg].append(text[st:end])
    return {r: "\n".join(v) for r, v in out.items()}



# ------------------------------------------------------------ FishDope v2 (D-A01)
# Sentence-level yellowtail evidence with (1) paragraph-heading + spot-level region
# attribution, (2) clause-scoped negation, (3) who / how many / how recent / trend.
# Rule-based, no learned parameters; hand-check in sweeps/A_extract_check.txt.
_HEAD_REGION = [  # paragraph headings (line starts), longest first at match time
    ("local", ["La Jolla", "Point Loma", "Mission Bay", "San Diego Bay", "Imperial Beach", "Del Mar",
               "Pacific Beach", "Ocean Beach", "South of Oceanside / La Jolla", "San Diego Kelp", "Torrey Pines"]),
    ("coronado", ["Coronado Islands", "Coronados", "Tijuana Kelp", "Rosarito"]),
    ("north", ["Oceanside", "Carlsbad", "Dana Point", "San Onofre", "Newport", "Laguna", "Huntington"]),
    ("offshore", ["OFFSHORE", "Offshore", "9 Mile Bank", "Nine Mile Bank", "Upper Hidden", "Hidden Bank", "Cortez and",
                  "Cortez Bank", "Tanner", "Deep Hole", "Report from", "Kelp Paddies", "Kelps are", "Boat Name"]),
    ("other", ["LA Harbor", "Catalina", "San Clemente", "Channel Islands", "Ensenada", "Todos Santos", "Colonet",
               "San Martin", "Marina Del Rey", "King Harbor", "Santa Monica", "San Nicolas", "Santa Barbara", "Redondo",
               "Mexican waters", "Mexican Waters", "MEXICO", "Pyramid Cove", "East End", "West End", "Backside",
               "Capt. Dave"]),
]
_HEAD_NONE = re.compile(r"(?i)^(?:PZZ|NWS|WEATHER|Weather|Synopsis|SYNOPSIS|TODAY|TONIGHT|MON|TUE|WED|THU|FRI|SAT|SUN|"
                        r"Small Craft|SMALL CRAFT|Coastal Waters|Inner Waters|Outer Waters|Waters From|"
                        r"[A-Za-z' ]*Bait Barge|Bait Report|Squid Report|Lobster|Live Weather|LIVE Weather|Tide Tables|"
                        r"Remember Guys|Always make sure|If you go fishing|Private boaters need|Latest on FMM|Important Links|"
                        r"FCC License|You can purchase|Call Al|For those interested|Due to a major|Welcome to|Click here|"
                        r"Date|All reports|They are also asking|This is the list|It.s Time)")
_HEAD_RE = re.compile("|".join(re.escape(k) for _, ks in _HEAD_REGION for k in sorted(ks, key=len, reverse=True)))
_HEAD2REG = {k: r for r, ks in _HEAD_REGION for k in ks}
_SPOT_LOCAL = re.compile(  # named places: local wherever they appear
    r"(?i)La Jolla|\bLJ\b|Point Loma(?! Sport| Landing)|Pt\.? Loma|Mission Bay(?! Bait)|Mission Beach|Crystal Pier|"
    r"Pacific Beach|\bPB\b|Ocean Beach|\bOB\b|Sunset Cliffs|Imperial Beach|\bIB\b|Silver Strand|"
    r"Coronado(?! Island|s|[’']s)|Del Mar|Torrey Pines|Scripps|N(?:orth)?\s?W(?:est)? Corner|Bird Rock|Green Tanks|"
    r"Whistler|Tourmaline|Children'?s Pool|Wind ?'?n'? ?Sea|Zuniga|Bull Ring|Solana Beach|Cardiff|Encinitas|"
    r"Hill Street|Point Loma Pipe|IB Pipe")
_SPOT_LOCAL_WEAK = re.compile(  # generic names ("the Cove"): local only inside a local/unlabelled paragraph
    r"(?i)Black'?s|the Cove|\bcove\b|the Caves|the Pipe|Dropoff|Drop off|the 270|32 fathom|the 32\b|the kelp ?line|"
    r"kelp ?line|MPA|closed zone|the beach")
_SPOT_OUT = {
    "coronado": re.compile(r"(?i)Coronado Island|Coronados|South Island|North Island|Middle Grounds|Rockpile|"
                           r"Ribbon Kelp|South Kelp|the pile\b|Rosarito|Tijuana Kelp|TJ Kelp|the Islands\b|Lighthouse"),
    "north": re.compile(r"(?i)Oceanside|Carlsbad|Dana Point|San Onofre|Newport|Laguna|Barn Kelp|San Mateo|Huntington"),
    "offshore": re.compile(r"(?i)kelp padd|paddies|\bpaddy|9 ?Mile|Nine Mile|Upper 500|Lower 500|\b(?:the )?(?:1[0-9]{2}|2[0-9]{2}|3[0-9]{2}|4[0-9]{2})\b(?! ?(?:lb|pound|ft|feet|fathom))(?=\s|$|[.,/])|"
                           r"Cortez|Tanner|Hidden Bank|43 fathom|60 mile|Butterfly|Mushroom|Bank\b|offshore|miles? out\b"),
    "other": re.compile(r"(?i)Catalina|Clemente|\bSCI\b|Ensenada|Todos Santos|Colonet|San Martin|Mexican|Mexico|"
                        r"Santa Barbara|Channel Island|Anacapa|Santa Cruz|San Nicolas|Redondo|Malibu|Palos Verdes|Rocky Point|"
                        r"Horseshoe Kelp|Huntington Flats|Long Point|Avalon|Pyramid"),
}
_COORD = re.compile(r"\b(3[2-4])[.°](\d{2})(?:[.\d]*)\s*[x×X/]\s*(11[7-9])[.°](\d{2})")
_MILES = re.compile(r"(?i)\b(\d{1,3}(?:\.\d)?)\s*(?:to \d{1,3}\s*)?miles?\b")
_CLAUSE = re.compile(r"(?i)[,;:()]|\s(?:but|although|though|however|while|whereas|yet)\s|\s-\s|…")
_NEG2 = re.compile(r"(?i)\b(?:no|not|nothing|none|zero|without|never|nobody|haven'?t|hasn'?t|didn'?t|isn'?t|aren'?t|"
                   r"wasn'?t|weren'?t|don'?t|doesn'?t|lack of|absent|fizzled|died|dried up|disappeared|gone)\b|n[’']t\b")
_SPEC = re.compile(r"(?i)\b(?:chance|possib\w*|could|might|may|hop(?:e|ing)|should|looking for|expect\w*|if\b|in case|"
                   r"shot at|potential|waiting|wait for|keep an eye|anticipat\w*|soon|tournament|shootout|sign up|register|"
                   r"any day|would|will be|target(?:ing)?|try(?:ing)? for|search(?:ing)? for|look(?:ing)? (?:at|for)|"
                   r"best (?:shot|bet)|time to|going to|gonna|keep(?:ing)? an eye|a look|decide)\b")
_CATCH2 = re.compile(r"(?i)\b(?:caught|catch(?:ing|es)?|landed|land(?:ing)?|scor(?:ed|ing|es?)|boated|hook(?:ed|ing|up)|"
                     r"got|limit(?:s|ed)?|picked|pick(?:ing)?|(?<!little )(?<!a )bit\b(?! more)|biting|bite|took|stuck|gaffed|released|counts?|"
                     r"produc(?:ed|ing|es?)|jigged|put \w+ on|bagged|nailed|whack\w*|decked|ended up with|had \d+|"
                     r"captured|taken|catching|finding|snap|sample of|aboard|coming (?:from|over|up|in)|came (?:from|over|in)|fish count|went \d+|\d+\s*(?:lb|pound|#)s?)\b")
_SIGHT2 = re.compile(r"(?i)\b(?:seen|saw|see|sighted|showing|showed|show(?:s)?|puddling|boiling|breezing|breaking|foaming|"
                     r"spotted|marked|metered|meter(?:s|ing)?|marks|around|here|schools?|holding|present|up on|"
                     r"signal|sign|chasing|busting|swimming|cruising|roaming|found|on (?:the )?kelps?|under (?:the )?(?:kelp|birds)|"
                     r"there (?:are|is|were|was))\b")
_WORDQ = {"a": 1, "an": 1, "one": 1, "single": 1, "lone": 1, "two": 2, "couple": 2, "pair": 2, "three": 3, "few": 3,
          "some": 3, "four": 4, "five": 5, "handful": 4, "several": 5, "six": 6, "dozen": 12, "good": 10, "decent": 8,
          "numbers": 10, "plenty": 15, "lots": 15, "bunch": 10, "many": 15, "limits": 25, "limit": 25, "wide": 25,
          "great": 20, "excellent": 25, "tons": 30}
_QTY_NUM = re.compile(r"(?i)\b(\d{1,3})\s+(?:(?:nice|big|large|small|rat|quality|keeper|more|legal|good|\w+-?size[d]?|"
                      r"\d+\s*(?:to|-)\s*\d+\s*(?:lb|pound)s?|\d+\s*(?:lb|pound)s?)\s+){0,2}(?:yellowtail|yellows|yt)\b")
_QTY_WORD = re.compile(r"(?i)\b(a|an|one|single|lone|two|couple|pair|three|few|some|four|five|handful|several|six|dozen|"
                       r"good|decent|numbers|plenty|lots|bunch|many|limits?|wide|great|excellent|tons)\b")
_WHO_BOAT = re.compile(r"(?i)sport ?boats?|party boat|1/2 day|half day|3/4 day|three quarter|the fleet|"
                       r"New Seaforth|Dolphin|Sea Watch|Alexes|El Gato|Premier|Jig Strike|Alicia|Fisherman (?:III|3)|"
                       r"Daily Double|Mission Belle|Josie Lynn|Malihini|Penetrator|passengers|anglers|guys? on the")
_WHO_PRIV = re.compile(r"(?i)private|kayak|skiff|yak|\bhis boat|their boat|small boat|panga|\bhe\b|\bshe\b|we\b|our\b|"
                       r"\bI\b|called in|report(?:ed)? in|buddy|son|friend")
_REC_D0 = re.compile(r"(?i)\b(?:today|this morning|this afternoon|this evening|tonight)\b")
_REC_D1 = re.compile(r"(?i)\b(?:yesterday|last night|last evening)\b")
_REC_RECENT = re.compile(r"(?i)\b(?:lately|recently|recent|past (?:few|couple|several) days|this week|last (?:few|couple) days|"
                         r"still|continu\w+|again|every day|daily|each day)\b")
_REC_OLD = re.compile(r"(?i)\b(?:last week|a (?:few|couple) days ago|earlier this week|last weekend|weeks? ago|"
                      r"days ago|last month|last year|since)\b")
_TREND_UP = re.compile(r"(?i)\b(?:picking up|picked up|improv\w+|better|wide open|hot|excellent|great|good|exploded|"
                       r"on fire|red hot|awesome|solid|steady|took off|best|lit up|going off|pumping|productive)\b")
_TREND_DN = re.compile(r"(?i)\b(?:slow\w*|fizzl\w+|died|tapered|tough|scratch\w*|spotty|off\b|dropped|worse|quiet|"
                       r"lock(?:ed)?[ -]?jaw|finicky|picky|hit (?:and|or) miss|dead|mellow\w*|dried up|turned off|shut down)\b")


def _head_region(line: str, prev: str) -> str:
    s = line.lstrip(" *-—–·")
    m = _HEAD_RE.match(s)
    if m:
        return _HEAD2REG[m.group(0)]
    if _HEAD_NONE.match(s):
        return "none"
    return prev


def _coord_region(sent: str) -> str | None:
    regs = []
    for la, lam, lo, lom in _COORD.findall(sent):
        lat, lon = int(la) + int(lam) / 60, int(lo) + int(lom) / 60
        if 32.55 <= lat <= 33.0 and 117.1 <= lon <= 117.33:
            regs.append("local")
        elif lat < 32.55 and lon < 117.33:
            regs.append("coronado")
        else:
            regs.append("offshore")
    if not regs:
        return None
    return "local" if all(r == "local" for r in regs) else [r for r in regs if r != "local"][0]


def _sent_region(sent: str, head: str, yt_pos: int) -> str:
    c = _coord_region(sent)
    if c is not None:
        return c
    hits = [(abs(m.start() - yt_pos), "local") for m in _SPOT_LOCAL.finditer(sent)]
    if head in ("local", "none"):
        hits += [(abs(m.start() - yt_pos) + 1, "local") for m in _SPOT_LOCAL_WEAK.finditer(sent)]
    for reg, rx in _SPOT_OUT.items():
        hits += [(abs(m.start() - yt_pos), reg) for m in rx.finditer(sent)]
    m = _MILES.search(sent)
    if m and float(m.group(1)) > 6:
        hits.append((abs(m.start() - yt_pos), "offshore"))
    if hits:
        return min(hits)[1]
    return head


def _yt_clause(sent: str, pos: int) -> str:
    cuts = [0] + [m.end() for m in _CLAUSE.finditer(sent)] + [len(sent)]
    for a, b in zip(cuts, cuts[1:]):
        if a <= pos < b:
            return sent[a:b]
    return sent


def _qty(sent: str) -> int:
    m = _QTY_NUM.search(sent)
    if m:
        return min(int(m.group(1)), 100)
    ym = _YT_RE.search(sent)
    words = _QTY_WORD.findall(sent[max(0, ym.start() - 40):ym.start()]) if ym else []
    return max((_WORDQ[w.lower()] for w in words), default=1)


def classify_yt_sentence(sent: str) -> dict:
    """Polarity of one yellowtail sentence: catch / sight / neg / spec (hypothetical) /
    list (GPS spot list) / mention. Coordinates are removed before classifying."""
    if len(_COORD.findall(sent)) >= 2:
        return {"pol": "list", "qty": 0, "who": "unknown", "rec": "none", "trend": 0}
    sent = _COORD.sub(" ", sent)
    ym = _YT_RE.search(sent)
    cl = _yt_clause(sent, ym.start())
    if re.search(r"(?i)(?:yellowtail|yellows) (?:bait|kelp|shootout|tournament)|for (?:yellowtail|yellows)\b", cl) \
            and not _CATCH2.search(cl.replace("fishing", "")):
        pol = "spec"
    elif _NEG2.search(cl):
        pol = "neg"
    elif _SPEC.search(cl) and not _CATCH2.search(re.sub(_SPEC, "", cl)):
        pol = "spec"
    elif _CATCH2.search(cl) or _QTY_NUM.search(cl):
        pol = "catch"
    elif _SIGHT2.search(cl):
        pol = "sight"
    elif _CATCH2.search(sent) and not _NEG2.search(sent):
        pol = "catch"
    elif _SIGHT2.search(sent):
        pol = "sight"
    else:
        pol = "mention"
    return {"pol": pol, "qty": _qty(sent) if pol == "catch" else 0,
            "who": "boat" if _WHO_BOAT.search(sent) else ("private" if _WHO_PRIV.search(sent) else "unknown"),
            "rec": ("d0" if _REC_D0.search(sent) else "d1" if _REC_D1.search(sent) else
                    "old" if _REC_OLD.search(sent) else "recent" if _REC_RECENT.search(sent) else "none"),
            "trend": int(bool(_TREND_UP.search(sent))) - int(bool(_TREND_DN.search(sent)))}


# v2 splitter also breaks run-together sentences ("today.The", "today.32.25 x ...").
_SENT_SPLIT2 = re.compile(r"(?<=[.!?])\s+|\n+|(?<=[a-z0-9)”\"'][.!?])(?=[A-Z“\"])|(?<=[a-z][.!?])(?=\d{2}[.°\s]\d{2})")


def yt_evidence(text: str) -> list[dict]:
    """Every yellowtail sentence in a report with its region and classification."""
    out, head = [], "none"
    for line in text.split("\n"):
        head = _head_region(line, head)
        for sent in _SENT_SPLIT2.split(line):
            ym = _YT_RE.search(sent)
            if not ym:
                continue
            out.append({"region": _sent_region(sent, head, ym.start()), "head": head, "sent": sent,
                        **classify_yt_sentence(sent)})
    return out


def yt_evidence_summary(ev: list[dict]) -> dict[str, float]:
    """Per-report aggregates for the local half-day waters and the Coronados."""
    f: dict[str, float] = {}
    for reg in ("local", "coronado", "north", "offshore"):
        e = [x for x in ev if x["region"] == reg]
        c = [x for x in e if x["pol"] == "catch"]
        f[f"{reg}_catch"] = len(c)
        f[f"{reg}_sight"] = sum(x["pol"] == "sight" for x in e)
        f[f"{reg}_neg"] = sum(x["pol"] == "neg" for x in e)
        f[f"{reg}_qty"] = max((x["qty"] for x in c), default=0)
        if reg == "local":
            f["local_spec"] = sum(x["pol"] == "spec" for x in e)
            f["local_catch_boat"] = sum(x["who"] == "boat" for x in c)
            f["local_catch_priv"] = sum(x["who"] != "boat" for x in c)
            f["local_catch_fresh"] = sum(x["rec"] in ("d0", "d1") for x in c)
            f["local_catch_stale"] = sum(x["rec"] == "old" for x in c)
            f["local_neg_fresh"] = sum(x["pol"] == "neg" and x["rec"] in ("d0", "d1", "recent") for x in e)
            f["local_trend"] = sum(x["trend"] for x in e if x["pol"] in ("catch", "sight", "neg"))
            f["local_present"] = int(len(c) + f["local_sight"] > 0)
    return f


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
        for k, v in yt_evidence_summary(yt_evidence(text)).items():
            c[f"v2_{k}"] = v
        rows.append({"src_id": rid, "report_date": pd.Timestamp(day), "available_at": pd.Timestamp(t),
                     "stamp_kind": "published" if p else "assumed_19pt", "migrated": bool(u and u.date().isoformat() == BULK_MIGRATION_DAY),
                     **{f"yt_{k}": v for k, v in c.items()}})
    df = pd.DataFrame(rows).sort_values("available_at", kind="stable").reset_index(drop=True)
    return df, pd.DataFrame(rejected, columns=["src_id", "report_date", "reason"])
