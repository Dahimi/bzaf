# Benchmark v0 — base

Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).

| track | items (test) | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|
| ecthr | 217 | 12.9 / 0.132 | 38.7 / 0.447 | — | 64.5 / 0.700 |
| goemotions | 403 | 0.0 / 0.000 | 24.8 / 0.315 | — | 28.8 / 0.335 |
| nlupp | 424 | 15.1 / 0.157 | 26.7 / 0.594 | — | 53.1 / 0.757 |
| sata | 1137 | 4.2 / 0.236 | 21.2 / 0.628 | — | 36.1 / 0.737 |
| synthetic | 205 | 43.9 / 0.736 | 36.1 / 0.709 | — | 89.3 / 0.955 |
| unfair_tos | 566 | 88.7 / 0.887 | 88.2 / 0.882 | — | 97.9 / 0.981 |
| wide (probe) | 215 | 36.3 / 0.662 | 17.2 / 0.198 | — | 28.8 / 0.548 |

## General decisions (single answer, each question in its own type)

Accuracy with its 95 % CI; chance-corrected accuracy = (accuracy − chance) / (1 − chance); log-loss and calibration error of the answer's probability.

| track | items (test) | accuracy % [95% CI] | chance % | chance-corrected % | log-loss | calibration error |
|---|---|---|---|---|---|---|
| anli | 224 | 35.3 [29.5, 41.5] | 33.3 | 2.9 | 1.717 | 0.343 |
| bbh | 219 | 41.6 [35.2, 48.4] | 31.6 | 14.6 | 1.590 | 0.186 |
| boolq | 205 | 74.6 [68.8, 80.0] | 50.0 | 49.3 | 0.649 | 0.110 |
| clinc150 | 201 | 76.6 [70.6, 82.6] | 0.7 | 76.5 | 0.970 | 0.070 |
| hellaswag | 198 | 50.0 [42.9, 57.1] | 25.0 | 33.3 | 1.238 | 0.126 |
| mmlu_pro | 211 | 12.3 [8.1, 17.1] | 10.8 | 1.7 | 2.510 | 0.193 |
| sst5 | 212 | 46.7 [39.6, 53.8] | 20.0 | 33.4 | 1.262 | 0.061 |
| **mean** | | | | **30.2** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | noul_ctx@0.5 | 62 | 71.0 % | 0.943 |
| goemotions | noul_ctx+platt | 62 | 100.0 % | 1.000 |
| goemotions | pick@top1 | 62 | 83.9 % | 0.839 |
| goemotions | pick+count | 62 | 64.5 % | 0.682 |
| goemotions | pick+dev_prior | 62 | 83.9 % | 0.839 |
| nlupp | noul_ctx@0.5 | 67 | 67.2 % | 0.873 |
| nlupp | noul_ctx+platt | 67 | 100.0 % | 1.000 |
| nlupp | pick@top1 | 67 | 91.0 % | 0.910 |
| nlupp | pick+count | 67 | 91.0 % | 0.920 |
| nlupp | pick+dev_prior | 67 | 82.1 % | 0.886 |
| sata | noul_ctx@0.5 | 66 | 83.3 % | 0.942 |
| sata | noul_ctx+platt | 66 | 78.8 % | 0.850 |
| sata | pick@top1 | 66 | 77.3 % | 0.773 |
| sata | pick+count | 66 | 75.8 % | 0.857 |
| sata | pick+dev_prior | 66 | 66.7 % | 0.779 |

## Cost and quality against the number of options (wide probe)

Median seconds per item for one yes/no question per option vs the one-pass questions; example F1.

| options | items | fan-out s | one-pass s | yes/no per option, tuned | Choice + dataset count | ceiling: ranking + true count |
|---|---|---|---|---|---|---|
| 10 | 55 | 0.35 | 0.13 | 0.747 | 0.191 | 0.639 |
| 50 | 54 | 0.35 | 0.13 | 0.636 | 0.210 | 0.499 |
| 100 | 53 | 0.35 | 0.13 | 0.671 | 0.201 | 0.529 |
| 200 | 53 | 0.35 | 0.13 | 0.592 | 0.189 | 0.521 |

