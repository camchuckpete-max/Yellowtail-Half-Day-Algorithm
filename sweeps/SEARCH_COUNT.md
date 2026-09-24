# Dev-fold search ledger (D-023)

| Round | Source | Configurations scored on dev | Cumulative |
|---|---|---|---|
| iter 0 | archive/iter0_uncommitted_code | 10 | 10 |
| iter 1–4 | named specs in LOG.md (dev + strict) | 14 | 24 |
| sweep 1 | sweeps/sweep1_iter2_output.txt | 90 | 114 |
| sweep 2 | sweeps/sweep2_iter3_output.txt | 75 | 189 |
| sweep 3 | sweeps/sweep3_iter4_output.txt | 36 | 225 |
| agent A | branch `agent/A-fishdope-text` (not merged): A_sweep1..3 (21+12+5) + 1 bootstrap re-score | 39 | 264 |
| agent B | sweeps/B_sweep1..5_output.txt (13+18+11+6+2) + eB01/eB02 dev and strict runs (4) | 54 | 318 |
| agent C | sweeps/C_sweep1 (24) + C_sweep2 (20) + C_sweep3 (6); C_diag1 and C_final_bootstrap only re-score counted configs | 50 | 368 |
| sweep 4 | sweeps/sweep4_retrain_output.txt (dev 2012–2014) | 36 | 404 |
| iter 5 | finalists e005, e007, eB01, e008, e009 on dev 2012–2016 (D-027) | 5 | 409 |
| sweep 5 | sweeps/sweep5_tides_output.txt (dev 2012–2016, source 8b48084) | 6 | 415 |
| agent D | branch `agent/D-bait-barge`: D_sweep1 (12) + D_sweep2 (8) + finalist dev + strict (2) | 22 | 437 |
| agent E | branch `agent/E-trip-level`: E sweeps (28) + finalist dev + strict (2) | 30 | 467 |
| agent F | branch `agent/F-latent-state`: F_sweep1..3 (9+8+7) + 2 bootstrap re-runs + 1 strict | 27 | 494 |
| iter 6 | Goal 1 finalists e005, eB01, e009, e007 on dev 2012–2023 | 4 | 498 |

**Goal C (conditions only) — separate ledger:** C1 30, C2 60, C3 20, C4 15, C6 14, C7 8, C9 6 = 153.

**Goal D (per trip, La Jolla boats, conditions only) — separate ledger:** D1 16, D2 18, D2b 18 (re-run on complete data), D3 3, D4 descriptive, D5 9 = 64.

Holdout scorings for Goal 1: 0 of 3 allowed.
