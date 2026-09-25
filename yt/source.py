"""Read-only access to the Daily-Fishing-Prediction data.

The only data source for this project is the Daily-Fishing-Prediction repo
(https://github.com/camchuckpete-max/Daily-Fishing-Prediction). We rebuild a
private SQLite DB from its `db_dump/*.sql.gz` files and record exactly which
commit and which file hashes were used, so every run can be reproduced.
"""
from __future__ import annotations

import gzip
import hashlib
import os
import sqlite3
import subprocess
from pathlib import Path

SOURCE_REPO = Path(os.environ.get("YT_SOURCE_REPO", "/home/user/Daily-Fishing-Prediction"))
CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"

# The only dump files read. Adding a table here is a logged decision.
DUMPS = ("landing_counts.sql.gz", "conditions_daily.sql.gz", "fishdope_reports.sql.gz",  # D-020
         "marine_forecast_products.sql.gz", "marine_forecasts.sql.gz",  # D-C02
         "coops_tide_predictions.sql.gz", "shore_station_temps.sql.gz", "buoy_observations.sql.gz",
         "upwelling_daily.sql.gz", "climate_indices.sql.gz",  # D-041 (Goal D, requests 0001-0003)
         "subsurface_temp_daily.sql.gz", "sea_level_anomaly.sql.gz",  # D-045
         "kelp_canopy_quarterly.sql.gz",  # D-046
         "metar_obs.sql.gz")  # D-047
# Row filters applied while streaming a dump (statement text -> keep?). Only the local stations of
# the ~1 GB buoy table are needed (D-041).
_LOCAL_BUOYS = ("46225", "46232", "46254", "46266", "LJPC1")
FILTERS_VERSION = "buoy-local-v1"  # part of the cache key: bump when STATEMENT_FILTERS change
STATEMENT_FILTERS = {
    "buoy_observations.sql.gz": lambda s: not s.startswith("INSERT INTO buoy_observations")
    or any(s.startswith(f"INSERT INTO buoy_observations VALUES('{b}'") for b in _LOCAL_BUOYS),
}


def _dump_files() -> list[tuple[str, str]]:
    """(file actually read, DUMPS entry it stands for). A dump the source later split into yearly
    shards (`<table>_<yyyy>.sql.gz`, e.g. buoy_observations from 2026-09-25) is read shard by shard
    in year order; each shard creates the table IF NOT EXISTS (D-052)."""
    out = []
    for name in DUMPS:
        if (SOURCE_REPO / "db_dump" / name).exists():
            out.append((name, name))
            continue
        stem = name[: -len(".sql.gz")]
        shards = sorted(p.name for p in (SOURCE_REPO / "db_dump").glob(f"{stem}_[0-9][0-9][0-9][0-9].sql.gz"))
        if not shards:
            raise FileNotFoundError(f"db_dump/{name} (and no yearly shards)")
        out += [(sh, name) for sh in shards]
    return out


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_manifest() -> dict:
    commit = subprocess.check_output(["git", "-C", str(SOURCE_REPO), "rev-parse", "HEAD"], text=True).strip()
    commit_time = subprocess.check_output(
        ["git", "-C", str(SOURCE_REPO), "log", "-1", "--format=%cI"], text=True).strip()
    dirty = subprocess.check_output(
        ["git", "-C", str(SOURCE_REPO), "status", "--porcelain", "db_dump"], text=True).strip()
    return {
        "source_repo": "camchuckpete-max/Daily-Fishing-Prediction",
        "source_commit": commit,
        "source_commit_time": commit_time,
        "db_dump_dirty": bool(dirty),
        "files": {f: _sha256(SOURCE_REPO / "db_dump" / f) for f, _ in _dump_files()},
    }


def open_db(manifest: dict) -> sqlite3.Connection:
    """Return a connection to a DB rebuilt from exactly the files in `manifest`."""
    key = hashlib.sha256(("".join(sorted(manifest["files"].values())) + FILTERS_VERSION).encode()).hexdigest()[:16]
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"source_{key}.db"
    if not path.exists():
        tmp = path.with_suffix(".tmp")
        tmp.unlink(missing_ok=True)
        db = sqlite3.connect(tmp)
        db.execute("PRAGMA foreign_keys=OFF")
        for fname, name in _dump_files():
            # Stream in statement-aligned chunks: large dumps exceed SQLite's max query size
            # when passed to executescript in one piece (D-038).
            with gzip.open(SOURCE_REPO / "db_dump" / fname, "rt") as f:
                batch: list[str] = []
                stmt: list[str] = []
                size = 0
                for line in f:
                    stmt.append(line)
                    s = "".join(stmt) if len(stmt) > 1 else line
                    if sqlite3.complete_statement(s):  # statement may span lines (newlines in text)
                        stmt = []
                        if s.strip().upper() in ("BEGIN TRANSACTION;", "COMMIT;"):
                            continue  # the dump's own transaction; each batch gets its own below
                        keep = STATEMENT_FILTERS.get(name)
                        if keep is not None and not keep(s):
                            continue
                        batch.append(s)
                        size += len(s)
                        if size > 50_000_000:
                            db.executescript("BEGIN;" + "".join(batch) + "COMMIT;")
                            batch, size = [], 0
                if stmt:
                    batch.append("".join(stmt))
                if batch:
                    db.executescript("BEGIN;" + "".join(batch) + "COMMIT;")
        db.commit()
        db.close()
        tmp.rename(path)
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