# Per-track details — base

## anli (dev 76, test 224, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 35.3 [29.5, 41.5] | 0.353 | 0.353 | 0.353 | 1.000 | 0.00 | 1.00 (1.00) | 1.717 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.717 | 0.343 | 0.9 % | 0.9 % | 0.621 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 41.6 [35.2, 48.4] | 0.416 | 0.416 | 0.416 | 1.000 | 0.00 | 1.00 (1.00) | 1.590 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.590 | 0.186 | 0.0 % | 0.0 % | 0.620 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 74.6 [68.8, 80.0] | 0.746 | 0.746 | 0.746 | 1.000 | 0.00 | 1.00 (1.00) | 0.649 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.649 | 0.110 | 11.2 % | 1.0 % | 0.177 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 76.6 [70.6, 82.6] | 0.766 | 0.766 | 0.766 | 1.000 | 0.00 | 1.00 (1.00) | 0.970 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.970 | 0.070 | 77.6 % | 66.7 % | 0.049 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 12.0 [7.8, 16.6] | 0.299 | 0.238 | 0.284 | 0.180 | 3.13 | 3.48 (1.09) | 6.129 |
| noul_ctx+platt | 12.9 [8.7, 17.5] | 0.132 | 0.131 | 0.025 | 0.134 | 1.07 | 0.02 (1.09) | 3.189 |
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| pick@top1 | 47.5 [40.6, 54.4] | 0.557 | 0.535 | 0.581 | 0.719 | 0.33 | 1.00 (1.09) | — |
| pick+true_count | 64.5 [57.6, 71.0] | 0.700 | 0.683 | 0.658 | 1.000 | 0.00 | 1.09 (1.09) | — |
| noul_ctx+true_count | 59.4 [53.0, 65.9] | 0.657 | 0.639 | 0.620 | 1.000 | 0.00 | 1.09 (1.09) | — |
| pick+count | 11.1 [7.4, 15.7] | 0.157 | 0.138 | 0.178 | 0.111 | 2.68 | 2.17 (1.09) | 3.259 |
| noul_ctx+count | 9.2 [5.5, 13.4] | 0.139 | 0.119 | 0.165 | 0.092 | 2.89 | 2.37 (1.09) | 3.730 |
| pick+dev_prior | 38.7 [32.7, 45.6] | 0.447 | 0.431 | 0.503 | 0.502 | 0.61 | 0.61 (1.09) | 2.271 |
| noul_ctx+dev_prior | 17.1 [12.4, 22.1] | 0.179 | 0.177 | 0.110 | 0.184 | 1.01 | 0.08 (1.09) | 2.743 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 6.129 | 0.119 | 0.0 % | 0.0 % | 0.893 |
| noul_ctx+platt | 3.189 | 0.266 | 0.0 % | 0.0 % | 0.906 |
| pick+count | 3.259 | 0.144 | 0.0 % | 0.0 % | 0.902 |
| noul_ctx+count | 3.730 | 0.128 | 0.0 % | 0.0 % | 0.911 |
| pick+dev_prior | 2.271 | 0.186 | 0.9 % | 0.9 % | 0.460 |
| noul_ctx+dev_prior | 2.743 | 0.075 | 0.9 % | 0.9 % | 0.716 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +51.61 pts [+45.16, +58.06] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +5.07 pts [+0.00, +10.60] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +17.05 pts [+12.44, +22.58] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -53.46 pts [-59.91, -46.54] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -25.81 pts [-31.34, -19.82] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -2.76 pts [-7.83, +2.30] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -2.40 nats [-2.81, -2.00] |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 0.2 [0.0, 1.0] | 0.086 | 0.047 | 0.088 | 0.025 | 21.10 | 22.19 (1.18) | 47.359 |
| noul_ctx+platt | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | 4.642 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| pick@top1 | 24.8 [20.6, 29.0] | 0.315 | 0.298 | 0.321 | 0.829 | 0.18 | 1.00 (1.18) | — |
| pick+true_count | 28.8 [24.3, 33.3] | 0.335 | 0.319 | 0.361 | 1.000 | 0.00 | 1.18 (1.18) | — |
| noul_ctx+true_count | 32.0 [27.5, 36.5] | 0.365 | 0.350 | 0.389 | 1.000 | 0.00 | 1.18 (1.18) | — |
| pick+count | 13.9 [10.7, 17.4] | 0.207 | 0.183 | 0.118 | 0.273 | 8.52 | 8.86 (1.18) | 5.215 |
| noul_ctx+count | 6.2 [4.0, 8.7] | 0.114 | 0.092 | 0.091 | 0.109 | 13.47 | 13.75 (1.18) | 5.589 |
| pick+dev_prior | 24.8 [20.6, 29.0] | 0.315 | 0.298 | 0.321 | 0.829 | 0.18 | 1.00 (1.18) | 3.167 |
| noul_ctx+dev_prior | 27.5 [23.3, 31.8] | 0.348 | 0.330 | 0.353 | 0.829 | 0.18 | 1.00 (1.18) | 3.541 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 47.359 | 0.082 | 0.0 % | 0.0 % | 0.999 |
| noul_ctx+platt | 4.642 | 0.434 | 0.0 % | 0.0 % | 1.000 |
| pick+count | 5.215 | 0.121 | 0.0 % | 0.0 % | 0.879 |
| noul_ctx+count | 5.589 | 0.066 | 0.0 % | 0.0 % | 0.967 |
| pick+dev_prior | 3.167 | 0.085 | 0.2 % | 0.2 % | 0.564 |
| noul_ctx+dev_prior | 3.541 | 0.125 | 1.0 % | 1.0 % | 0.556 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +28.54 pts [+24.32, +33.00] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -3.23 pts [-6.20, -0.50] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +3.97 pts [+2.23, +5.71] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -14.89 pts [-18.37, -11.66] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -3.97 pts [-5.71, -2.23] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +5.96 pts [+3.72, +8.44] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -41.77 nats [-44.63, -39.09] |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 50.0 [42.9, 57.1] | 0.500 | 0.500 | 0.500 | 1.000 | 0.00 | 1.00 (1.00) | 1.238 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.238 | 0.126 | 1.5 % | 1.5 % | 0.373 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 12.3 [8.1, 17.1] | 0.123 | 0.123 | 0.123 | 1.000 | 0.00 | 1.00 (1.00) | 2.510 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 2.510 | 0.193 | 0.5 % | 0.5 % | 0.789 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 4.0 [2.1, 5.9] | 0.141 | 0.097 | 0.097 | 0.050 | 34.20 | 36.08 (1.93) | 85.857 |
| noul_ctx+platt | 15.1 [11.8, 18.6] | 0.157 | 0.156 | 0.024 | 0.151 | 1.91 | 0.02 (1.93) | 7.355 |
| always_none | 13.7 [10.4, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| pick@top1 | 17.9 [14.4, 21.5] | 0.490 | 0.399 | 0.499 | 0.224 | 1.21 | 1.00 (1.93) | — |
| pick+true_count | 53.1 [48.6, 57.8] | 0.757 | 0.693 | 0.705 | 1.000 | 0.00 | 1.93 (1.93) | — |
| noul_ctx+true_count | 46.0 [41.3, 50.9] | 0.707 | 0.633 | 0.634 | 1.000 | 0.00 | 1.93 (1.93) | — |
| pick+count | 29.0 [24.5, 33.3] | 0.588 | 0.504 | 0.442 | 0.333 | 1.89 | 1.75 (1.93) | 5.313 |
| noul_ctx+count | 20.0 [16.3, 24.1] | 0.336 | 0.293 | 0.114 | 0.208 | 15.75 | 15.85 (1.93) | 7.481 |
| pick+dev_prior | 26.7 [22.6, 30.9] | 0.594 | 0.510 | 0.606 | 0.389 | 0.93 | 1.48 (1.93) | 4.159 |
| noul_ctx+dev_prior | 13.7 [10.4, 17.2] | 0.140 | 0.139 | 0.005 | 0.137 | 1.93 | 0.00 (1.93) | 6.327 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 85.857 | 0.112 | 0.0 % | 0.0 % | 0.962 |
| noul_ctx+platt | 7.355 | 0.148 | 7.1 % | 5.9 % | 0.623 |
| pick+count | 5.313 | 0.206 | 3.5 % | 1.4 % | 0.559 |
| noul_ctx+count | 7.481 | 0.137 | 3.5 % | 1.4 % | 0.600 |
| pick+dev_prior | 4.159 | 0.120 | 0.0 % | 0.0 % | 0.714 |
| noul_ctx+dev_prior | 6.327 | 0.098 | 0.0 % | 0.0 % | 0.765 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +37.97 pts [+33.49, +42.69] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +7.08 pts [+3.77, +10.61] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +35.14 pts [+30.90, +39.86] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.06 pts [-28.07, -20.28] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -26.42 pts [-30.66, -22.41] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +16.04 pts [+12.74, +19.58] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -78.38 nats [-83.76, -72.95] |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 0.6 [0.2, 1.1] | 0.553 | 0.402 | 0.563 | 0.020 | 4.86 | 7.96 (3.60) | 11.269 |
| noul_ctx+platt | 4.2 [3.1, 5.4] | 0.236 | 0.185 | 0.320 | 0.060 | 3.18 | 1.26 (3.60) | 6.000 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.426 | 0.294 | 0.384 | 0.000 | 2.60 | 1.00 (3.60) | — |
| pick+true_count | 36.1 [33.2, 38.9] | 0.737 | 0.645 | 0.750 | 1.000 | 0.00 | 3.60 (3.60) | — |
| noul_ctx+true_count | 34.7 [31.8, 37.4] | 0.735 | 0.639 | 0.744 | 1.000 | 0.00 | 3.60 (3.60) | — |
| pick+count | 6.1 [4.7, 7.5] | 0.536 | 0.411 | 0.565 | 0.067 | 4.49 | 6.78 (3.60) | 5.182 |
| noul_ctx+count | 1.6 [0.9, 2.3] | 0.489 | 0.357 | 0.534 | 0.016 | 5.19 | 7.55 (3.60) | 5.909 |
| pick+dev_prior | 21.2 [18.9, 23.6] | 0.628 | 0.515 | 0.595 | 0.386 | 1.66 | 2.17 (3.60) | 4.490 |
| noul_ctx+dev_prior | 9.4 [7.7, 11.1] | 0.583 | 0.445 | 0.554 | 0.126 | 3.13 | 4.01 (3.60) | 5.217 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 11.269 | 0.368 | 0.0 % | 0.0 % | 0.998 |
| noul_ctx+platt | 6.000 | 0.060 | 0.0 % | 0.0 % | 0.963 |
| pick+count | 5.182 | 0.101 | 0.0 % | 0.0 % | 0.909 |
| noul_ctx+count | 5.909 | 0.128 | 0.0 % | 0.0 % | 0.983 |
| pick+dev_prior | 4.490 | 0.079 | 4.7 % | 3.8 % | 0.578 |
| noul_ctx+dev_prior | 5.217 | 0.073 | 0.6 % | 0.6 % | 0.771 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 0.6 | 40.2 | +4.35 | 4.86 | 2.8 | 36 |
| noul_ctx+platt | 10.7 | 18.5 | -2.34 | 3.18 | 9.5 | 690 |
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| pick@top1 | 0.0 | 29.4 | -2.60 | 2.60 | 6.8 | 0 |
| pick+true_count | 36.1 | 64.5 | +0.00 | 0.00 | 7.5 | 0 |
| noul_ctx+true_count | 34.7 | 63.9 | +0.00 | 0.00 | 6.1 | 0 |
| pick+count | 6.9 | 41.1 | +3.18 | 4.49 | 4.5 | 136 |
| noul_ctx+count | 1.9 | 35.7 | +3.95 | 5.19 | 3.2 | 168 |
| pick+dev_prior | 21.2 | 51.5 | -1.44 | 1.66 | 12.8 | 0 |
| noul_ctx+dev_prior | 9.4 | 44.5 | +0.41 | 3.13 | 18.9 | 0 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +31.84 pts [+29.11, +34.56] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +1.41 pts [-0.88, +3.61] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +36.06 pts [+33.25, +38.87] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -29.99 pts [-32.63, -27.44] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -14.86 pts [-16.97, -12.84] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +0.97 pts [+0.18, +1.85] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -5.36 nats [-5.71, -5.04] |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 46.7 [39.6, 53.8] | 0.467 | 0.467 | 0.467 | 1.000 | 0.00 | 1.00 (1.00) | 1.262 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.262 | 0.061 | 0.0 % | 0.0 % | 0.462 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 43.9 [37.1, 50.7] | 0.772 | 0.714 | 0.822 | 0.439 | 1.04 | 3.12 (2.79) | 2.436 |
| noul_ctx+platt | 43.9 [37.1, 50.2] | 0.736 | 0.687 | 0.828 | 0.449 | 0.89 | 2.50 (2.79) | 2.165 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| pick@top1 | 18.0 [12.7, 22.9] | 0.549 | 0.432 | 0.494 | 0.195 | 1.88 | 1.00 (2.79) | — |
| pick+true_count | 89.3 [84.9, 93.7] | 0.955 | 0.941 | 0.962 | 1.000 | 0.00 | 2.79 (2.79) | — |
| noul_ctx+true_count | 95.1 [91.7, 98.0] | 0.988 | 0.981 | 0.983 | 1.000 | 0.00 | 2.79 (2.79) | — |
| pick+count | 35.6 [29.3, 42.0] | 0.743 | 0.668 | 0.801 | 0.356 | 1.01 | 2.38 (2.79) | 2.062 |
| noul_ctx+count | 34.6 [28.3, 41.0] | 0.756 | 0.678 | 0.805 | 0.346 | 1.00 | 2.41 (2.79) | 1.943 |
| pick+dev_prior | 36.1 [29.8, 42.9] | 0.709 | 0.623 | 0.713 | 0.371 | 1.35 | 2.00 (2.79) | 2.306 |
| noul_ctx+dev_prior | 46.3 [39.5, 53.2] | 0.788 | 0.720 | 0.796 | 0.463 | 1.02 | 2.23 (2.79) | 2.187 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 2.436 | 0.178 | 2.9 % | 2.9 % | 0.462 |
| noul_ctx+platt | 2.165 | 0.213 | 5.4 % | 2.4 % | 0.487 |
| pick+count | 2.062 | 0.135 | 4.9 % | 4.4 % | 0.543 |
| noul_ctx+count | 1.943 | 0.134 | 4.9 % | 4.4 % | 0.536 |
| pick+dev_prior | 2.306 | 0.172 | 0.5 % | 0.5 % | 0.565 |
| noul_ctx+dev_prior | 2.187 | 0.280 | 0.0 % | 0.0 % | 0.404 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +45.37 pts [+37.56, +53.17] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -5.85 pts [-11.22, -0.49] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +71.22 pts [+64.88, +77.56] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -53.66 pts [-60.49, -46.83] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -53.17 pts [-59.51, -46.34] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -9.27 pts [-17.09, -1.46] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.49 nats [-0.79, -0.22] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 38.0 [33.9, 42.0] | 0.407 | 0.396 | 0.062 | 0.380 | 3.77 | 3.89 (0.13) | 7.697 |
| noul_ctx+platt | 88.7 [86.0, 91.2] | 0.887 | 0.887 | 0.127 | 0.887 | 0.12 | 0.01 (0.13) | 0.462 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| pick@top1 | 9.2 [6.7, 11.5] | 0.097 | 0.095 | 0.176 | 0.110 | 0.89 | 1.00 (0.13) | — |
| pick+true_count | 97.9 [96.6, 98.9] | 0.981 | 0.980 | 0.833 | 1.000 | 0.00 | 0.13 (0.13) | — |
| noul_ctx+true_count | 97.5 [96.1, 98.6] | 0.977 | 0.976 | 0.806 | 1.000 | 0.00 | 0.13 (0.13) | — |
| pick+count | 58.8 [54.9, 62.9] | 0.612 | 0.602 | 0.080 | 0.588 | 2.62 | 2.72 (0.13) | 2.252 |
| noul_ctx+count | 59.7 [55.8, 63.8] | 0.622 | 0.611 | 0.075 | 0.597 | 2.78 | 2.88 (0.13) | 2.292 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.533 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.573 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 7.697 | 0.297 | 0.0 % | 0.0 % | 0.595 |
| noul_ctx+platt | 0.462 | 0.032 | 96.8 % | 83.9 % | 0.027 |
| pick+count | 2.252 | 0.352 | 51.8 % | 44.3 % | 0.141 |
| noul_ctx+count | 2.292 | 0.362 | 52.5 % | 45.1 % | 0.136 |
| pick+dev_prior | 0.533 | 0.046 | 48.2 % | 0.7 % | 0.103 |
| noul_ctx+dev_prior | 0.573 | 0.046 | 48.2 % | 0.7 % | 0.103 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +9.19 pts [+6.89, +11.48] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.35 pts [+0.00, +0.88] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.69 pts [+86.04, +91.34] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -39.05 pts [-42.93, -34.98] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -9.72 pts [-12.01, -7.24] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +21.73 pts [+18.37, +25.44] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -5.41 nats [-5.88, -4.94] |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul@0.5 | 35.8 [29.3, 41.9] | 0.683 | 0.601 | 0.626 | 0.419 | 1.35 | 2.36 (2.44) | 9.291 |
| noul+platt | 36.3 [29.8, 42.8] | 0.662 | 0.585 | 0.624 | 0.419 | 1.18 | 1.89 (2.44) | 5.005 |
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| pick@top1 | 16.7 [12.1, 21.9] | 0.416 | 0.339 | 0.384 | 0.237 | 1.58 | 1.00 (2.44) | — |
| pick+true_count | 28.8 [23.3, 34.9] | 0.548 | 0.464 | 0.472 | 1.000 | 0.00 | 2.44 (2.44) | — |
| noul+true_count | 67.4 [61.4, 74.0] | 0.865 | 0.818 | 0.829 | 1.000 | 0.00 | 2.44 (2.44) | — |
| pick+count | 15.3 [10.7, 20.5] | 0.281 | 0.245 | 0.172 | 0.195 | 3.68 | 2.15 (2.44) | 8.643 |
| noul+count | 32.6 [26.5, 39.5] | 0.478 | 0.435 | 0.311 | 0.340 | 3.09 | 2.11 (2.44) | 4.952 |
| pick+dev_prior | 17.2 [12.1, 22.8] | 0.198 | 0.191 | 0.124 | 0.177 | 2.30 | 0.19 (2.44) | 8.360 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul@0.5 | 9.291 | 0.256 | 1.4 % | 1.4 % | 0.521 |
| noul+platt | 5.005 | 0.196 | 1.4 % | 1.4 % | 0.498 |
| pick+count | 8.643 | 0.109 | 0.9 % | 0.9 % | 0.794 |
| noul+count | 4.952 | 0.181 | 5.6 % | 1.9 % | 0.565 |
| pick+dev_prior | 8.360 | 0.120 | 1.4 % | 1.4 % | 0.721 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul+platt | -7.44 pts [-13.49, -0.93] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +12.09 pts [+7.91, +16.28] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -13.49 pts [-18.14, -9.30] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -11.63 pts [-15.81, -7.44] |
