# D-C01 hand-check sample for the FishDope water-temperature extractor (no model scored).
import sys, json, random; sys.path.insert(0, '.')
from yt import source, events
db = source.open_db(source.source_manifest())
rows = db.execute("SELECT report_id, report_date, narrative_json FROM fishdope_reports "
                  "WHERE report_date BETWEEN '2009-06-01' AND '2014-12-31'").fetchall()
allh, loc = [], []
for rid, rd, nj in rows:
    n = json.loads(nj or "{}")
    text = "\n".join(f"{k}\n{v}" for part in ("highlights", "bait_report", "sections") for k, v in (n.get(part) or {}).items())
    for sent in events._SENT_SPLIT.split(text):
        for v in events.water_temps(sent):
            allh.append((rd, v, sent.strip()[:220]))
    rt = events.region_texts(text)["local"]
    for sent in events._SENT_SPLIT.split(rt):
        for v in events.water_temps(sent, inshore=True):
            loc.append((rd, v, sent.strip()[:220]))
print(f"configurations scored: 0\nall-region extractions: {len(allh)}   inshore-local extractions: {len(loc)}")
random.seed(2026)
print("\n== sample A: all regions (is the value a water temperature?)")
for i, h in enumerate(random.sample(allh, 30)): print(i, h[0], h[1], "|", h[2].replace("\n", " "))
print("\n== sample B: inshore local (water temp? and inshore San Diego?)")
for i, h in enumerate(random.sample(loc, 30)): print(i, h[0], h[1], "|", h[2].replace("\n", " "))
