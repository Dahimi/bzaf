# Benchmark v0 — ours

Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).

| track | items (test) | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|
| ecthr | 217 | — | — | — | — |
| goemotions | 403 | — | — | — | — |
| nlupp | 424 | — | — | — | — |
| sata | 1137 | — | — | — | — |
| synthetic | 205 | — | — | — | — |
| unfair_tos | 566 | — | — | — | — |
| wide (probe) | 215 | — | — | — | — |

## General decisions (single answer, each question in its own type)

Accuracy with its 95 % CI; chance-corrected accuracy = (accuracy − chance) / (1 − chance); log-loss and calibration error of the answer's probability.

| track | items (test) | accuracy % [95% CI] | chance % | chance-corrected % | log-loss | calibration error |
|---|---|---|---|---|---|---|
| anli | 224 | 60.3 [53.6, 66.5] | 33.3 | 40.4 | 0.983 | 0.148 |
| bbh | 219 | 66.2 [59.8, 72.6] | 31.6 | 50.6 | 0.866 | 0.083 |
| boolq | 205 | 86.3 [81.5, 90.7] | 50.0 | 72.7 | 0.313 | 0.075 |
| clinc150 | 201 | 77.6 [71.6, 83.1] | 0.7 | 77.5 | 0.890 | 0.070 |
| hellaswag | 198 | 87.9 [83.3, 92.4] | 25.0 | 83.8 | 0.447 | 0.155 |
| mmlu_pro | 211 | 44.1 [37.0, 50.7] | 10.8 | 37.3 | 1.662 | 0.058 |
| sst5 | 212 | 57.5 [50.9, 64.2] | 20.0 | 46.9 | 1.064 | 0.132 |
| **mean** | | | | **58.5** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | ours@mode | 62 | 82.3 % | 0.844 |
| nlupp | ours@mode | 67 | 91.0 % | 0.928 |
| sata | ours@mode | 66 | 77.3 % | 0.906 |

## Cost and quality against the number of options (wide probe)

Median seconds per item for one yes/no question per option vs the one-pass questions; example F1.

| options | items | fan-out s | one-pass s |  |
|---|---|---|---|
| 10 | 55 | nan | nan |  |
| 50 | 54 | nan | nan |  |
| 100 | 53 | nan | nan |  |
| 200 | 53 | nan | nan |  |

# Per-track details — ours

