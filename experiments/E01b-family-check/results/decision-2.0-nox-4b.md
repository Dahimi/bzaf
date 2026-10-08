# Benchmark v0 — decision-2.0-nox-4b

Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).

| track | items (test) | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|
| ecthr | 217 | 35.9 / 0.472 | 50.7 / 0.570 | — | 77.4 / 0.815 |
| goemotions | 403 | 17.1 / 0.217 | 35.5 / 0.420 | — | 39.2 / 0.440 |
| nlupp | 424 | 35.8 / 0.695 | 35.4 / 0.660 | — | 62.3 / 0.824 |
| sata | 1137 | 29.8 / 0.767 | 29.6 / 0.676 | — | 54.4 / 0.816 |
| synthetic | 205 | 94.6 / 0.982 | 70.2 / 0.840 | — | 95.6 / 0.985 |
| unfair_tos | 566 | 92.4 / 0.926 | 88.2 / 0.882 | — | 99.1 / 0.993 |
| wide (probe) | 215 | 99.1 / 0.999 | 53.5 / 0.587 | — | 97.7 / 0.991 |

## General decisions (single answer, each question in its own type)

Accuracy with its 95 % CI; chance-corrected accuracy = (accuracy − chance) / (1 − chance); log-loss and calibration error of the answer's probability.

| track | items (test) | accuracy % [95% CI] | chance % | chance-corrected % | log-loss | calibration error |
|---|---|---|---|---|---|---|
| anli | 224 | 63.8 [57.6, 69.6] | 33.3 | 45.8 | 0.894 | 0.107 |
| bbh | 219 | 67.6 [61.2, 73.5] | 31.6 | 52.6 | 0.787 | 0.068 |
| boolq | 205 | 86.8 [82.4, 91.2] | 50.0 | 73.7 | 0.308 | 0.049 |
| clinc150 | 201 | 87.6 [82.6, 92.0] | 0.7 | 87.5 | 0.693 | 0.170 |
| hellaswag | 198 | 85.9 [80.8, 90.4] | 25.0 | 81.1 | 0.433 | 0.120 |
| mmlu_pro | 211 | 55.0 [47.9, 61.6] | 10.8 | 49.5 | 1.440 | 0.127 |
| sst5 | 212 | 56.6 [49.5, 63.2] | 20.0 | 45.8 | 1.072 | 0.123 |
| **mean** | | | | **62.3** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | noul_ctx@0.5 | 62 | 67.7 % | 0.886 |
| goemotions | noul_ctx+platt | 62 | 82.3 % | 0.839 |
| goemotions | pick@top1 | 62 | 87.1 % | 0.871 |
| goemotions | pick+count | 62 | 91.9 % | 0.944 |
| goemotions | pick+dev_prior | 62 | 87.1 % | 0.871 |
| nlupp | noul_ctx@0.5 | 1 | 0.0 % | 0.600 |
| nlupp | noul_ctx+platt | 1 | 100.0 % | 1.000 |
| nlupp | pick@top1 | 1 | 100.0 % | 1.000 |
| nlupp | pick+count | 1 | 100.0 % | 1.000 |
| nlupp | pick+dev_prior | 1 | 0.0 % | 0.000 |
| sata | noul_ctx@0.5 | 66 | 72.7 % | 0.898 |
| sata | noul_ctx+platt | 66 | 77.3 % | 0.923 |
| sata | pick@top1 | 66 | 84.8 % | 0.848 |
| sata | pick+count | 66 | 75.8 % | 0.881 |
| sata | pick+dev_prior | 66 | 80.3 % | 0.875 |

## Cost and quality against the number of options (wide probe)

Median seconds per item for one yes/no question per option vs the one-pass questions; example F1.

| options | items | fan-out s | one-pass s | yes/no per option, tuned | Choice + dataset count | ceiling: ranking + true count |
|---|---|---|---|---|---|---|
| 10 | 55 | 2.87 | 2.31 | 1.000 | 0.818 | 1.000 |
| 50 | 54 | 15.86 | 8.08 | 1.000 | 0.712 | 1.000 |
| 100 | 53 | 31.85 | 12.59 | 1.000 | 0.503 | 1.000 |
| 200 | 53 | 68.98 | 28.98 | 0.996 | 0.303 | 0.962 |

