# E01 readout scores — kev-4b

## goemotions (dev 133, test 267)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 4.5 [2.2, 7.1] | 0.242 | 0.261 | 0.154 | 2.99 (1.18) | 9.651 |
| noul+platt | 4.9 [2.6, 7.9] | 0.072 | 0.132 | 0.086 | 0.19 (1.18) | 3.926 |
| noul_ctx@0.5 | 3.0 [1.1, 5.2] | 0.257 | 0.291 | 0.169 | 2.60 (1.18) | 7.117 |
| noul_ctx+platt | 7.5 [4.5, 10.9] | 0.100 | 0.165 | 0.135 | 0.22 (1.18) | 3.763 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (1.18) | — |
| pick@top1 | 28.1 [22.5, 33.7] | 0.333 | 0.330 | 0.828 | 1.00 (1.18) | — |
| pick+true_count | 30.3 [24.7, 36.0] | 0.346 | 0.352 | 1.000 | 1.18 (1.18) | — |
| noul+true_count | 24.3 [19.1, 29.6] | 0.294 | 0.308 | 1.000 | 1.18 (1.18) | — |
| noul_ctx+true_count | 25.8 [20.6, 31.5] | 0.305 | 0.317 | 1.000 | 1.18 (1.18) | — |
| pick+count | 6.0 [3.4, 9.0] | 0.070 | 0.116 | 0.094 | 0.11 (1.18) | 4.530 |
| noul+count | 4.1 [1.9, 6.7] | 0.044 | 0.073 | 0.052 | 0.06 (1.18) | 4.803 |
| noul_ctx+count | 5.6 [3.0, 8.6] | 0.069 | 0.116 | 0.090 | 0.11 (1.18) | 4.593 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +22.85 pts [+17.60, +28.09] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +4.49 pts [+0.37, +8.99] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +2.25 pts [+0.75, +4.12] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.34 pts [-29.60, -19.10] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +2.62 pts [-0.75, +5.99] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | -1.50 pts [-4.12, +1.12] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -2.52 nats [-2.72, -2.32] |

## sata (dev 122, test 278)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 20.1 [15.5, 24.8] | 0.690 | 0.721 | 0.277 | 3.27 (3.58) | 4.256 |
| noul+platt | 18.0 [13.7, 22.7] | 0.693 | 0.723 | 0.234 | 3.41 (3.58) | 4.263 |
| noul_ctx@0.5 | 25.2 [20.1, 30.6] | 0.717 | 0.747 | 0.342 | 3.24 (3.58) | 3.892 |
| noul_ctx+platt | 23.4 [18.7, 28.4] | 0.734 | 0.752 | 0.324 | 3.52 (3.58) | 3.896 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (3.58) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.449 | 0.397 | 0.000 | 1.00 (3.58) | — |
| pick+true_count | 51.8 [46.0, 57.6] | 0.813 | 0.813 | 1.000 | 3.58 (3.58) | — |
| noul+true_count | 49.3 [43.5, 55.4] | 0.806 | 0.803 | 1.000 | 3.58 (3.58) | — |
| noul_ctx+true_count | 54.0 [47.8, 59.7] | 0.825 | 0.823 | 1.000 | 3.58 (3.58) | — |
| pick+count | 16.9 [12.6, 21.6] | 0.360 | 0.397 | 0.180 | 0.96 (3.58) | 4.430 |
| noul+count | 12.2 [8.6, 15.8] | 0.265 | 0.287 | 0.126 | 0.63 (3.58) | 4.642 |
| noul_ctx+count | 14.0 [10.1, 18.3] | 0.325 | 0.360 | 0.144 | 0.83 (3.58) | 4.406 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +26.62 pts [+21.58, +32.01] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -2.16 pts [-5.40, +1.08] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +51.80 pts [+46.04, +57.55] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -34.89 pts [-40.65, -29.50] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -11.15 pts [-15.83, -6.83] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +5.04 pts [+0.36, +9.71] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.51 nats [+0.36, +0.67] |

