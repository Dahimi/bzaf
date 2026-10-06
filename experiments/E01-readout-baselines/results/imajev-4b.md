# E01 readout scores — imajev-4b

## goemotions (dev 133, test 267, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 0.7 [0.0, 1.9] | 0.287 | 0.262 | 0.015 | 6.55 (1.18) | 13.268 |
| noul+platt | 12.0 [8.2, 16.1] | 0.139 | 0.218 | 0.169 | 0.23 (1.18) | 3.523 |
| noul_ctx@0.5 | 3.4 [1.5, 5.6] | 0.325 | 0.276 | 0.041 | 5.59 (1.18) | 11.774 |
| noul_ctx+platt | 9.4 [6.0, 13.1] | 0.124 | 0.204 | 0.176 | 0.25 (1.18) | 3.502 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (1.18) | — |
| pick@top1 | 27.7 [22.5, 33.0] | 0.331 | 0.330 | 0.828 | 1.00 (1.18) | — |
| pick+true_count | 32.6 [27.0, 37.8] | 0.365 | 0.387 | 1.000 | 1.18 (1.18) | — |
| noul+true_count | 28.8 [23.6, 34.5] | 0.341 | 0.362 | 1.000 | 1.18 (1.18) | — |
| noul_ctx+true_count | 30.3 [24.7, 36.0] | 0.343 | 0.365 | 1.000 | 1.18 (1.18) | — |
| pick+count | 18.4 [13.9, 22.8] | 0.346 | 0.360 | 0.431 | 1.57 (1.18) | 4.196 |
| noul+count | 12.7 [8.6, 16.5] | 0.300 | 0.332 | 0.378 | 1.53 (1.18) | 4.350 |
| noul_ctx+count | 16.9 [12.4, 21.3] | 0.334 | 0.358 | 0.382 | 1.61 (1.18) | 4.416 |
| pick+dev_prior | 27.7 [22.5, 33.0] | 0.331 | 0.330 | 0.828 | 1.00 (1.18) | 2.997 |
| noul_ctx+dev_prior | 25.8 [20.6, 30.7] | 0.323 | 0.326 | 0.828 | 1.00 (1.18) | 3.217 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul+platt | +20.60 pts [+15.73, +25.84] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +2.25 pts [-1.50, +6.37] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +4.87 pts [+2.62, +7.49] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -14.23 pts [-18.73, -10.11] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -4.87 pts [-7.49, -2.62] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +13.48 pts [+9.73, +17.60] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +2.62 pts [+0.37, +4.87] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -7.36 nats [-7.93, -6.81] |

## sata (dev 122, test 278, failed 10)

