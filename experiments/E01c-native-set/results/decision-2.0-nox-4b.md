# E01 readout scores — decision-2.0-nox-4b

## goemotions (dev 133, test 267, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 4.1 [1.9, 6.7] | 0.349 | 0.333 | 0.075 | 3.43 (1.18) | 9.250 |
| noul_ctx+platt | 16.9 [12.4, 21.3] | 0.212 | 0.304 | 0.292 | 0.42 (1.18) | 3.401 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (1.18) | — |
| pick@top1 | 33.7 [28.1, 39.3] | 0.401 | 0.399 | 0.828 | 1.00 (1.18) | — |
| pick+true_count | 37.8 [31.8, 43.4] | 0.428 | 0.444 | 1.000 | 1.18 (1.18) | — |
| noul_ctx+true_count | 35.6 [30.0, 41.2] | 0.396 | 0.413 | 1.000 | 1.18 (1.18) | — |
| pick+count | 13.5 [9.4, 17.6] | 0.255 | 0.364 | 0.236 | 0.79 (1.18) | 4.163 |
| noul_ctx+count | 12.7 [9.0, 16.9] | 0.218 | 0.338 | 0.228 | 0.61 (1.18) | 4.424 |
| pick+dev_prior | 33.7 [28.1, 39.3] | 0.401 | 0.399 | 0.828 | 1.00 (1.18) | 2.829 |
| noul_ctx+dev_prior | 31.1 [25.5, 36.3] | 0.378 | 0.378 | 0.828 | 1.00 (1.18) | 3.091 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +20.97 pts [+16.48, +26.22] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +2.25 pts [-1.12, +5.62] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +4.12 pts [+1.87, +6.74] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.34 pts [-29.59, -19.48] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -4.12 pts [-6.74, -1.87] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +8.61 pts [+4.87, +12.36] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -4.83 nats [-4.96, -4.69] |

## sata (dev 122, test 278, failed 16)

> **WARNING: 16 items failed (4 %)** and count as wrong. First error: `HTTP 503: b'{"error":{"code":"not_ready","message":"model decision-2.0-nox-4b is loading"}}'`. Re-run the readout to retry them.

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 29.1 [24.1, 34.9] | 0.726 | 0.761 | 0.338 | 3.09 (3.58) | 3.484 |
| noul_ctx+platt | 28.8 [23.7, 34.5] | 0.752 | 0.777 | 0.331 | 3.57 (3.58) | 3.381 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (3.58) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.449 | 0.401 | 0.000 | 1.00 (3.58) | — |
| pick+true_count | 54.0 [48.6, 60.1] | 0.788 | 0.820 | 0.960 | 3.63 (3.58) | — |
| noul_ctx+true_count | 52.9 [47.1, 59.0] | 0.790 | 0.818 | 0.960 | 3.63 (3.58) | — |
| pick+count | 31.7 [26.3, 37.1] | 0.641 | 0.713 | 0.353 | 2.77 (3.58) | 3.613 |
| noul_ctx+count | 32.0 [26.6, 37.8] | 0.600 | 0.684 | 0.345 | 2.54 (3.58) | 3.695 |
| pick+dev_prior | 31.7 [26.3, 37.4] | 0.668 | 0.641 | 0.428 | 2.31 (3.58) | 3.560 |
| noul_ctx+dev_prior | 29.1 [23.7, 34.5] | 0.667 | 0.639 | 0.396 | 2.43 (3.58) | 3.642 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +24.82 pts [+19.78, +30.58] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +1.08 pts [-2.52, +5.04] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +53.96 pts [+48.56, +60.07] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -22.30 pts [-27.35, -17.63] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -22.30 pts [-27.34, -17.63] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +2.88 pts [-2.16, +7.55] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.21 nats [+0.11, +0.32] |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 94.6 [91.7, 97.6] | 0.982 | 0.990 | 0.946 | 2.81 (2.79) | 0.455 |
| noul_ctx+platt | 94.6 [91.7, 97.6] | 0.982 | 0.990 | 0.946 | 2.81 (2.79) | 0.213 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.000 | 0.044 | 0.00 (2.79) | — |
| pick@top1 | 19.0 [13.7, 24.4] | 0.557 | 0.497 | 0.195 | 1.00 (2.79) | — |
| pick+true_count | 95.6 [92.2, 98.0] | 0.985 | 0.984 | 1.000 | 2.79 (2.79) | — |
| noul_ctx+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 2.79 (2.79) | — |
| pick+count | 84.4 [79.0, 88.8] | 0.967 | 0.969 | 0.844 | 2.92 (2.79) | 0.896 |
| noul_ctx+count | 87.8 [83.4, 92.2] | 0.974 | 0.978 | 0.878 | 2.87 (2.79) | 0.695 |
| pick+dev_prior | 70.2 [63.9, 76.6] | 0.840 | 0.846 | 0.707 | 2.40 (2.79) | 2.066 |
| noul_ctx+dev_prior | 76.6 [70.7, 82.4] | 0.886 | 0.888 | 0.766 | 2.43 (2.79) | 1.865 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +0.98 pts [-2.44, +4.39] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -4.39 pts [-7.80, -1.95] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +76.59 pts [+70.73, +82.44] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -11.22 pts [-15.61, -7.32] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -25.37 pts [-31.23, -19.51] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -6.83 pts [-11.22, -2.44] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.24 nats [+0.18, +0.30] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 52.1 [48.1, 56.2] | 0.566 | 0.286 | 0.523 | 0.75 (0.13) | 2.260 |
| noul_ctx+platt | 92.4 [90.3, 94.5] | 0.926 | 0.646 | 0.924 | 0.10 (0.13) | 0.229 |
| always_none | 88.2 [85.7, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [8.0, 12.9] | 0.109 | 0.197 | 0.110 | 1.00 (0.13) | — |
| pick+true_count | 99.1 [98.2, 99.8] | 0.993 | 0.931 | 1.000 | 0.13 (0.13) | — |
| noul_ctx+true_count | 98.9 [98.1, 99.6] | 0.991 | 0.917 | 1.000 | 0.13 (0.13) | — |
| pick+count | 69.6 [65.9, 73.3] | 0.734 | 0.390 | 0.696 | 0.49 (0.13) | 1.208 |
| noul_ctx+count | 72.8 [69.3, 76.5] | 0.761 | 0.411 | 0.728 | 0.45 (0.13) | 1.213 |
| pick+dev_prior | 88.2 [85.7, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.456 |
| noul_ctx+dev_prior | 88.2 [85.7, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.461 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +6.71 pts [+4.59, +8.83] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.18 pts [-0.35, +0.88] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.69 pts [+86.04, +91.34] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -29.51 pts [-33.39, -25.97] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.95 pts [-13.43, -8.48] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +20.67 pts [+17.49, +24.21] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.05 nats [-1.09, -1.00] |
