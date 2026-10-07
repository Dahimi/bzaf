# E01 readout scores — vela-2.0-4b

## goemotions (dev 133, test 267, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.0 [1.1, 5.2] | 0.205 | 0.160 | 0.090 | 8.57 (1.18) | 17.119 |
| noul_ctx+platt | 1.9 [0.4, 3.7] | 0.019 | 0.034 | 0.022 | 0.14 (1.18) | 4.368 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (1.18) | — |
| pick@top1 | 31.5 [25.8, 37.5] | 0.391 | 0.395 | 0.828 | 1.00 (1.18) | — |
| pick+true_count | 36.7 [30.7, 42.7] | 0.411 | 0.435 | 1.000 | 1.18 (1.18) | — |
| noul_ctx+true_count | 34.8 [29.2, 40.4] | 0.396 | 0.410 | 1.000 | 1.18 (1.18) | — |
| pick+count | 19.9 [15.4, 24.7] | 0.277 | 0.371 | 0.375 | 0.76 (1.18) | 4.313 |
| noul_ctx+count | 11.6 [7.9, 15.7] | 0.121 | 0.191 | 0.169 | 0.19 (1.18) | 4.979 |
| pick+dev_prior | 31.5 [25.8, 37.5] | 0.391 | 0.395 | 0.828 | 1.00 (1.18) | 2.831 |
| noul_ctx+dev_prior | 31.5 [26.2, 37.1] | 0.386 | 0.388 | 0.828 | 1.00 (1.18) | 3.497 |
| set@shipped | 18.0 [13.5, 22.5] | 0.418 | 0.396 | 0.330 | 2.19 (1.18) | 4.529 |
| set+platt | 18.4 [13.5, 22.8] | 0.213 | 0.304 | 0.307 | 0.37 (1.18) | 3.114 |
| set+true_count | 37.1 [31.1, 43.1] | 0.415 | 0.441 | 1.000 | 1.18 (1.18) | — |
| set+dev_prior | 31.5 [25.8, 37.1] | 0.386 | 0.388 | 0.828 | 1.00 (1.18) | 2.903 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -19.10 pts [-23.97, -14.61] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | -0.37 pts [-1.50, +0.75] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +13.48 pts [+8.24, +18.73] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +33.71 pts [+28.09, +39.33] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +1.87 pts [-1.12, +4.87] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +5.24 pts [+2.62, +7.87] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -16.85 pts [-21.72, -12.36] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -5.24 pts [-7.87, -2.62] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +8.61 pts [+4.12, +13.11] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -12.14 nats [-13.50, -10.89] |

