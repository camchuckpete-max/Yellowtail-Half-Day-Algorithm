# Agent D: linkage and extraction quality of the FishDope bait-barge data (D-D01, D-D02).
# configurations scored: 0 (data audit only; reads dev-period reports <= 2016 for the samples)
import random, sys
sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import events, source
db = source.open_db(source.source_manifest())
fd, rej = events.load_fishdope(db)
bb, st = events.load_bait_barge(db, fd, rej)
print("change-log linkage:", st)
bbd_ = bb[bb["report_date"] < "2017-01-01"]
print("kept rows by report year (<= 2016 only; later years not inspected):", bbd_.groupby(bbd_["report_date"].dt.year).size().to_dict())
print("rejected reports that carried bait_barge rows were dropped:", st["rejected_report"])
lag = bbd_["asof_lag"].dropna()
print(f"as-of lag (report day - stamp), change-log <= 2016: n={len(lag)} median={lag.median()} p90={lag.quantile(.9)} max={lag.max()}")
dev = fd[fd["report_date"] < "2017-01-01"]
print("text parse: reports with a San Diego line by year:", dev[dev["bb_sd_seen"] == 1].groupby(dev["report_date"].dt.year).size().to_dict())
print("text parse: reports with a Mission Bay line by year:", dev[dev["bb_mb_seen"] == 1].groupby(dev["report_date"].dt.year).size().to_dict())
for k in ("sd", "mb"):
    v = dev[dev[f"bb_{k}_seen"] == 1]
    print(k, "state rates:", {c: round(float(v[f"bb_{k}_{c}"].mean()), 3) for c in
                              ("sardine", "anchovy", "mackerel", "squid", "out", "neg_sardine", "limited")},
          "sardine size median", v[f"bb_{k}_sardine_in"].median(), "lag median", v[f"bb_{k}_lag"].median())
# Agreement change-log vs text parse, per (report, local barge, species), dev period only.
# The change-log omits many (barge, species) pairs; where it has a row, does it agree with the text?
bbd = bb[(bb["report_date"] < "2017-01-01") & bb["barge"].isin(["sd", "mb"]) & (bb["species"] != "none")]
t = dev.set_index("src_id")
agree = n = 0; omit = tot = 0
for (rid, b, sp), g in bbd.groupby(["report_id", "barge", "species"]):
    x = t.loc[rid]
    if not x[f"bb_{b}_seen"] or sp == "squid":
        continue
    n += 1; agree += int(g["stocked"].iloc[-1] == x[f"bb_{b}_{sp}"])
print(f"change-log rows (sd/mb, sardine/anchovy/mackerel) agreeing with the text parse: {agree}/{n}")
have = set(zip(bbd["report_id"], bbd["barge"], bbd["species"]))
for rid, x in t.iterrows():
    for b in ("sd", "mb"):
        for sp in ("sardine", "anchovy", "mackerel"):
            if x[f"bb_{b}_seen"] and x[f"bb_{b}_{sp}"] == 1 and x["report_date"] >= pd.Timestamp("2013-09-01"):
                tot += 1; omit += int((rid, b, sp) not in have)
print(f"text-parse 'stocked' (sd/mb) with no change-log row for that report: {omit}/{tot}")
# Size attribution check: change-log anchovy rows whose size equals the sardine size on the same line.
same = bbd.pivot_table(index=["report_id", "barge"], columns="species", values="size_in", aggfunc="last")
if {"sardine", "anchovy"} <= set(same.columns):
    both = same.dropna(subset=["sardine", "anchovy"])
    print(f"change-log: anchovy size == sardine size on the same barge line: {(both['sardine'] == both['anchovy']).sum()}/{len(both)}")
# Random hand-check sample of the text parse (2013-09..2016), to be read by a human.
random.seed(0)
rows = db.execute("SELECT report_id, report_date, narrative_json FROM fishdope_reports "
                  "WHERE report_date BETWEEN '2013-09-01' AND '2016-12-31'").fetchall()
import json
from datetime import datetime
print("\n--- hand-check sample (40 local barge lines) ---")
k = 0
for rid, rd, nj in random.sample(rows, 60):
    segs = events.bait_barge_segments("\n".join((json.loads(nj).get("bait_report") or {}).values()))
    for b in ("sd", "mb"):
        if b in segs and k < 40:
            f = events.parse_barge(segs[b], datetime.fromisoformat(rd))
            print(k, rd, b, repr(segs[b][:150]), {a: v for a, v in f.items() if v == v and v != 0})
            k += 1
