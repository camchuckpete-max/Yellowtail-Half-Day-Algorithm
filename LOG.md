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
| `20260923T205037Z_e001_logreg_all_mcc` | e001_logreg_all_mcc | dev | 41 | 0.520 | 0.854 | 0.611 / 0.450 | [-0.154, -0.013] | 4/7 = 0.571 (lo95 0.250) |
| `20260923T205046Z_e001_logreg_all_p50` | e001_logreg_all_p50 | dev | 41 | 0.531 | 0.854 | 0.611 / 0.450 | [-0.154, 0.008] | 1/3 = 0.333 (lo95 0.061) |
| `20260923T205056Z_e001_logreg_all_p40` | e001_logreg_all_p40 | dev | 41 | 0.509 | 0.854 | 0.611 / 0.450 | [-0.167, -0.023] | 4/6 = 0.667 (lo95 0.300) |
| `20260923T205107Z_e002_hgb_all_p40` | e002_hgb_all_p40 | dev | 41 | 0.449 | 0.815 | 0.611 / 0.450 | [-0.240, -0.084] | 5/18 = 0.278 (lo95 0.125) |
| `20260923T205116Z_e003_logreg_recency_p50` | e003_logreg_recency_p50 | dev | 14 | 0.574 | 0.879 | 0.611 / 0.450 | [-0.092, 0.032] | 0/0 = nan (lo95 nan) |
| `20260923T205125Z_e003_logreg_recency_p40` | e003_logreg_recency_p40 | dev | 14 | 0.587 | 0.879 | 0.611 / 0.450 | [-0.076, 0.043] | 0/0 = nan (lo95 nan) |
| `20260923T205135Z_e004_breakout_logreg` | e004_breakout_logreg | dev | 41 | -0.048 | 0.797 | 0.611 / 0.450 | [-0.744, -0.543] | 1/11 = 0.091 (lo95 0.016) |
| `20260923T205159Z_e003_logreg_recency_p40` | e003_logreg_recency_p40 (strict) | dev | 14 | 0.521 | 0.852 | 0.536 / 0.436 | [-0.083, 0.072] | 2/11 = 0.182 (lo95 0.051) |
| `20260923T211023Z_e005_recency_d1_C001_p35` | e005_recency_d1_C001_p35 | dev | 15 | 0.640 | 0.893 | 0.611 / 0.450 | [0.005, 0.058] | 0/0 = nan (lo95 nan) |
| `20260923T211108Z_e005_recency_d1_C001_p35` | e005_recency_d1_C001_p35 (strict) | dev | 15 | 0.574 | 0.871 | 0.536 / 0.436 | [-0.005, 0.104] | 0/1 = 0.000 (lo95 0.000) |
| `20260923T211117Z_e006_recency_d1_fishdope_C003_p35` | e006_recency_d1_fishdope_C003_p35 | dev | 28 | 0.640 | 0.889 | 0.611 / 0.450 | [0.005, 0.073] | 0/0 = nan (lo95 nan) |
| `20260923T211127Z_e006_recency_d1_fishdope_C003_p35` | e006_recency_d1_fishdope_C003_p35 (strict) | dev | 28 | 0.554 | 0.863 | 0.536 / 0.436 | [-0.042, 0.094] | 2/7 = 0.286 (lo95 0.082) |
| `20260923T211536Z_e007_recency_d1_fdsent_C003_p35` | e007_recency_d1_fdsent_C003_p35 | dev | 28 | 0.655 | 0.891 | 0.611 / 0.450 | [0.018, 0.078] | 0/0 = nan (lo95 nan) |
| `20260923T211626Z_e007_recency_d1_fdsent_C003_p35` | e007_recency_d1_fdsent_C003_p35 (strict) | dev | 28 | 0.532 | 0.867 | 0.536 / 0.436 | [-0.062, 0.071] | 3/10 = 0.300 (lo95 0.108) |
| `20260923T215602Z_eB01_fleet_C003_mccrange` | eB01_fleet_C003_mccrange | dev | 24 | 0.645 | 0.895 | 0.611 / 0.450 | [0.006, 0.061] | 2/3 = 0.667 (lo95 0.208) |
| `20260923T215613Z_eB02_fleet_fdsent_C003_p35` | eB02_fleet_fdsent_C003_p35 | dev | 37 | 0.653 | 0.891 | 0.611 / 0.450 | [0.012, 0.074] | 1/3 = 0.333 (lo95 0.061) |
| `20260923T215728Z_eB01_fleet_C003_mccrange` | eB01_fleet_C003_mccrange (strict) | dev | 24 | 0.550 | 0.873 | 0.536 / 0.436 | [-0.038, 0.073] | 7/22 = 0.318 (lo95 0.164) |
| `20260923T215739Z_eB02_fleet_fdsent_C003_p35` | eB02_fleet_fdsent_C003_p35 (strict) | dev | 37 | 0.534 | 0.864 | 0.536 / 0.436 | [-0.061, 0.064] | 3/17 = 0.176 (lo95 0.062) |
| `20260923T224019Z_e005_recency_d1_C001_p35` | e005_recency_d1_C001_p35 | dev | 15 | 0.624 | 0.887 | 0.606 / 0.435 | [-0.002, 0.040] | 0/2 = 0.000 (lo95 0.000) |
| `20260923T224019Z_eB01_fleet_C003_mccrange` | eB01_fleet_C003_mccrange | dev | 24 | 0.626 | 0.891 | 0.606 / 0.435 | [-0.002, 0.042] | 2/5 = 0.400 (lo95 0.118) |
| `20260923T224020Z_e007_recency_d1_fdsent_C003_p35` | e007_recency_d1_fdsent_C003_p35 | dev | 28 | 0.625 | 0.887 | 0.606 / 0.435 | [-0.007, 0.045] | 3/6 = 0.500 (lo95 0.188) |
| `20260923T224024Z_e008_e007_monthly` | e008_e007_monthly | dev | 28 | 0.614 | 0.890 | 0.606 / 0.435 | [-0.020, 0.036] | 3/9 = 0.333 (lo95 0.121) |
| `20260923T224024Z_e009_eB01_monthly_p40` | e009_eB01_monthly_p40 | dev | 24 | 0.627 | 0.893 | 0.606 / 0.435 | [-0.002, 0.045] | 4/6 = 0.667 (lo95 0.300) |
| `20260924T045443Z_eE01_tripmodel_calib` | eE01_tripmodel_calib | dev | 3 | 0.632 | 0.882 | 0.606 / 0.435 | [0.002, 0.048] | 0/0 = nan (lo95 nan) |