## sata (dev 122, test 278, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 20.5 [16.2, 25.2] | 0.666 | 0.679 | 0.245 | 3.63 (3.58) | 4.712 |
| noul_ctx+platt | 20.1 [15.8, 24.8] | 0.665 | 0.685 | 0.252 | 3.31 (3.58) | 4.656 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (3.58) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.469 | 0.410 | 0.000 | 1.00 (3.58) | — |
| pick+true_count | 58.6 [53.2, 64.4] | 0.830 | 0.834 | 1.000 | 3.58 (3.58) | — |
| noul_ctx+true_count | 50.4 [44.6, 56.1] | 0.794 | 0.792 | 1.000 | 3.58 (3.58) | — |
| pick+count | 32.7 [27.3, 38.5] | 0.689 | 0.718 | 0.353 | 3.09 (3.58) | 3.743 |
| noul_ctx+count | 21.6 [16.9, 26.6] | 0.570 | 0.620 | 0.255 | 2.53 (3.58) | 4.435 |
| pick+dev_prior | 34.5 [29.1, 40.3] | 0.701 | 0.647 | 0.446 | 2.42 (3.58) | 3.562 |
| noul_ctx+dev_prior | 21.2 [16.5, 26.3] | 0.650 | 0.599 | 0.281 | 3.25 (3.58) | 4.254 |
| set@shipped | 31.3 [25.9, 36.7] | 0.697 | 0.694 | 0.349 | 2.50 (3.58) | 5.427 |
| set+platt | 34.2 [29.1, 39.9] | 0.764 | 0.743 | 0.374 | 3.41 (3.58) | 3.828 |
| set+true_count | 60.1 [54.7, 65.8] | 0.843 | 0.845 | 1.000 | 3.58 (3.58) | — |
| set+dev_prior | 33.5 [28.1, 38.8] | 0.705 | 0.658 | 0.446 | 2.28 (3.58) | 3.622 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -28.78 pts [-34.17, -23.38] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | -1.44 pts [-3.96, +1.08] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +2.16 pts [-2.88, +6.83] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +38.13 pts [+32.37, +43.88] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +8.27 pts [+3.24, +13.31] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +58.63 pts [+53.23, +64.39] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -25.90 pts [-31.29, -20.85] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -24.10 pts [-29.14, -19.06] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +1.08 pts [-3.24, +5.40] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.28 nats [-0.46, -0.10] |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 68.8 [62.4, 75.6] | 0.916 | 0.929 | 0.712 | 2.87 (2.79) | 1.360 |
| noul_ctx+platt | 70.7 [64.4, 77.1] | 0.920 | 0.933 | 0.727 | 2.70 (2.79) | 0.884 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.000 | 0.044 | 0.00 (2.79) | — |
| pick@top1 | 19.5 [14.1, 24.9] | 0.567 | 0.505 | 0.195 | 1.00 (2.79) | — |
| pick+true_count | 98.5 [96.6, 100.0] | 0.996 | 0.995 | 1.000 | 2.79 (2.79) | — |
| noul_ctx+true_count | 95.1 [91.7, 98.0] | 0.983 | 0.983 | 1.000 | 2.79 (2.79) | — |
| pick+count | 79.0 [73.2, 84.4] | 0.957 | 0.961 | 0.795 | 2.81 (2.79) | 1.120 |
| noul_ctx+count | 78.0 [72.2, 83.4] | 0.956 | 0.957 | 0.785 | 2.67 (2.79) | 1.305 |
| pick+dev_prior | 69.8 [63.4, 76.1] | 0.852 | 0.855 | 0.698 | 2.36 (2.79) | 1.930 |
| noul_ctx+dev_prior | 56.6 [49.8, 63.4] | 0.798 | 0.805 | 0.566 | 2.46 (2.79) | 2.116 |
| set@shipped | 66.3 [60.0, 72.7] | 0.924 | 0.917 | 0.663 | 2.40 (2.79) | 0.871 |
| set+platt | 90.2 [85.9, 94.1] | 0.971 | 0.981 | 0.902 | 2.78 (2.79) | 0.395 |
| set+true_count | 98.5 [96.6, 100.0] | 0.996 | 0.995 | 1.000 | 2.79 (2.79) | — |
| set+dev_prior | 63.9 [57.6, 70.7] | 0.858 | 0.861 | 0.639 | 2.41 (2.79) | 1.886 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -32.20 pts [-38.54, -25.85] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.00 pts [-1.46, +1.46] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | -2.44 pts [-9.27, +3.90] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +27.80 pts [+20.98, +34.15] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +3.41 pts [+0.00, +6.83] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +79.02 pts [+73.66, +84.39] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -19.51 pts [-25.37, -14.15] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -28.78 pts [-35.12, -22.44] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +9.27 pts [+2.93, +15.61] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.05 nats [-0.18, +0.07] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 70.7 [67.0, 74.4] | 0.739 | 0.154 | 0.712 | 1.39 (0.13) | 2.582 |
| noul_ctx+platt | 89.6 [87.1, 92.0] | 0.896 | 0.333 | 0.896 | 0.04 (0.13) | 0.355 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | — |
| pick@top1 | 10.2 [7.8, 12.7] | 0.108 | 0.197 | 0.110 | 1.00 (0.13) | — |
| pick+true_count | 98.9 [98.1, 99.6] | 0.991 | 0.917 | 1.000 | 0.13 (0.13) | — |
| noul_ctx+true_count | 98.8 [97.9, 99.6] | 0.991 | 0.903 | 1.000 | 0.13 (0.13) | — |
| pick+count | 74.7 [71.0, 78.3] | 0.770 | 0.458 | 0.749 | 0.38 (0.13) | 0.896 |
| noul_ctx+count | 83.7 [80.7, 86.7] | 0.849 | 0.522 | 0.841 | 0.27 (0.13) | 0.975 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.455 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.534 |
| set@shipped | 74.0 [70.1, 77.6] | 0.756 | 0.453 | 0.742 | 0.38 (0.13) | 0.736 |
| set+platt | 88.3 [85.7, 91.0] | 0.887 | 0.370 | 0.883 | 0.06 (0.13) | 0.277 |
| set+true_count | 98.8 [97.9, 99.6] | 0.990 | 0.903 | 1.000 | 0.13 (0.13) | — |
| set+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.000 | 0.882 | 0.00 (0.13) | 0.455 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -24.73 pts [-28.45, -21.38] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.18 pts [-0.35, +0.88] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +14.13 pts [+9.72, +18.73] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +9.36 pts [+6.89, +11.67] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.18 pts [-0.35, +0.71] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.69 pts [+86.04, +91.34] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.20 pts [-27.74, -20.67] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.78 pts [-13.25, -8.30] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +13.07 pts [+10.24, +15.90] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.61 nats [-1.83, -1.38] |
