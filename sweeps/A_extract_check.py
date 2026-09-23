# Agent A: print a random sample of yellowtail sentences with the v2 extractor's region
# and polarity, for hand-checking (D-A01). Reports 2010-2014 only (never >= 2015).
import json, random, sqlite3, sys, collections
sys.path.insert(0, '.')
from yt import events, source
db = source.open_db(source.source_manifest())
rows = []
for rd, nj in db.execute("SELECT report_date, narrative_json FROM fishdope_reports "
                         "WHERE report_date BETWEEN '2010-01-01' AND '2014-12-31'"):
    n = json.loads(nj or "{}")
    text = "\n".join(f"{k}\n{v}" for part in ("highlights", "bait_report", "sections")
                     for k, v in (n.get(part) or {}).items())
    for e in events.yt_evidence(text):
        rows.append((rd, e))
print("yt sentences:", len(rows))
print("region:", collections.Counter(e["region"] for _, e in rows))
loc = [(rd, e) for rd, e in rows if e["region"] == "local"]
print("local polarity:", collections.Counter(e["pol"] for _, e in loc))
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
random.seed(seed)
mode = sys.argv[2] if len(sys.argv) > 2 else "local"
pool = {"local": loc, "catch": [r for r in loc if r[1]["pol"] == "catch"],
        "neg": [r for r in loc if r[1]["pol"] == "neg"],
        "all": rows}[mode]
for i, (rd, e) in enumerate(random.sample(pool, min(40, len(pool)))):
    print(f"[{i:02d}] {rd} head={e['head']} reg={e['region']} pol={e['pol']} qty={e['qty']} who={e['who']} "
          f"rec={e['rec']} tr={e['trend']}\n     {e['sent'][:300]}")
