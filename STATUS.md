# Status

_Updated after Goal D sweep D8 (source commit e24c47c)._

| Goal | Status |
|---|---|
| 1 — noticeably beat "repeat yesterday" | **Not met.** Dev 2012–2023 (D-033): best e005 0.581 vs B1 0.554 (+0.027, CI [+0.009, +0.045]; bar +0.05). Earlier, dev 2012–2016: best 0.633 vs 0.606 after 494 configurations (D-030). |
| 2 — fewest variables matching Goal 1 | Not started (goals worked in order, D-018). |
| 3 — breakout precision ≥ 40% (3-day window) | Not started (D-018). |

| C — conditions only (no fish counts, no FishDope) | Iteration 1 done (D-031–D-035). Forecast era (dev 2012–2016): nothing beats season-only (AUC 0.714 vs 0.709). SST era (dev 2021–2023): **SST alone AUC 0.803 vs season 0.762**, better Brier; yes/no MCC ≈ 0.30 for both. |
| D — per-trip, New Seaforth + Sea Watch, conditions only | In progress (D-036–D-047). Best: Scripps Pier water temp × trip type × season + ONI + 3-day temp change, walk-forward 2012–2023 **AUC 0.763**. Held-out bands (D-044): 0–5 % → 7 % observed, 35–65 % → 43 %, 85–100 % → 87 % (47 trips). No gain from tides, wind (buoys, KSAN, in-trip), pressure, upwelling, glider, sea level, kelp. Waiting on kelp-box SST backfill and request 0004 (HF-radar currents, clarity). |

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

## Tried and ruled out (dev 2012–2016)
FishDope text (mention counts, sentence-level, spot-level), water temperature from text, bait barges, NWS forecasts (wind, swell, seas, advisories), tides, moon, fleet/boat state, species mix, trip-level model, latent-state filter, monthly refit, recency weighting, recalibration, regime thresholds, boosting/ensembles.

## Holdout
Never accessed (0 of 3 allowed scorings used). Holdout = days ≥ 2024-01-01 (D-033).

## Waiting on
Source backfill: 2017 is partial (102 days); 2018–2025 not yet loaded. SST/chlorophyll
(2020+) and buoys (2022+) only become usable once those years' half-day counts load.
