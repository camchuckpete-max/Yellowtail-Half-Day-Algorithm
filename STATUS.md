# Status

_Updated after iteration 5 (source commit b09f41f)._

| Goal | Status |
|---|---|
| 1 — noticeably beat "repeat yesterday" | **Not met.** On dev 2012–2016 the best models beat B1 by +0.008 to +0.021 MCC (bar: +0.05, CI > 0). All CIs include 0. |
| 2 — fewest variables matching Goal 1 | Not started (goals worked in order, D-018). |
| 3 — breakout precision ≥ 40% (3-day window) | Not started (D-018). |

## What we know
- B1 ("most recent visible day had a half-day yellowtail") is a strong rule: dev MCC 0.606.
- Models rank days better than B1 (AUC ≈ 0.89 vs B1 ≈ 0.78) and give better-calibrated
  odds, but the yes/no call rarely differs from B1's, because the cases B1 gets wrong
  sit near 50/50 given everything available (catch history, fleet state, FishDope text,
  water temperature from text, NWS forecasts).
- The 0.655 found on 2012–2014 did not survive the two fresh years added in D-027
  (e007: 2015 −0.026, 2016 +0.009 vs B1). It was selection noise from 404 configurations.
- The target partly measures fleet activity (days with ≤2 half-day trips are 2% positive)
  and leans on one boat (New Seaforth on 76% of positive days).

## Holdout
Never accessed (0 of 3 allowed scorings used). Holdout = days ≥ 2017-01-01.

## Waiting on
Source backfill: 2017 is partial (102 days); 2018–2025 not yet loaded. SST/chlorophyll
(2020+) and buoys (2022+) only become usable once those years' half-day counts load.
