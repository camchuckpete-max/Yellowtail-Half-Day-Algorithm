"""Visible-prefix access to the masked snapshot tables (SPEC §4.4).

`Tables` never opens the source DB: it reads the parquet snapshot written by `arena.api.snapshot`
and answers `visible(name, t)` with the rows whose `avail_t <= t` (a prefix, since tables are
sorted by `avail_t`)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


class Tables:
    def __init__(self, snapshot_dir: Path):
        self.dir = Path(snapshot_dir)
        self.meta = json.loads((self.dir / "meta.json").read_text())
        self.names = tuple(self.meta["tables"])
        self._df: dict[str, pd.DataFrame] = {}
        self._avail: dict[str, np.ndarray] = {}

    def table(self, name: str) -> pd.DataFrame:
        if name not in self._df:
            df = pd.read_parquet(self.dir / f"{name}.parquet")
            self._df[name] = df
            self._avail[name] = df["avail_t"].to_numpy()
        return self._df[name]

    def visible(self, name: str, t: float) -> pd.DataFrame:
        df = self.table(name)
        i = int(np.searchsorted(self._avail[name], t, side="right"))
        return df.iloc[:i]

    def poisoned(self, t: float, rng: np.random.Generator) -> "Tables":
        """A copy with every numeric value in rows available after `t` replaced by noise (PIT test)."""
        out = Tables.__new__(Tables)
        out.dir, out.meta, out.names, out._df, out._avail = self.dir, self.meta, self.names, {}, {}
        for name in self.names:
            df = self.table(name).copy()
            after = df["avail_t"].to_numpy() > t
            for c in df.columns:
                if c.startswith("avail_") or not after.any():
                    continue
                if pd.api.types.is_bool_dtype(df[c]):
                    df.loc[after, c] = rng.random(after.sum()) < 0.5
                elif pd.api.types.is_integer_dtype(df[c]):
                    df.loc[after, c] = pd.Series(rng.integers(0, 500, after.sum()), index=df.index[after]).astype(df[c].dtype)
                elif pd.api.types.is_numeric_dtype(df[c]):
                    df.loc[after, c] = pd.Series(rng.uniform(0, 500, after.sum()), index=df.index[after]).astype(df[c].dtype)
                elif df[c].dtype == object:
                    df.loc[after, c] = "POISON"
            out._df[name] = df
            out._avail[name] = df["avail_t"].to_numpy()
        return out