# Per-track details — decision-2.0-nox-4b

## anli (dev 76, test 224, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 63.8 [57.6, 69.6] | 0.638 | 0.638 | 0.638 | 1.000 | 0.00 | 1.00 (1.00) | 0.894 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.894 | 0.107 | 0.9 % | 0.9 % | 0.284 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 67.6 [61.2, 73.5] | 0.676 | 0.676 | 0.676 | 1.000 | 0.00 | 1.00 (1.00) | 0.787 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.787 | 0.068 | 43.4 % | 21.9 % | 0.135 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 86.8 [82.4, 91.2] | 0.868 | 0.868 | 0.868 | 1.000 | 0.00 | 1.00 (1.00) | 0.308 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.308 | 0.049 | 94.6 % | 62.4 % | 0.048 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 87.6 [82.6, 92.0] | 0.876 | 0.876 | 0.876 | 1.000 | 0.00 | 1.00 (1.00) | 0.693 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.693 | 0.170 | 87.6 % | 76.6 % | 0.025 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 34.6 [28.1, 41.0] | 0.556 | 0.500 | 0.610 | 0.392 | 0.76 | 1.20 (1.09) | 3.202 |
| noul_ctx+platt | 35.9 [29.5, 41.9] | 0.472 | 0.442 | 0.536 | 0.406 | 0.71 | 0.71 (1.09) | 2.016 |
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| pick@top1 | 57.6 [50.7, 64.5] | 0.658 | 0.636 | 0.678 | 0.719 | 0.33 | 1.00 (1.09) | — |
| pick+true_count | 77.4 [71.4, 82.9] | 0.815 | 0.801 | 0.785 | 1.000 | 0.00 | 1.09 (1.09) | — |
| noul_ctx+true_count | 77.0 [71.0, 82.5] | 0.796 | 0.787 | 0.772 | 1.000 | 0.00 | 1.09 (1.09) | — |
| pick+count | 19.8 [14.7, 25.3] | 0.278 | 0.258 | 0.346 | 0.203 | 0.99 | 0.48 (1.09) | 2.686 |
| noul_ctx+count | 19.8 [14.7, 25.3] | 0.251 | 0.238 | 0.295 | 0.203 | 0.99 | 0.35 (1.09) | 2.969 |
| pick+dev_prior | 50.7 [44.2, 57.1] | 0.570 | 0.553 | 0.623 | 0.585 | 0.52 | 0.74 (1.09) | 1.970 |
| noul_ctx+dev_prior | 36.4 [30.0, 42.4] | 0.396 | 0.388 | 0.442 | 0.406 | 0.75 | 0.43 (1.09) | 2.252 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.202 | 0.271 | 0.0 % | 0.0 % | 0.634 |
| noul_ctx+platt | 2.016 | 0.167 | 0.0 % | 0.0 % | 0.651 |
| pick+count | 2.686 | 0.103 | 0.9 % | 0.9 % | 0.751 |
| noul_ctx+count | 2.969 | 0.096 | 0.9 % | 0.9 % | 0.770 |
| pick+dev_prior | 1.970 | 0.282 | 0.5 % | 0.5 % | 0.355 |
| noul_ctx+dev_prior | 2.252 | 0.198 | 0.9 % | 0.9 % | 0.445 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +41.47 pts [+34.56, +48.39] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.46 pts [-4.15, +4.61] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +19.82 pts [+14.75, +25.35] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -57.60 pts [-64.06, -50.69] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -26.73 pts [-32.72, -20.74] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -14.75 pts [-21.20, -7.83] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.23 nats [-0.32, -0.15] |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 5.2 [3.2, 7.4] | 0.363 | 0.264 | 0.340 | 0.089 | 2.27 | 3.43 (1.18) | 9.229 |
| noul_ctx+platt | 17.1 [13.4, 20.8] | 0.217 | 0.205 | 0.308 | 0.270 | 0.83 | 0.41 (1.18) | 3.371 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| pick@top1 | 35.5 [31.0, 40.2] | 0.420 | 0.403 | 0.416 | 0.829 | 0.18 | 1.00 (1.18) | — |
| pick+true_count | 39.2 [34.5, 44.2] | 0.440 | 0.424 | 0.450 | 1.000 | 0.00 | 1.18 (1.18) | — |
| noul_ctx+true_count | 37.0 [32.5, 41.7] | 0.413 | 0.399 | 0.422 | 1.000 | 0.00 | 1.18 (1.18) | — |
| pick+count | 12.4 [9.2, 15.9] | 0.249 | 0.217 | 0.359 | 0.218 | 0.88 | 0.77 (1.18) | 4.173 |
| noul_ctx+count | 13.4 [10.2, 16.6] | 0.218 | 0.196 | 0.334 | 0.216 | 0.90 | 0.59 (1.18) | 4.413 |
| pick+dev_prior | 35.5 [31.0, 40.2] | 0.420 | 0.403 | 0.416 | 0.829 | 0.18 | 1.00 (1.18) | 2.777 |
| noul_ctx+dev_prior | 33.3 [28.8, 37.7] | 0.397 | 0.380 | 0.394 | 0.829 | 0.18 | 1.00 (1.18) | 3.017 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 9.229 | 0.051 | 0.0 % | 0.0 % | 0.904 |
| noul_ctx+platt | 3.371 | 0.228 | 4.0 % | 3.5 % | 0.711 |
| pick+count | 4.173 | 0.042 | 1.5 % | 1.5 % | 0.753 |
| noul_ctx+count | 4.413 | 0.058 | 2.7 % | 2.5 % | 0.744 |
| pick+dev_prior | 2.777 | 0.069 | 2.7 % | 1.7 % | 0.499 |
| noul_ctx+dev_prior | 3.017 | 0.104 | 7.9 % | 2.7 % | 0.505 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +22.08 pts [+18.11, +26.05] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +2.23 pts [-0.50, +4.96] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +3.72 pts [+1.99, +5.71] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -26.80 pts [-31.02, -22.83] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -3.72 pts [-5.71, -1.99] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +8.19 pts [+4.96, +11.41] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -4.82 nats [-4.93, -4.71] |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 85.9 [80.8, 90.4] | 0.859 | 0.859 | 0.859 | 1.000 | 0.00 | 1.00 (1.00) | 0.433 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.433 | 0.120 | 89.4 % | 78.3 % | 0.032 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 55.0 [47.9, 61.6] | 0.550 | 0.550 | 0.550 | 1.000 | 0.00 | 1.00 (1.00) | 1.440 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.440 | 0.127 | 29.9 % | 10.9 % | 0.247 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 7.8 [5.2, 10.4] | 0.548 | 0.431 | 0.573 | 0.125 | 2.17 | 4.03 (1.93) | 12.187 |
| noul_ctx+platt | 35.8 [31.4, 40.3] | 0.695 | 0.615 | 0.692 | 0.443 | 0.73 | 1.63 (1.93) | 3.062 |
| always_none | 13.7 [10.4, 17.0] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| pick@top1 | 19.3 [15.6, 23.1] | 0.534 | 0.436 | 0.539 | 0.224 | 1.21 | 1.00 (1.93) | — |
| pick+true_count | 62.3 [57.8, 66.7] | 0.824 | 0.769 | 0.775 | 1.000 | 0.00 | 1.93 (1.93) | — |
| noul_ctx+true_count | 59.2 [54.5, 63.7] | 0.802 | 0.744 | 0.753 | 1.000 | 0.00 | 1.93 (1.93) | — |
| pick+count | 38.2 [33.7, 42.7] | 0.692 | 0.617 | 0.685 | 0.446 | 0.77 | 1.34 (1.93) | 3.245 |
| noul_ctx+count | 33.7 [29.5, 38.2] | 0.594 | 0.531 | 0.558 | 0.377 | 1.10 | 0.88 (1.93) | 4.199 |
| pick+dev_prior | 35.4 [31.4, 39.6] | 0.660 | 0.586 | 0.661 | 0.425 | 0.87 | 1.36 (1.93) | 3.443 |
| noul_ctx+dev_prior | 27.1 [22.9, 31.4] | 0.409 | 0.373 | 0.347 | 0.274 | 1.53 | 0.43 (1.93) | 4.397 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 12.187 | 0.077 | 0.2 % | 0.2 % | 0.834 |
| noul_ctx+platt | 3.062 | 0.051 | 2.6 % | 1.2 % | 0.477 |
| pick+count | 3.245 | 0.197 | 3.3 % | 1.7 % | 0.450 |
| noul_ctx+count | 4.199 | 0.213 | 3.1 % | 2.1 % | 0.443 |
| pick+dev_prior | 3.443 | 0.235 | 0.5 % | 0.5 % | 0.592 |
| noul_ctx+dev_prior | 4.397 | 0.200 | 0.0 % | 0.0 % | 0.581 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +26.42 pts [+21.93, +30.90] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +3.07 pts [-0.24, +6.37] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +42.92 pts [+38.21, +47.88] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.06 pts [-28.07, -20.05] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -26.89 pts [-31.13, -22.88] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +25.94 pts [+20.99, +30.66] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -7.99 nats [-8.34, -7.67] |