## anli (dev 76, test 224, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 60.3 [53.6, 66.5] | 0.603 | 0.603 | 0.603 | 1.000 | 0.00 | 1.00 (1.00) | 0.983 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.983 | 0.148 | 0.4 % | 0.4 % | 0.322 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 66.2 [59.8, 72.6] | 0.662 | 0.662 | 0.662 | 1.000 | 0.00 | 1.00 (1.00) | 0.866 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.866 | 0.083 | 28.3 % | 19.6 % | 0.165 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 86.3 [81.5, 90.7] | 0.863 | 0.863 | 0.863 | 1.000 | 0.00 | 1.00 (1.00) | 0.313 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.313 | 0.075 | 93.2 % | 73.2 % | 0.048 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 77.6 [71.6, 83.1] | 0.776 | 0.776 | 0.776 | 1.000 | 0.00 | 1.00 (1.00) | 0.890 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.890 | 0.070 | 81.6 % | 73.1 % | 0.043 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| ours@mode | 25.8 [19.8, 31.8] | 0.298 | 0.288 | 0.349 | 0.281 | 0.92 | 0.41 (1.09) | 2.169 |
| ours+dev_prior | 56.7 [49.8, 63.1] | 0.651 | 0.628 | 0.683 | 0.691 | 0.37 | 0.93 (1.09) | 1.790 |
| ours+dev_prior@16 | 56.7 [49.8, 63.1] | 0.667 | 0.640 | 0.695 | 0.668 | 0.40 | 0.99 (1.09) | 2.100 |
| ours+dev_prior@64 | 54.4 [47.5, 61.3] | 0.620 | 0.599 | 0.663 | 0.641 | 0.44 | 0.84 (1.09) | 1.839 |
| ours+dev_match | 43.8 [37.3, 50.7] | 0.539 | 0.512 | 0.577 | 0.493 | 0.73 | 0.94 (1.09) | 1.935 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.169 | 0.244 | 0.0 % | 0.0 % | 0.747 |
| ours+dev_prior | 1.790 | 0.239 | 0.9 % | 0.9 % | 0.336 |
| ours+dev_prior@16 | 2.100 | 0.348 | 0.9 % | 0.9 % | 0.343 |
| ours+dev_prior@64 | 1.839 | 0.255 | 0.9 % | 0.9 % | 0.340 |
| ours+dev_match | 1.935 | 0.153 | 0.5 % | 0.5 % | 0.533 |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| ours@mode | 33.0 [28.3, 37.7] | 0.399 | 0.381 | 0.495 | 0.439 | 0.70 | 0.73 (1.18) | 2.590 |
| ours+dev_prior | 47.6 [42.7, 52.6] | 0.558 | 0.537 | 0.551 | 0.829 | 0.18 | 1.00 (1.18) | 2.157 |
| ours+dev_prior@16 | 47.6 [42.7, 52.6] | 0.558 | 0.537 | 0.551 | 0.829 | 0.18 | 1.00 (1.18) | 2.985 |
| ours+dev_prior@64 | 47.6 [42.7, 52.6] | 0.558 | 0.537 | 0.551 | 0.829 | 0.18 | 1.00 (1.18) | 2.365 |
| ours+dev_match | 48.1 [43.2, 53.1] | 0.560 | 0.540 | 0.554 | 0.834 | 0.18 | 1.00 (1.18) | 2.152 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.590 | 0.040 | 5.7 % | 2.7 % | 0.485 |
| ours+dev_prior | 2.157 | 0.050 | 12.4 % | 6.0 % | 0.335 |
| ours+dev_prior@16 | 2.985 | 0.260 | 12.4 % | 6.0 % | 0.335 |
| ours+dev_prior@64 | 2.365 | 0.116 | 12.4 % | 6.0 % | 0.335 |
| ours+dev_match | 2.152 | 0.065 | 8.4 % | 7.9 % | 0.317 |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 87.9 [83.3, 92.4] | 0.879 | 0.879 | 0.879 | 1.000 | 0.00 | 1.00 (1.00) | 0.447 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.447 | 0.155 | 93.9 % | 81.8 % | 0.030 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 44.1 [37.0, 50.7] | 0.441 | 0.441 | 0.441 | 1.000 | 0.00 | 1.00 (1.00) | 1.662 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.662 | 0.058 | 14.7 % | 1.9 % | 0.344 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 13.7 [10.4, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| ours@mode | 30.9 [26.7, 35.6] | 0.523 | 0.466 | 0.499 | 0.323 | 1.25 | 0.70 (1.93) | 3.589 |
| ours+dev_prior | 33.7 [29.5, 38.2] | 0.677 | 0.595 | 0.674 | 0.417 | 0.84 | 1.48 (1.93) | 3.481 |
| ours+dev_prior@16 | 15.6 [12.0, 19.1] | 0.170 | 0.167 | 0.068 | 0.156 | 1.87 | 0.08 (1.93) | 4.357 |
| ours+dev_prior@64 | 28.1 [24.1, 32.5] | 0.472 | 0.428 | 0.515 | 0.328 | 1.22 | 0.91 (1.93) | 3.723 |
| ours+dev_match | 39.6 [35.1, 44.3] | 0.642 | 0.582 | 0.645 | 0.455 | 0.88 | 1.12 (1.93) | 3.040 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 3.589 | 0.252 | 11.1 % | 8.5 % | 0.466 |
| ours+dev_prior | 3.481 | 0.200 | 0.9 % | 0.9 % | 0.606 |
| ours+dev_prior@16 | 4.357 | 0.113 | 0.7 % | 0.7 % | 0.713 |
| ours+dev_prior@64 | 3.723 | 0.183 | 0.7 % | 0.7 % | 0.596 |
| ours+dev_match | 3.040 | 0.065 | 12.7 % | 10.8 % | 0.400 |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| ours@mode | 23.0 [20.6, 25.5] | 0.572 | 0.499 | 0.640 | 0.250 | 2.06 | 2.37 (3.60) | 4.516 |
| ours+dev_prior | 31.2 [28.7, 34.0] | 0.693 | 0.591 | 0.651 | 0.427 | 1.54 | 2.17 (3.60) | 3.460 |
| ours+dev_prior@16 | 13.0 [11.1, 15.0] | 0.724 | 0.601 | 0.705 | 0.199 | 1.77 | 3.60 (3.60) | 3.798 |
| ours+dev_prior@64 | 34.3 [31.5, 37.2] | 0.723 | 0.626 | 0.685 | 0.422 | 1.60 | 2.59 (3.60) | 3.509 |
| ours+dev_match | 34.8 [32.0, 37.7] | 0.747 | 0.657 | 0.731 | 0.415 | 1.48 | 3.08 (3.60) | 3.747 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 4.516 | 0.201 | 0.0 % | 0.0 % | 0.643 |
| ours+dev_prior | 3.460 | 0.148 | 20.4 % | 14.3 % | 0.395 |
| ours+dev_prior@16 | 3.798 | 0.060 | 0.0 % | 0.0 % | 0.794 |
| ours+dev_prior@64 | 3.509 | 0.167 | 20.2 % | 4.7 % | 0.377 |
| ours+dev_match | 3.747 | 0.079 | 16.3 % | 0.2 % | 0.376 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| ours@mode | 30.6 | 49.9 | -1.23 | 2.06 | 12.3 | 280 |
| ours+dev_prior | 31.2 | 59.1 | -1.43 | 1.54 | 12.5 | 0 |
| ours+dev_prior@16 | 13.1 | 60.1 | -0.01 | 1.77 | 12.5 | 9 |
| ours+dev_prior@64 | 34.3 | 62.6 | -1.01 | 1.60 | 13.6 | 0 |
| ours+dev_match | 35.3 | 65.7 | -0.52 | 1.48 | 12.6 | 15 |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 57.5 [50.9, 64.2] | 0.575 | 0.575 | 0.575 | 1.000 | 0.00 | 1.00 (1.00) | 1.064 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.064 | 0.132 | 0.9 % | 0.9 % | 0.360 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| ours@mode | 98.0 [96.1, 99.5] | 0.997 | 0.995 | 0.997 | 0.980 | 0.02 | 2.81 (2.79) | 0.085 |
| ours+dev_prior | 75.6 [69.7, 81.5] | 0.884 | 0.859 | 0.891 | 0.756 | 0.58 | 2.51 (2.79) | 1.820 |
| ours+dev_prior@16 | 41.5 [35.1, 48.3] | 0.806 | 0.735 | 0.833 | 0.415 | 1.03 | 3.41 (2.79) | 1.921 |
| ours+dev_prior@64 | 66.8 [60.5, 73.2] | 0.850 | 0.811 | 0.868 | 0.668 | 0.75 | 2.87 (2.79) | 1.829 |
| ours+dev_match | 97.6 [95.1, 99.5] | 0.997 | 0.995 | 0.996 | 0.976 | 0.02 | 2.81 (2.79) | 0.100 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.085 | 0.037 | 100.0 % | 100.0 % | 0.001 |
| ours+dev_prior | 1.820 | 0.562 | 39.0 % | 2.0 % | 0.155 |
| ours+dev_prior@16 | 1.921 | 0.325 | 0.0 % | 0.0 % | 0.665 |
| ours+dev_prior@64 | 1.829 | 0.486 | 2.0 % | 2.0 % | 0.313 |
| ours+dev_match | 0.100 | 0.039 | 100.0 % | 100.0 % | 0.001 |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| ours@mode | 84.6 [81.8, 87.5] | 0.861 | 0.857 | 0.457 | 0.848 | 0.24 | 0.32 (0.13) | 0.539 |
| ours+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.455 |
| ours+dev_prior@16 | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.745 |
| ours+dev_prior@64 | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.517 |
| ours+dev_match | 89.9 [87.5, 92.4] | 0.905 | 0.904 | 0.530 | 0.899 | 0.15 | 0.20 (0.13) | 0.332 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.539 | 0.105 | 83.0 % | 67.3 % | 0.041 |
| ours+dev_prior | 0.455 | 0.046 | 48.2 % | 0.7 % | 0.103 |
| ours+dev_prior@16 | 0.745 | 0.282 | 48.2 % | 0.7 % | 0.103 |
| ours+dev_prior@64 | 0.517 | 0.095 | 48.2 % | 0.7 % | 0.103 |
| ours+dev_match | 0.332 | 0.064 | 99.8 % | 85.3 % | 0.018 |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| ours@mode | 98.1 [96.3, 99.5] | 0.998 | 0.996 | 0.996 | 0.981 | 0.02 | 2.44 (2.44) | 0.132 |
| ours+dev_prior | 83.3 [78.1, 87.9] | 0.851 | 0.847 | 0.849 | 0.833 | 0.65 | 1.83 (2.44) | 2.355 |
| ours+dev_prior@16 | 75.3 [69.8, 80.9] | 0.870 | 0.846 | 0.476 | 0.753 | 4.62 | 6.39 (2.44) | 3.107 |
| ours+dev_prior@64 | 75.8 [70.2, 81.4] | 0.781 | 0.778 | 0.746 | 0.758 | 1.00 | 1.48 (2.44) | 2.467 |
| ours+dev_match | 98.1 [96.3, 99.5] | 0.998 | 0.997 | 0.996 | 0.981 | 0.02 | 2.44 (2.44) | 0.132 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.132 | 0.058 | 100.0 % | 100.0 % | 0.001 |
| ours+dev_prior | 2.355 | 0.718 | 84.2 % | 63.3 % | 0.039 |
| ours+dev_prior@16 | 3.107 | 0.678 | 33.5 % | 18.6 % | 0.115 |
| ours+dev_prior@64 | 2.467 | 0.647 | 74.4 % | 58.1 % | 0.059 |
| ours+dev_match | 0.132 | 0.063 | 100.0 % | 100.0 % | 0.000 |
