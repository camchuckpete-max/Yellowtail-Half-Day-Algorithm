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
         "forage_observations.sql.gz")  # D-D01


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
        "files": {name: _sha256(SOURCE_REPO / "db_dump" / name) for name in DUMPS},
    }


def open_db(manifest: dict) -> sqlite3.Connection:
    """Return a connection to a DB rebuilt from exactly the files in `manifest`."""
    key = hashlib.sha256("".join(sorted(manifest["files"].values())).encode()).hexdigest()[:16]
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"source_{key}.db"
    if not path.exists():
        tmp = path.with_suffix(".tmp")
        tmp.unlink(missing_ok=True)
        db = sqlite3.connect(tmp)
        for name in DUMPS:
            with gzip.open(SOURCE_REPO / "db_dump" / name, "rt") as f:
                db.executescript("PRAGMA foreign_keys=OFF;" + f.read())
        db.commit()
        db.close()
        tmp.rename(path)
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