## sata (dev 513, test 1137, failed 4)

> **4 items failed (0 %)** and count as wrong. First error: `HTTP 500: b'{"error":{"code":"internal_error","message":"OutOfMemoryError: CUDA out of memory. Tried to allocate 876.00 MiB. GPU 0 has a total capacity of 44.42 GiB of which 24.12 MiB is free. Process 1 has 44.39 GiB memory in use. Of the allocated memory 38.39 GiB is allocated by PyTorch, with 1.80`. Re-run the readout to retry them.

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 27.5 [25.1, 30.1] | 0.732 | 0.636 | 0.747 | 0.342 | 1.28 | 2.98 (3.60) | 3.658 |
| noul_ctx+platt | 29.8 [27.0, 32.4] | 0.767 | 0.672 | 0.775 | 0.369 | 1.15 | 3.54 (3.60) | 3.550 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.454 | 0.314 | 0.403 | 0.000 | 2.61 | 1.00 (3.60) | — |
| pick+true_count | 54.4 [51.5, 57.1] | 0.816 | 0.750 | 0.828 | 0.997 | 0.01 | 3.60 (3.60) | — |
| noul_ctx+true_count | 53.8 [50.9, 56.6] | 0.823 | 0.754 | 0.831 | 0.997 | 0.01 | 3.60 (3.60) | — |
| pick+count | 29.8 [27.2, 32.5] | 0.629 | 0.561 | 0.697 | 0.330 | 1.70 | 2.49 (3.60) | 3.647 |
| noul_ctx+count | 25.8 [23.1, 28.4] | 0.569 | 0.506 | 0.650 | 0.287 | 1.95 | 2.26 (3.60) | 3.816 |
| pick+dev_prior | 29.6 [26.9, 32.3] | 0.676 | 0.572 | 0.636 | 0.423 | 1.57 | 2.11 (3.60) | 3.574 |
| noul_ctx+dev_prior | 26.8 [24.4, 29.5] | 0.675 | 0.566 | 0.631 | 0.385 | 1.67 | 2.19 (3.60) | 3.742 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.658 | 0.109 | 0.0 % | 0.0 % | 0.543 |
| noul_ctx+platt | 3.550 | 0.056 | 0.0 % | 0.0 % | 0.518 |
| pick+count | 3.647 | 0.071 | 0.0 % | 0.0 % | 0.536 |
| noul_ctx+count | 3.816 | 0.072 | 0.0 % | 0.0 % | 0.606 |
| pick+dev_prior | 3.574 | 0.149 | 17.7 % | 7.5 % | 0.410 |
| noul_ctx+dev_prior | 3.742 | 0.134 | 2.2 % | 2.1 % | 0.488 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 28.5 | 63.6 | -0.63 | 1.28 | 8.0 | 38 |
| noul_ctx+platt | 30.5 | 67.2 | -0.07 | 1.15 | 6.9 | 25 |
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| pick@top1 | 0.0 | 31.4 | -2.61 | 2.61 | 7.6 | 3 |
| pick+true_count | 54.5 | 75.0 | -0.01 | 0.01 | 5.0 | 3 |
| noul_ctx+true_count | 54.0 | 75.4 | -0.01 | 0.01 | 4.5 | 3 |
| pick+count | 37.9 | 56.1 | -1.12 | 1.70 | 6.5 | 242 |
| noul_ctx+count | 36.1 | 50.6 | -1.35 | 1.95 | 8.3 | 326 |
| pick+dev_prior | 29.6 | 57.2 | -1.50 | 1.57 | 11.1 | 3 |
| noul_ctx+dev_prior | 26.9 | 56.6 | -1.42 | 1.67 | 14.1 | 3 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +24.54 pts [+22.08, +27.18] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.53 pts [-1.32, +2.29] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +54.35 pts [+51.45, +57.08] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.54 pts [-27.09, -22.08] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -24.80 pts [-27.26, -22.43] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -1.76 pts [-4.05, +0.53] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.16 nats [+0.11, +0.20] |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 56.6 [49.5, 63.2] | 0.566 | 0.566 | 0.566 | 1.000 | 0.00 | 1.00 (1.00) | 1.072 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.072 | 0.123 | 1.9 % | 1.9 % | 0.373 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 94.6 [91.2, 97.6] | 0.982 | 0.977 | 0.990 | 0.946 | 0.05 | 2.81 (2.79) | 0.455 |
| noul_ctx+platt | 94.6 [91.2, 97.6] | 0.982 | 0.977 | 0.990 | 0.946 | 0.05 | 2.81 (2.79) | 0.213 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| pick@top1 | 19.0 [13.7, 24.4] | 0.557 | 0.440 | 0.497 | 0.195 | 1.88 | 1.00 (2.79) | — |
| pick+true_count | 95.6 [92.7, 98.0] | 0.985 | 0.980 | 0.984 | 1.000 | 0.00 | 2.79 (2.79) | — |
| noul_ctx+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.79 (2.79) | — |
| pick+count | 84.4 [79.5, 89.3] | 0.967 | 0.951 | 0.969 | 0.844 | 0.16 | 2.92 (2.79) | 0.896 |
| noul_ctx+count | 87.8 [82.9, 92.2] | 0.974 | 0.962 | 0.978 | 0.878 | 0.12 | 2.87 (2.79) | 0.695 |
| pick+dev_prior | 70.2 [63.4, 76.6] | 0.840 | 0.808 | 0.846 | 0.707 | 0.79 | 2.40 (2.79) | 2.066 |
| noul_ctx+dev_prior | 76.6 [70.2, 82.4] | 0.886 | 0.862 | 0.888 | 0.766 | 0.59 | 2.43 (2.79) | 1.865 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 0.455 | 0.257 | 100.0 % | 98.5 % | 0.020 |
| noul_ctx+platt | 0.213 | 0.039 | 100.0 % | 99.0 % | 0.013 |
| pick+count | 0.896 | 0.290 | 63.4 % | 51.2 % | 0.062 |
| noul_ctx+count | 0.695 | 0.283 | 82.9 % | 64.9 % | 0.043 |
| pick+dev_prior | 2.066 | 0.540 | 1.5 % | 1.5 % | 0.181 |
| noul_ctx+dev_prior | 1.865 | 0.587 | 84.9 % | 2.4 % | 0.089 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +0.98 pts [-1.95, +3.91] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -4.39 pts [-7.32, -1.95] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +76.59 pts [+70.73, +82.44] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -11.22 pts [-15.61, -7.30] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -25.37 pts [-31.71, -19.51] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -6.83 pts [-11.22, -2.44] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.24 nats [+0.18, +0.30] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 52.1 [48.1, 56.4] | 0.566 | 0.554 | 0.286 | 0.523 | 0.62 | 0.75 (0.13) | 2.260 |
| noul_ctx+platt | 92.4 [90.3, 94.5] | 0.926 | 0.926 | 0.646 | 0.924 | 0.08 | 0.10 (0.13) | 0.229 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [8.0, 12.9] | 0.109 | 0.108 | 0.197 | 0.110 | 0.89 | 1.00 (0.13) | — |
| pick+true_count | 99.1 [98.2, 99.8] | 0.993 | 0.992 | 0.931 | 1.000 | 0.00 | 0.13 (0.13) | — |
| noul_ctx+true_count | 98.9 [98.1, 99.6] | 0.991 | 0.991 | 0.917 | 1.000 | 0.00 | 0.13 (0.13) | — |
| pick+count | 69.6 [65.9, 73.3] | 0.734 | 0.724 | 0.390 | 0.696 | 0.38 | 0.49 (0.13) | 1.208 |
| noul_ctx+count | 72.8 [69.1, 76.5] | 0.761 | 0.753 | 0.411 | 0.728 | 0.34 | 0.45 (0.13) | 1.213 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.456 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.461 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 2.260 | 0.311 | 9.4 % | 0.4 % | 0.311 |
| noul_ctx+platt | 0.229 | 0.025 | 100.0 % | 91.9 % | 0.011 |
| pick+count | 1.208 | 0.214 | 16.6 % | 3.9 % | 0.180 |
| noul_ctx+count | 1.213 | 0.266 | 50.4 % | 1.2 % | 0.142 |
| pick+dev_prior | 0.456 | 0.046 | 48.2 % | 1.1 % | 0.102 |
| noul_ctx+dev_prior | 0.461 | 0.046 | 48.2 % | 1.1 % | 0.102 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +6.71 pts [+4.77, +8.83] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.18 pts [-0.35, +0.88] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.69 pts [+86.04, +91.34] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -29.51 pts [-33.22, -25.97] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.95 pts [-13.43, -8.30] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +20.67 pts [+17.31, +24.38] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.05 nats [-1.09, -1.00] |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul@0.5 | 99.1 [97.7, 100.0] | 0.999 | 0.998 | 0.998 | 0.991 | 0.01 | 2.45 (2.44) | 3.960 |
| noul+platt | 99.1 [97.7, 100.0] | 0.999 | 0.998 | 0.998 | 0.991 | 0.01 | 2.45 (2.44) | 0.071 |
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| pick@top1 | 23.3 [17.7, 29.3] | 0.585 | 0.476 | 0.535 | 0.237 | 1.58 | 1.00 (2.44) | — |
| pick+true_count | 97.7 [95.3, 99.5] | 0.991 | 0.988 | 0.990 | 1.000 | 0.00 | 2.44 (2.44) | — |
| noul+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | — |
| pick+count | 67.4 [61.4, 73.5] | 0.870 | 0.839 | 0.898 | 0.674 | 0.51 | 2.51 (2.44) | 2.799 |
| noul+count | 78.6 [73.0, 83.7] | 0.954 | 0.927 | 0.955 | 0.786 | 0.23 | 2.67 (2.44) | 2.056 |
| pick+dev_prior | 53.5 [47.0, 60.0] | 0.587 | 0.573 | 0.537 | 0.535 | 1.55 | 0.92 (2.44) | 3.365 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul@0.5 | 3.960 | 0.774 | 100.0 % | 100.0 % | 0.003 |
| noul+platt | 0.071 | 0.009 | 100.0 % | 100.0 % | 0.000 |
| pick+count | 2.799 | 0.408 | 45.1 % | 42.8 % | 0.131 |
| noul+count | 2.056 | 0.464 | 61.9 % | 38.1 % | 0.084 |
| pick+dev_prior | 3.365 | 0.444 | 40.5 % | 31.2 % | 0.183 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul@0.5 | -1.40 pts [-4.19, +0.93] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +74.42 pts [+67.91, +80.00] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -30.23 pts [-36.28, -24.19] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -44.19 pts [-50.70, -37.21] |