## synthetic (dev 95, test 205)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 88.8 [84.4, 93.2] | 0.973 | 0.979 | 0.893 | 2.82 (2.79) | 0.678 |
| noul+platt | 88.8 [84.4, 93.2] | 0.974 | 0.978 | 0.898 | 2.80 (2.79) | 0.372 |
| noul_ctx@0.5 | 86.8 [82.0, 91.2] | 0.971 | 0.977 | 0.868 | 2.83 (2.79) | 0.857 |
| noul_ctx+platt | 85.9 [81.0, 90.7] | 0.968 | 0.975 | 0.859 | 2.80 (2.79) | 0.390 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.000 | 0.044 | 0.00 (2.79) | — |
| pick@top1 | 19.5 [14.1, 24.9] | 0.567 | 0.505 | 0.195 | 1.00 (2.79) | — |
| pick+true_count | 99.5 [98.5, 100.0] | 0.998 | 0.998 | 1.000 | 2.79 (2.79) | — |
| noul+true_count | 98.0 [96.1, 99.5] | 0.995 | 0.993 | 1.000 | 2.79 (2.79) | — |
| noul_ctx+true_count | 99.5 [98.5, 100.0] | 0.998 | 0.998 | 1.000 | 2.79 (2.79) | — |
| pick+count | 61.5 [54.6, 68.3] | 0.827 | 0.857 | 0.615 | 2.21 (2.79) | 1.501 |
| noul+count | 61.0 [54.1, 67.8] | 0.854 | 0.876 | 0.615 | 2.28 (2.79) | 1.422 |
| noul_ctx+count | 58.5 [51.7, 65.4] | 0.837 | 0.858 | 0.585 | 2.22 (2.79) | 1.481 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul@0.5 | +10.73 pts [+6.34, +15.12] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.00 pts [-1.46, +1.46] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +80.00 pts [+74.63, +85.37] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -38.05 pts [-44.39, -31.22] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -28.29 pts [-35.12, -20.98] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | -1.95 pts [-6.34, +2.93] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.62 nats [+0.54, +0.70] |

## unfair_tos (dev 234, test 566)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 63.3 [59.4, 67.5] | 0.671 | 0.227 | 0.634 | 0.79 (0.13) | 3.060 |
| noul+platt | 91.0 [88.7, 93.3] | 0.917 | 0.547 | 0.910 | 0.08 (0.13) | 0.341 |
| noul_ctx@0.5 | 61.8 [57.6, 65.9] | 0.660 | 0.259 | 0.618 | 0.86 (0.13) | 2.354 |
| noul_ctx+platt | 92.2 [89.9, 94.3] | 0.926 | 0.589 | 0.922 | 0.07 (0.13) | 0.276 |
| always_none | 88.2 [85.3, 90.6] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [8.0, 12.9] | 0.108 | 0.194 | 0.110 | 1.00 (0.13) | — |
| pick+true_count | 98.9 [98.1, 99.6] | 0.992 | 0.917 | 1.000 | 0.13 (0.13) | — |
| noul+true_count | 98.4 [97.3, 99.3] | 0.986 | 0.861 | 1.000 | 0.13 (0.13) | — |
| noul_ctx+true_count | 98.9 [98.1, 99.6] | 0.993 | 0.917 | 1.000 | 0.13 (0.13) | — |
| pick+count | 82.9 [79.7, 86.0] | 0.834 | 0.510 | 0.832 | 0.24 (0.13) | 0.764 |
| noul+count | 89.2 [86.6, 91.7] | 0.893 | 0.504 | 0.896 | 0.11 (0.13) | 0.846 |
| noul_ctx+count | 85.9 [82.9, 88.9] | 0.862 | 0.533 | 0.860 | 0.19 (0.13) | 0.782 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +6.71 pts [+4.77, +8.83] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.00 pts [-0.53, +0.53] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.52 pts [+85.87, +90.99] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -16.08 pts [-19.08, -12.90] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +24.03 pts [+20.32, +27.92] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | -1.41 pts [-5.30, +2.65] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.57 nats [-1.69, -1.46] |
