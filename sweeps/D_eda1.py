# Agent D EDA on dev days 2014-2016 (the only dev years with bait-barge data). Selection on dev: disclosed (D-D03).
# configurations scored: 0
import sys; sys.path.insert(0, '.')
import pandas as pd
from yt import dataset, evaluate
df, _ = dataset.build(); df = evaluate.eligible(df)
d = df[(df["date"] >= "2014-01-01") & (df["date"] < "2017-01-01")]
print("days", len(d), "bb_have", round(d["bb_have"].mean(), 3))
for c in ("bb_loc_sardine", "bb_sd_sardine", "bb_loc_mackerel", "bb_loc_anchovy", "bb_loc_short", "bb_reg_squid",
          "bb_stale", "bb_sardine_change", "fo_loc_sardine", "fo_reg_squid", "fo_loc_out"):
    print(c, d.groupby(["hd_yt_lastday", c])["y"].agg(["mean", "size"]).round(3).to_dict("index"))
for c in ("bb_sardine_in_c", "bb_reg_sardine", "bb_sardine_frac_7", "fo_reg_sardine"):
    q = pd.qcut(d[c].rank(method="first"), 4, labels=False)
    print(c, d.groupby(["hd_yt_lastday", q])["y"].agg(["mean", "size"]).round(3).to_dict("index"),
          "corr with y", round(d[c].corr(d["y"]), 3))
