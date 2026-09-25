# D-052 check: the yearly-sharded buoy dump (f6cd218) loads the same local-station rows as the single-file dump (e24c47c).
import os, sys, subprocess; sys.path.insert(0, '.')
q = "SELECT station_id, substr(ts_utc,1,4) y, count(*) FROM buoy_observations WHERE ts_utc < '2026-09-24' GROUP BY 1,2"
out = {}
for snap in ("/home/user/dfp-e24c47c", "/home/user/dfp-f6cd218"):
    code = f"import sys; sys.path.insert(0,'.'); from yt import source; db=source.open_db(source.source_manifest()); print(sorted(db.execute({q!r}).fetchall()))"
    out[snap] = subprocess.check_output([sys.executable, "-c", code], env={**os.environ, "YT_SOURCE_REPO": snap}, text=True)
a, b = (eval(v) for v in out.values())
da, db_ = {(s, y): n for s, y, n in a}, {(s, y): n for s, y, n in b}
diff = {k: (da.get(k), db_.get(k)) for k in set(da) | set(db_) if da.get(k) != db_.get(k)}
print("station-years:", len(da), "vs", len(db_), "| differing:", len(diff))
for k in sorted(diff)[:20]: print(k, diff[k])
