"""Build (and cache) the PIT feature + label table for a given source snapshot."""
from __future__ import annotations

import hashlib

import pandas as pd

from . import events, features, source

WARMUP_DAYS = 30  # first 30 days of data are used only as history, never as targets


def build(strict: bool = False) -> tuple[pd.DataFrame, dict]:
    manifest = source.source_manifest()
    key = hashlib.sha256((str(sorted(manifest["files"].items())) + f"strict={strict}"
                          + _code_hash()).encode()).hexdigest()[:16]
    path = source.CACHE_DIR / f"dataset_{key}.pkl"
    if path.exists():
        df = pd.read_pickle(path)
    else:
        db = source.open_db(manifest)
        trips = events.load_trips(db, strict=strict)
        fc = events.load_forecasts(db)
        lab = events.labels(trips)
        first = trips["fished_date"].min() + pd.Timedelta(days=WARMUP_DAYS)
        lab = lab[lab["date"] >= first].reset_index(drop=True)
        feat = features.build(trips, fc, pd.DatetimeIndex(lab["date"]))
        df = feat.merge(lab, on="date", how="inner")
        df.to_pickle(path)
    manifest = dict(manifest, strict_timing=strict, dataset_cache_key=key,
                    n_rows=len(df), first_date=str(df["date"].min().date()),
                    last_date=str(df["date"].max().date()),
                    table_sha256=hashlib.sha256(
                        pd.util.hash_pandas_object(df.drop(columns=["cutoff"]), index=False).values.tobytes()
                    ).hexdigest())
    return df, manifest


def _code_hash() -> str:
    from pathlib import Path
    h = hashlib.sha256()
    for name in ("events.py", "features.py", "dataset.py"):
        h.update((Path(__file__).parent / name).read_bytes())
    return h.hexdigest()
