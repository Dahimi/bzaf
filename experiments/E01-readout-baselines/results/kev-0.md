# E01 readout scores — kev-0.8b

## goemotions (dev 133, test 267)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 0.4 [0.0, 1.1] | 0.128 | 0.135 | 0.026 | 9.84 (1.18) | 18.099 |
| noul+platt | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (1.18) | 4.470 |
| noul_ctx@0.5 | 0.7 [0.0, 1.9] | 0.129 | 0.134 | 0.060 | 10.80 (1.18) | 19.490 |
| noul_ctx+platt | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (1.18) | 4.541 |
| pick@top1 | 30.3 [24.7, 36.0] | 0.355 | 0.351 | 0.828 | 1.00 (1.18) | — |
| pick+true_count | 31.8 [26.2, 37.5] | 0.365 | 0.362 | 1.000 | 1.18 (1.18) | — |
| pick+count | 4.9 [2.2, 7.9] | 0.063 | 0.092 | 0.060 | 3.63 (1.18) | 5.480 |
| noul+count | 0.7 [0.0, 1.9] | 0.020 | 0.072 | 0.007 | 4.20 (1.18) | 6.045 |
| noul_ctx+count | 0.4 [0.0, 1.1] | 0.017 | 0.072 | 0.004 | 4.41 (1.18) | 6.001 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +31.09 pts [+25.47, +36.71] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -26.97 pts [-32.58, -21.72] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -0.37 pts [-1.87, +0.75] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +0.37 pts [-0.75, +1.87] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -13.49 nats [-14.53, -12.47] |

## sata (dev 122, test 278)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 10.1 [6.8, 13.7] | 0.649 | 0.663 | 0.155 | 4.35 (3.58) | 5.226 |
| noul+platt | 15.1 [11.2, 19.4] | 0.594 | 0.636 | 0.245 | 2.85 (3.58) | 4.937 |
| noul_ctx@0.5 | 13.7 [10.1, 18.0] | 0.654 | 0.674 | 0.205 | 3.97 (3.58) | 4.962 |
| noul_ctx+platt | 13.3 [9.7, 17.6] | 0.607 | 0.657 | 0.201 | 3.02 (3.58) | 4.772 |
| pick@top1 | 0.0 [0.0, 0.0] | 0.405 | 0.363 | 0.000 | 1.00 (3.58) | — |
| pick+true_count | 45.0 [38.8, 50.7] | 0.750 | 0.760 | 1.000 | 3.58 (3.58) | — |
| pick+count | 4.0 [1.8, 6.5] | 0.270 | 0.318 | 0.043 | 1.17 (3.58) | 4.941 |
| noul+count | 0.7 [0.0, 1.8] | 0.190 | 0.275 | 0.007 | 1.34 (3.58) | 5.389 |
| noul_ctx+count | 2.5 [0.7, 4.7] | 0.225 | 0.306 | 0.029 | 1.37 (3.58) | 5.203 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul+platt | +29.86 pts [+23.74, +35.61] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -41.01 pts [-46.76, -35.25] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -11.15 pts [-15.47, -7.55] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +3.60 pts [-0.36, +7.91] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.24 nats [+0.11, +0.38] |

## synthetic (dev 95, test 205)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 57.1 [50.2, 63.9] | 0.893 | 0.908 | 0.600 | 2.65 (2.79) | 1.723 |
| noul+platt | 57.1 [50.2, 63.9] | 0.893 | 0.908 | 0.600 | 2.67 (2.79) | 1.246 |
| noul_ctx@0.5 | 67.3 [61.0, 74.1] | 0.905 | 0.928 | 0.688 | 2.72 (2.79) | 1.866 |
| noul_ctx+platt | 66.3 [60.0, 72.7] | 0.904 | 0.927 | 0.673 | 2.76 (2.79) | 1.048 |
| pick@top1 | 17.6 [12.2, 22.5] | 0.543 | 0.489 | 0.195 | 1.00 (2.79) | — |
| pick+true_count | 81.0 [75.6, 86.3] | 0.931 | 0.932 | 1.000 | 2.79 (2.79) | — |
| pick+count | 7.3 [3.9, 11.2] | 0.174 | 0.165 | 0.073 | 0.28 (2.79) | 3.429 |
| noul+count | 11.2 [7.3, 15.6] | 0.255 | 0.266 | 0.112 | 0.43 (2.79) | 2.635 |
| noul_ctx+count | 10.2 [6.3, 14.6] | 0.226 | 0.234 | 0.102 | 0.41 (2.79) | 2.739 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +13.66 pts [+6.83, +20.49] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -73.66 pts [-79.51, -67.32] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -57.07 pts [-64.39, -49.74] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +10.24 pts [+2.93, +17.56] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.87 nats [+0.79, +0.96] |

## unfair_tos (dev 234, test 566)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 17.7 [14.7, 20.9] | 0.212 | 0.052 | 0.177 | 4.40 (0.13) | 6.060 |
| noul+platt | 87.6 [85.0, 90.3] | 0.876 | 0.026 | 0.876 | 0.01 (0.13) | 0.525 |
| noul_ctx@0.5 | 44.3 [40.1, 48.6] | 0.495 | 0.175 | 0.445 | 1.28 (0.13) | 3.485 |
| noul_ctx+platt | 88.0 [85.3, 90.6] | 0.881 | 0.178 | 0.880 | 0.03 (0.13) | 0.366 |
| pick@top1 | 9.5 [7.1, 12.0] | 0.100 | 0.182 | 0.110 | 1.00 (0.13) | — |
| pick+true_count | 98.2 [97.2, 99.3] | 0.984 | 0.861 | 1.000 | 0.13 (0.13) | — |
| pick+count | 85.2 [82.2, 88.0] | 0.855 | 0.466 | 0.852 | 0.16 (0.13) | 1.477 |
| noul+count | 87.3 [84.6, 90.1] | 0.873 | 0.071 | 0.875 | 0.02 (0.13) | 1.601 |
| noul_ctx+count | 85.7 [82.7, 88.5] | 0.858 | 0.377 | 0.859 | 0.12 (0.13) | 1.514 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +10.25 pts [+7.77, +12.90] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -13.07 pts [-15.90, -10.25] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +41.34 pts [+36.93, +45.94] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +26.68 pts [+22.61, +30.74] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.97 nats [-2.09, -1.86] |
