"""Build (and cache) the PIT feature + label table for a given source snapshot."""
from __future__ import annotations

import hashlib

import pandas as pd

from . import events, features, source, tripmodel

WARMUP_DAYS = 30  # first 30 days of data are used only as history, never as targets
# Trip-level model variants precomputed as day features (D-E01): column prefix -> tripmodel.build kwargs
TRIP_VARIANTS = {"tm": {"C": 0.1}, "tmb": {"C": 0.1, "boats": True},
                 # D-E03: extended boat/pair inputs; boosted yt model; recency-weighted training
                 "tmx": {"C": 0.1, "boats": True, "ext": True},
                 "tmh": {"boats": True, "ext": True, "kind": "hgb"},
                 "tmw": {"C": 0.1, "boats": True, "ext": True, "halflife": 365.0}}


def build(strict: bool = False) -> tuple[pd.DataFrame, dict]:
    manifest = source.source_manifest()
    src = str(sorted(manifest["files"].items())) + f"strict={strict}"
    key = hashlib.sha256((src + _code_hash()).encode()).hexdigest()[:16]
    path = source.CACHE_DIR / f"dataset_{key}.pkl"
    if path.exists():
        df = pd.read_pickle(path)
    else:
        db = source.open_db(manifest)
        trips = events.load_trips(db, strict=strict)
        # Day features (cached on their own code so trip-model variants do not rebuild them, D-E03)
        bkey = hashlib.sha256((src + _code_hash(("events.py", "features.py"))).encode()).hexdigest()[:16]
        bpath = source.CACHE_DIR / f"dayfeat_{bkey}.pkl"
        if bpath.exists():
            df = pd.read_pickle(bpath)
        else:
            fc = events.load_forecasts(db)
            fd_rep, fd_rej = events.load_fishdope(db)
            mf = events.load_marine_forecasts(db)
            fd_rej.to_csv(source.CACHE_DIR / f"fishdope_rejected_{key}.csv", index=False)
            lab = events.labels(trips)
            first = trips["fished_date"].min() + pd.Timedelta(days=WARMUP_DAYS)
            lab = lab[lab["date"] >= first].reset_index(drop=True)
            feat = features.build(trips, fc, pd.DatetimeIndex(lab["date"]), fd_rep, mf)
            df = feat.merge(lab, on="date", how="inner")
            df.to_pickle(bpath)
        days = pd.DatetimeIndex(df["date"])
        rows = None
        for pre, kw in TRIP_VARIANTS.items():
            tkey = hashlib.sha256((src + _code_hash(("events.py", "features.py", "tripmodel.py"))
                                   + pre + str(sorted(kw.items()))).encode()).hexdigest()[:16]
            tpath = source.CACHE_DIR / f"tripfeat_{tkey}.pkl"
            if tpath.exists():
                tm = pd.read_pickle(tpath)
            else:
                if rows is None:
                    rows = tripmodel.candidate_rows(trips, tripmodel.all_days(trips, days), strict=strict)
                tm = tripmodel.build(trips, days, prefix=pre, strict=strict, rows=rows, **kw)
                tm.to_pickle(tpath)
            df = df.merge(tm, on="date", how="left")
            a = df[f"audit_{pre}_label_at"]
            assert (a.isna() | (a <= df["cutoff"])).all()  # every trip label used was public by the cutoff
        df.to_pickle(path)
    manifest = dict(manifest, strict_timing=strict, dataset_cache_key=key,
                    n_rows=len(df), first_date=str(df["date"].min().date()),
                    last_date=str(df["date"].max().date()),
                    table_sha256=hashlib.sha256(
                        pd.util.hash_pandas_object(df.drop(columns=["cutoff"]), index=False).values.tobytes()
                    ).hexdigest())
    return df, manifest


def _code_hash(names=("events.py", "features.py", "dataset.py", "tripmodel.py")) -> str:
    from pathlib import Path
    h = hashlib.sha256()
    for name in names:
        h.update((Path(__file__).parent / name).read_bytes())
    return h.hexdigest()
