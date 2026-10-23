# Benchmark v0 — qwen3.6-27b

Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).

| track | items (test) | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|
| ecthr | 217 | 66.8 / 0.744 | 65.9 / 0.750 | — | 90.3 / 0.920 |
| nlupp | 424 | 41.5 / 0.731 | 26.7 / 0.631 | — | 58.3 / 0.790 |
| sata | 1137 | 33.0 / 0.795 | 28.1 / 0.684 | — | 46.4 / 0.797 |
| synthetic | 205 | 97.6 / 0.995 | 56.6 / 0.800 | — | 86.3 / 0.967 |
| unfair_tos | 566 | 92.8 / 0.928 | 88.2 / 0.882 | — | 98.9 / 0.992 |

# Per-track details — qwen3.6-27b

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 62.7 [56.2, 69.6] | 0.798 | 0.756 | 0.819 | 0.645 | 0.38 | 1.33 (1.09) | 1.296 |
| noul_ctx+platt | 66.8 [60.8, 73.3] | 0.744 | 0.725 | 0.788 | 0.705 | 0.33 | 0.95 (1.09) | 1.056 |
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| pick@top1 | 65.9 [59.4, 72.4] | 0.750 | 0.726 | 0.771 | 0.719 | 0.33 | 1.00 (1.09) | — |
| pick+true_count | 90.3 [86.2, 94.5] | 0.920 | 0.915 | 0.903 | 1.000 | 0.00 | 1.09 (1.09) | — |
| noul_ctx+true_count | 91.7 [88.0, 95.4] | 0.935 | 0.929 | 0.920 | 1.000 | 0.00 | 1.09 (1.09) | — |
| pick+count | 57.6 [51.2, 64.5] | 0.700 | 0.671 | 0.765 | 0.594 | 0.45 | 1.06 (1.09) | 1.322 |
| noul_ctx+count | 57.1 [50.7, 64.1] | 0.694 | 0.664 | 0.755 | 0.594 | 0.47 | 1.03 (1.09) | 1.282 |
| pick+dev_prior | 65.9 [59.4, 72.4] | 0.750 | 0.726 | 0.771 | 0.719 | 0.33 | 1.00 (1.09) | 1.375 |
| noul_ctx+dev_prior | 67.3 [60.8, 73.7] | 0.762 | 0.738 | 0.781 | 0.719 | 0.34 | 1.00 (1.09) | 1.335 |
| write | 55.8 [49.3, 62.2] | 0.774 | 0.720 | 0.787 | 0.562 | 0.53 | 1.52 (1.09) | — |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 1.296 | 0.119 | 0.0 % | 0.0 % | 0.251 |
| noul_ctx+platt | 1.056 | 0.101 | 0.0 % | 0.0 % | 0.214 |
| pick+count | 1.322 | 0.082 | 2.3 % | 2.3 % | 0.290 |
| noul_ctx+count | 1.282 | 0.093 | 0.5 % | 0.5 % | 0.300 |
| pick+dev_prior | 1.375 | 0.212 | 18.4 % | 4.1 % | 0.196 |
| noul_ctx+dev_prior | 1.335 | 0.227 | 34.1 % | 0.5 % | 0.192 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +23.50 pts [+17.97, +29.03] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -1.38 pts [-4.61, +1.84] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +24.42 pts [+18.89, +30.41] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -32.72 pts [-38.71, -26.73] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -24.42 pts [-30.41, -18.89] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -5.53 pts [-11.07, +0.01] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.01 nats [-0.12, +0.09] |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 42.7 [38.0, 47.2] | 0.741 | 0.674 | 0.784 | 0.514 | 0.60 | 2.11 (1.93) | 3.100 |
| noul_ctx+platt | 41.5 [36.8, 46.2] | 0.731 | 0.662 | 0.768 | 0.495 | 0.60 | 1.69 (1.93) | 2.572 |
| always_none | 13.7 [10.4, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| pick@top1 | 17.5 [13.9, 21.0] | 0.512 | 0.415 | 0.523 | 0.224 | 1.21 | 1.00 (1.93) | — |
| pick+true_count | 58.3 [53.8, 63.0] | 0.790 | 0.732 | 0.739 | 1.000 | 0.00 | 1.93 (1.93) | — |
| noul_ctx+true_count | 71.0 [66.7, 75.2] | 0.866 | 0.825 | 0.839 | 1.000 | 0.00 | 1.93 (1.93) | — |
| pick+count | 30.7 [26.7, 35.1] | 0.654 | 0.567 | 0.649 | 0.361 | 0.84 | 1.24 (1.93) | 4.678 |
| noul_ctx+count | 32.1 [27.8, 36.6] | 0.676 | 0.588 | 0.668 | 0.370 | 0.83 | 1.25 (1.93) | 3.922 |
| pick+dev_prior | 26.7 [22.6, 31.1] | 0.631 | 0.541 | 0.660 | 0.366 | 0.87 | 1.82 (1.93) | 4.207 |
| noul_ctx+dev_prior | 30.9 [26.7, 35.4] | 0.666 | 0.580 | 0.693 | 0.399 | 0.80 | 1.83 (1.93) | 3.451 |
| write | 43.9 [39.2, 48.8] | 0.735 | 0.668 | 0.763 | 0.542 | 0.53 | 1.78 (1.93) | — |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.100 | 0.085 | 1.4 % | 1.4 % | 0.380 |
| noul_ctx+platt | 2.572 | 0.053 | 5.0 % | 1.4 % | 0.397 |
| pick+count | 4.678 | 0.332 | 3.1 % | 2.6 % | 0.482 |
| noul_ctx+count | 3.922 | 0.415 | 3.1 % | 1.4 % | 0.503 |
| pick+dev_prior | 4.207 | 0.090 | 0.0 % | 0.0 % | 0.680 |
| noul_ctx+dev_prior | 3.451 | 0.112 | 0.2 % | 0.2 % | 0.592 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +15.57 pts [+10.61, +20.52] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -12.74 pts [-16.75, -8.73] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +40.80 pts [+36.08, +45.28] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -27.59 pts [-31.84, -23.58] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -31.60 pts [-35.85, -27.12] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -10.61 pts [-15.33, -5.66] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.82 nats [+0.59, +1.07] |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 29.4 [26.7, 32.0] | 0.770 | 0.673 | 0.787 | 0.368 | 1.01 | 3.02 (3.60) | 3.653 |
| noul_ctx+platt | 33.0 [30.2, 35.7] | 0.795 | 0.704 | 0.806 | 0.399 | 0.91 | 3.31 (3.60) | 3.115 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.463 | 0.321 | 0.408 | 0.000 | 2.60 | 1.00 (3.60) | — |
| pick+true_count | 46.4 [43.4, 49.1] | 0.797 | 0.716 | 0.781 | 1.000 | 0.00 | 3.60 (3.60) | — |
| noul_ctx+true_count | 59.9 [57.0, 62.8] | 0.862 | 0.802 | 0.861 | 1.000 | 0.00 | 3.60 (3.60) | — |
| pick+count | 8.7 [7.1, 10.4] | 0.606 | 0.474 | 0.622 | 0.135 | 1.85 | 2.19 (3.60) | 6.026 |
| noul_ctx+count | 13.9 [12.0, 16.0] | 0.645 | 0.522 | 0.678 | 0.174 | 1.64 | 2.22 (3.60) | 5.033 |
| pick+dev_prior | 28.1 [25.5, 30.6] | 0.684 | 0.576 | 0.636 | 0.403 | 1.58 | 2.05 (3.60) | 4.487 |
| noul_ctx+dev_prior | 31.9 [29.2, 34.7] | 0.731 | 0.629 | 0.689 | 0.410 | 1.47 | 2.22 (3.60) | 3.494 |
| write | 34.9 [32.1, 37.8] | 0.789 | 0.699 | 0.802 | 0.417 | 0.96 | 3.02 (3.60) | — |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.653 | 0.209 | 1.5 % | 0.9 % | 0.507 |
| noul_ctx+platt | 3.115 | 0.022 | 1.5 % | 1.4 % | 0.459 |
| pick+count | 6.026 | 0.369 | 0.0 % | 0.0 % | 0.917 |
| noul_ctx+count | 5.033 | 0.357 | 0.0 % | 0.0 % | 0.886 |
| pick+dev_prior | 4.487 | 0.096 | 5.5 % | 3.9 % | 0.491 |
| noul_ctx+dev_prior | 3.494 | 0.132 | 15.8 % | 4.4 % | 0.419 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 30.1 | 67.3 | -0.58 | 1.01 | 4.9 | 29 |
| noul_ctx+platt | 33.5 | 70.4 | -0.29 | 0.91 | 4.2 | 18 |
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| pick@top1 | 0.0 | 32.1 | -2.60 | 2.60 | 8.1 | 0 |
| pick+true_count | 46.4 | 71.6 | +0.00 | 0.00 | 12.1 | 0 |
| noul_ctx+true_count | 59.9 | 80.2 | +0.00 | 0.00 | 3.3 | 0 |
| pick+count | 9.0 | 47.4 | -1.42 | 1.85 | 7.6 | 37 |
| noul_ctx+count | 14.3 | 52.2 | -1.38 | 1.64 | 7.5 | 33 |
| pick+dev_prior | 28.1 | 57.6 | -1.55 | 1.58 | 12.9 | 0 |
| noul_ctx+dev_prior | 31.9 | 62.9 | -1.39 | 1.47 | 10.7 | 0 |
| write | 35.4 | 69.9 | -0.58 | 0.96 | 4.4 | 14 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +13.37 pts [+10.29, +16.27] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -13.54 pts [-16.27, -10.91] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +46.35 pts [+43.36, +49.08] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -37.64 pts [-40.46, -34.83] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -18.29 pts [-20.49, -16.18] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -15.48 pts [-18.12, -12.75] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +1.38 nats [+1.24, +1.50] |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 93.2 [89.8, 96.6] | 0.987 | 0.978 | 0.988 | 0.932 | 0.07 | 2.73 (2.79) | 0.123 |
| noul_ctx+platt | 97.6 [95.6, 99.5] | 0.995 | 0.992 | 0.996 | 0.976 | 0.02 | 2.79 (2.79) | 0.288 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| pick@top1 | 19.5 [14.1, 24.9] | 0.567 | 0.449 | 0.505 | 0.195 | 1.88 | 1.00 (2.79) | — |
| pick+true_count | 86.3 [81.5, 90.7] | 0.967 | 0.948 | 0.944 | 1.000 | 0.00 | 2.79 (2.79) | — |
| noul_ctx+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.79 (2.79) | — |
| pick+count | 77.1 [71.2, 82.9] | 0.953 | 0.924 | 0.930 | 0.868 | 0.14 | 2.71 (2.79) | 1.105 |
| noul_ctx+count | 88.3 [83.9, 92.2] | 0.979 | 0.965 | 0.978 | 0.883 | 0.12 | 2.72 (2.79) | 0.572 |
| pick+dev_prior | 56.6 [49.8, 62.9] | 0.800 | 0.745 | 0.782 | 0.566 | 1.03 | 1.98 (2.79) | 2.352 |
| noul_ctx+dev_prior | 77.1 [71.2, 82.9] | 0.917 | 0.897 | 0.929 | 0.771 | 0.39 | 2.67 (2.79) | 1.820 |
| write | 92.7 [88.8, 95.6] | 0.987 | 0.978 | 0.987 | 0.927 | 0.07 | 2.72 (2.79) | — |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 0.123 | 0.020 | 100.0 % | 95.1 % | 0.005 |
| noul_ctx+platt | 0.288 | 0.016 | 100.0 % | 100.0 % | 0.002 |
| pick+count | 1.105 | 0.194 | 74.6 % | 45.4 % | 0.065 |
| noul_ctx+count | 0.572 | 0.210 | 74.1 % | 48.8 % | 0.055 |
| pick+dev_prior | 2.352 | 0.393 | 32.7 % | 15.6 % | 0.177 |
| noul_ctx+dev_prior | 1.820 | 0.569 | 29.3 % | 3.9 % | 0.150 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | -11.22 pts [-16.10, -6.82] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -13.66 pts [-18.54, -9.27] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +66.83 pts [+60.49, +73.17] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -9.27 pts [-13.66, -5.37] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -29.76 pts [-36.10, -23.41] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -4.88 pts [-8.78, -0.98] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.45 nats [+0.39, +0.52] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 70.8 [67.1, 74.4] | 0.721 | 0.718 | 0.439 | 0.710 | 0.30 | 0.42 (0.13) | 1.476 |
| noul_ctx+platt | 92.8 [90.6, 94.7] | 0.928 | 0.928 | 0.623 | 0.928 | 0.08 | 0.09 (0.13) | 0.253 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [8.0, 12.9] | 0.109 | 0.108 | 0.197 | 0.110 | 0.89 | 1.00 (0.13) | — |
| pick+true_count | 98.9 [98.1, 99.6] | 0.992 | 0.991 | 0.917 | 1.000 | 0.00 | 0.13 (0.13) | — |
| noul_ctx+true_count | 99.3 [98.6, 99.8] | 0.995 | 0.994 | 0.944 | 1.000 | 0.00 | 0.13 (0.13) | — |
| pick+count | 73.7 [70.0, 77.2] | 0.746 | 0.744 | 0.460 | 0.744 | 0.26 | 0.38 (0.13) | 0.990 |
| noul_ctx+count | 74.2 [70.3, 77.7] | 0.751 | 0.749 | 0.476 | 0.746 | 0.26 | 0.38 (0.13) | 0.989 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.444 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.443 |
| write | 69.1 [65.2, 72.8] | 0.703 | 0.700 | 0.424 | 0.693 | 0.32 | 0.44 (0.13) | — |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 1.476 | 0.193 | 3.5 % | 1.4 % | 0.194 |
| noul_ctx+platt | 0.253 | 0.045 | 100.0 % | 92.9 % | 0.013 |
| pick+count | 0.990 | 0.167 | 55.5 % | 47.7 % | 0.097 |
| noul_ctx+count | 0.989 | 0.177 | 55.1 % | 47.0 % | 0.099 |
| pick+dev_prior | 0.444 | 0.046 | 48.2 % | 0.7 % | 0.103 |
| noul_ctx+dev_prior | 0.443 | 0.046 | 48.2 % | 0.7 % | 0.103 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +6.18 pts [+4.24, +7.95] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -0.35 pts [-0.88, +0.00] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.52 pts [+85.87, +91.17] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -25.27 pts [-28.98, -21.73] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.78 pts [-13.25, -8.13] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +3.36 pts [+1.24, +5.65] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.49 nats [-0.59, -0.39] |
