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

Holdout scorings for Goal 1: 0 of 3 allowed.