> **WARNING: 10 items failed (2 %)** and count as wrong. First error: `HTTP 422: b'{"error":"invalid_request","detail":"fields.6.choice.options.1.value: String should have at most 128 characters"}'`. Re-run the readout to retry them.

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 33.1 [27.7, 38.5] | 0.748 | 0.764 | 0.388 | 3.20 (3.58) | 3.677 |
| noul+platt | 33.1 [27.7, 38.5] | 0.752 | 0.769 | 0.378 | 3.34 (3.58) | 3.576 |
| noul_ctx@0.5 | 30.2 [24.8, 35.6] | 0.736 | 0.752 | 0.363 | 2.96 (3.58) | 3.839 |
| noul_ctx+platt | 32.0 [26.6, 37.4] | 0.758 | 0.769 | 0.385 | 3.35 (3.58) | 3.503 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (3.58) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.461 | 0.406 | 0.000 | 1.00 (3.58) | — |
| pick+true_count | 51.1 [45.7, 56.8] | 0.809 | 0.827 | 0.971 | 3.60 (3.58) | — |
| noul+true_count | 56.8 [51.1, 62.6] | 0.821 | 0.831 | 0.971 | 3.60 (3.58) | — |
| noul_ctx+true_count | 55.4 [49.6, 61.2] | 0.808 | 0.823 | 0.971 | 3.60 (3.58) | — |
| pick+count | 15.5 [11.5, 20.1] | 0.613 | 0.643 | 0.191 | 2.09 (3.58) | 4.147 |
| noul+count | 22.3 [17.6, 27.3] | 0.644 | 0.687 | 0.255 | 2.33 (3.58) | 3.782 |
| noul_ctx+count | 22.3 [17.6, 27.3] | 0.651 | 0.701 | 0.252 | 2.38 (3.58) | 3.849 |
| pick+dev_prior | 29.5 [24.5, 35.3] | 0.682 | 0.635 | 0.403 | 2.12 (3.58) | 3.833 |
| noul_ctx+dev_prior | 33.1 [28.1, 38.8] | 0.716 | 0.691 | 0.421 | 2.52 (3.58) | 3.535 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul@0.5 | +17.99 pts [+12.59, +23.38] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -4.32 pts [-8.63, +0.01] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +51.08 pts [+45.68, +56.83] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -35.61 pts [-41.37, -29.86] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -21.58 pts [-26.26, -16.91] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -7.91 pts [-12.23, -3.60] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | -2.88 pts [-7.19, +1.80] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.01 nats [-0.21, +0.20] |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 70.7 [63.9, 76.6] | 0.928 | 0.935 | 0.712 | 2.53 (2.79) | 0.554 |
| noul+platt | 91.2 [87.3, 94.6] | 0.986 | 0.983 | 0.917 | 2.80 (2.79) | 0.287 |
| noul_ctx@0.5 | 88.8 [84.4, 92.7] | 0.979 | 0.978 | 0.893 | 2.68 (2.79) | 0.473 |
| noul_ctx+platt | 92.2 [88.3, 95.6] | 0.987 | 0.985 | 0.927 | 2.76 (2.79) | 0.165 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.000 | 0.044 | 0.00 (2.79) | — |
| pick@top1 | 19.5 [14.1, 24.9] | 0.567 | 0.505 | 0.195 | 1.00 (2.79) | — |
| pick+true_count | 96.1 [93.2, 98.5] | 0.993 | 0.986 | 1.000 | 2.79 (2.79) | — |
| noul+true_count | 98.5 [96.6, 100.0] | 0.997 | 0.995 | 1.000 | 2.79 (2.79) | — |
| noul_ctx+true_count | 99.5 [98.5, 100.0] | 0.998 | 0.998 | 1.000 | 2.79 (2.79) | — |
| pick+count | 75.1 [68.8, 80.5] | 0.945 | 0.944 | 0.771 | 2.61 (2.79) | 1.191 |
| noul+count | 77.1 [71.2, 82.4] | 0.949 | 0.950 | 0.771 | 2.63 (2.79) | 0.837 |
| noul_ctx+count | 79.0 [73.7, 84.4] | 0.954 | 0.958 | 0.790 | 2.65 (2.79) | 0.826 |
| pick+dev_prior | 52.2 [45.4, 59.0] | 0.754 | 0.736 | 0.522 | 1.83 (2.79) | 2.229 |
| noul_ctx+dev_prior | 71.2 [64.4, 77.1] | 0.874 | 0.873 | 0.712 | 2.39 (2.79) | 1.863 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +3.90 pts [-0.49, +8.29] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -3.41 pts [-6.34, -0.98] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +76.59 pts [+70.73, +82.44] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -20.98 pts [-26.34, -15.61] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -43.90 pts [-50.74, -37.07] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -9.76 pts [-15.12, -4.39] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +18.05 pts [+12.20, +24.39] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.35 nats [+0.29, +0.42] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 66.6 [62.7, 70.5] | 0.693 | 0.374 | 0.668 | 0.52 (0.13) | 1.520 |
| noul+platt | 89.6 [87.1, 92.2] | 0.900 | 0.500 | 0.899 | 0.09 (0.13) | 0.271 |
| noul_ctx@0.5 | 69.1 [65.4, 72.8] | 0.705 | 0.414 | 0.691 | 0.46 (0.13) | 1.356 |
| noul_ctx+platt | 93.5 [91.5, 95.4] | 0.939 | 0.702 | 0.936 | 0.10 (0.13) | 0.243 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [7.8, 12.9] | 0.109 | 0.197 | 0.110 | 1.00 (0.13) | — |
| pick+true_count | 99.1 [98.4, 99.8] | 0.993 | 0.931 | 1.000 | 0.13 (0.13) | — |
| noul+true_count | 98.6 [97.5, 99.5] | 0.989 | 0.889 | 1.000 | 0.13 (0.13) | — |
| noul_ctx+true_count | 98.9 [98.1, 99.6] | 0.992 | 0.917 | 1.000 | 0.13 (0.13) | — |
| pick+count | 71.6 [67.7, 75.3] | 0.733 | 0.444 | 0.721 | 0.41 (0.13) | 0.940 |
| noul+count | 73.0 [69.1, 76.7] | 0.747 | 0.455 | 0.735 | 0.40 (0.13) | 0.940 |
| noul_ctx+count | 72.8 [69.1, 76.5] | 0.746 | 0.453 | 0.733 | 0.40 (0.13) | 0.936 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.455 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.450 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +5.65 pts [+3.89, +7.60] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.18 pts [-0.35, +0.71] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.69 pts [+86.04, +91.34] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -27.56 pts [-31.28, -23.85] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.95 pts [-13.43, -8.30] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +3.71 pts [+1.41, +6.01] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +2.47 pts [-0.18, +5.12] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.42 nats [-0.51, -0.34] |
