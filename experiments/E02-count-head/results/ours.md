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
| anli | 224 | 36.2 [30.4, 42.9] | 33.3 | 4.2 | 1.705 | 0.327 |
| bbh | 219 | 36.5 [30.1, 43.4] | 31.6 | 7.2 | 1.569 | 0.239 |
| boolq | 205 | 74.1 [68.3, 80.0] | 50.0 | 48.3 | 0.623 | 0.100 |
| clinc150 | 201 | 77.6 [71.6, 83.1] | 0.7 | 77.5 | 0.855 | 0.065 |
| hellaswag | 198 | 50.0 [42.9, 57.1] | 25.0 | 33.3 | 1.255 | 0.103 |
| mmlu_pro | 211 | 13.3 [8.5, 18.0] | 10.8 | 2.7 | 2.531 | 0.189 |
| sst5 | 212 | 48.6 [41.5, 55.2] | 20.0 | 35.7 | 1.262 | 0.089 |
| **mean** | | | | **29.9** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|

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
| native@top1 | 36.2 [30.4, 42.9] | 0.362 | 0.362 | 0.362 | 1.000 | 0.00 | 1.00 (1.00) | 1.705 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.705 | 0.327 | 0.9 % | 0.9 % | 0.631 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 36.5 [30.1, 43.4] | 0.365 | 0.365 | 0.365 | 1.000 | 0.00 | 1.00 (1.00) | 1.569 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.569 | 0.239 | 0.0 % | 0.0 % | 0.579 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 74.1 [68.3, 80.0] | 0.741 | 0.741 | 0.741 | 1.000 | 0.00 | 1.00 (1.00) | 0.623 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.623 | 0.100 | 21.0 % | 1.0 % | 0.168 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 77.6 [71.6, 83.1] | 0.776 | 0.776 | 0.776 | 1.000 | 0.00 | 1.00 (1.00) | 0.855 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.855 | 0.065 | 82.1 % | 74.6 % | 0.043 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| ours@mode | 41.5 [35.0, 48.4] | 0.528 | 0.498 | 0.559 | 0.682 | 0.38 | 1.08 (1.09) | 2.475 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.475 | 0.152 | 0.0 % | 0.0 % | 0.435 |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| ours@mode | 51.6 [46.7, 56.3] | 0.603 | 0.581 | 0.595 | 0.829 | 0.18 | 1.01 (1.18) | 2.077 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.077 | 0.112 | 7.7 % | 5.5 % | 0.301 |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 50.0 [42.9, 57.1] | 0.500 | 0.500 | 0.500 | 1.000 | 0.00 | 1.00 (1.00) | 1.255 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.255 | 0.103 | 1.5 % | 1.5 % | 0.381 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 13.3 [8.5, 18.0] | 0.133 | 0.133 | 0.133 | 1.000 | 0.00 | 1.00 (1.00) | 2.531 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 2.531 | 0.189 | 0.5 % | 0.5 % | 0.797 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 13.7 [10.4, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| ours@mode | 28.5 [24.5, 32.8] | 0.588 | 0.500 | 0.525 | 0.330 | 1.11 | 0.90 (1.93) | 5.211 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 5.211 | 0.192 | 1.4 % | 1.4 % | 0.614 |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| ours@mode | 12.7 [10.7, 14.7] | 0.546 | 0.426 | 0.509 | 0.201 | 2.03 | 1.93 (3.60) | 7.758 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 7.758 | 0.155 | 2.2 % | 2.0 % | 0.700 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| ours@mode | 12.7 | 42.6 | -1.67 | 2.03 | 10.3 | 0 |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 48.6 [41.5, 55.2] | 0.486 | 0.486 | 0.486 | 1.000 | 0.00 | 1.00 (1.00) | 1.262 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.262 | 0.089 | 0.0 % | 0.0 % | 0.453 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| ours@mode | 88.3 [83.4, 92.2] | 0.975 | 0.964 | 0.979 | 0.883 | 0.12 | 2.75 (2.79) | 0.522 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.522 | 0.234 | 98.0 % | 71.2 % | 0.038 |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| ours@mode | 6.7 [4.8, 8.7] | 0.094 | 0.087 | 0.186 | 0.081 | 0.95 | 1.07 (0.13) | 3.224 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 3.224 | 0.210 | 0.0 % | 0.0 % | 0.879 |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| ours@mode | 95.3 [92.6, 98.1] | 0.989 | 0.984 | 0.990 | 0.953 | 0.05 | 2.43 (2.44) | 0.501 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.501 | 0.297 | 100.0 % | 100.0 % | 0.009 |
