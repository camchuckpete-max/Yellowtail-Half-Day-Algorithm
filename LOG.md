# Run log

One line per saved run. Columns: run id | experiment | dev/HOLDOUT | #features | model MCC | model AUC | baseline MCC B1 yesterday / B2 last-7 | 95% CI of MCC(model) − MCC(best baseline) | breakout hits/calls = precision (Wilson lo95)

| run | experiment | split | #feat | MCC | AUC | B1 / B2 MCC | ΔMCC CI | breakout |
|---|---|---|---|---|---|---|---|---|
| `20260923T204723Z_e001_logreg_all_mcc` | e001_logreg_all_mcc | dev | 41 | 0.520 | 0.854 | 0.591 / 0.450 | [-0.140, 0.012] | 0/0 = nan (lo95 nan) |
| `20260923T204733Z_e001_logreg_all_p50` | e001_logreg_all_p50 | dev | 41 | 0.531 | 0.854 | 0.591 / 0.450 | [-0.140, 0.033] | 0/0 = nan (lo95 nan) |
| `20260923T204743Z_e001_logreg_all_p40` | e001_logreg_all_p40 | dev | 41 | 0.509 | 0.854 | 0.591 / 0.450 | [-0.153, 0.002] | 0/0 = nan (lo95 nan) |
| `20260923T204757Z_e002_hgb_all_mcc` | e002_hgb_all_mcc | dev | 41 | 0.188 | 0.815 | 0.591 / 0.450 | [-0.529, -0.293] | 14/183 = 0.077 (lo95 0.046) |
| `20260923T204807Z_e002_hgb_all_p50` | e002_hgb_all_p50 | dev | 41 | 0.416 | 0.815 | 0.591 / 0.450 | [-0.270, -0.081] | 1/2 = 0.500 (lo95 0.095) |
| `20260923T204818Z_e002_hgb_all_p40` | e002_hgb_all_p40 | dev | 41 | 0.449 | 0.815 | 0.591 / 0.450 | [-0.231, -0.059] | 2/8 = 0.250 (lo95 0.071) |
| `20260923T204831Z_e003_logreg_recency_mcc` | e003_logreg_recency_mcc | dev | 14 | 0.362 | 0.879 | 0.591 / 0.450 | [-0.357, -0.116] | 4/53 = 0.075 (lo95 0.030) |
| `20260923T204841Z_e003_logreg_recency_p50` | e003_logreg_recency_p50 | dev | 14 | 0.574 | 0.879 | 0.591 / 0.450 | [-0.076, 0.056] | 0/0 = nan (lo95 nan) |
| `20260923T204850Z_e003_logreg_recency_p40` | e003_logreg_recency_p40 | dev | 14 | 0.587 | 0.879 | 0.591 / 0.450 | [-0.056, 0.063] | 0/0 = nan (lo95 nan) |
| `20260923T204900Z_e004_breakout_logreg` | e004_breakout_logreg | dev | 41 | 0.000 | 0.756 | 0.591 / 0.450 | [-0.663, -0.498] | 0/0 = nan (lo95 nan) |
| `20260923T204923Z_e003_logreg_recency_p40` | e003_logreg_recency_p40 (strict) | dev | 14 | 0.521 | 0.852 | 0.000 / 0.436 | [-0.021, 0.196] | 0/1 = 0.000 (lo95 0.000) |
| — | **Above: B1 = D-1 only, breakout window 7 days. Below: B1 = most recent visible day (D-016), breakout window 3 days (D-015).** | | | | | | | |
