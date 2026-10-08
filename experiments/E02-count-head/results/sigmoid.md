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
| anli | 224 | 36.2 [29.9, 42.9] | 33.3 | 4.2 | 1.683 | 0.324 |
| bbh | 219 | 37.4 [31.1, 44.3] | 31.6 | 8.6 | 1.604 | 0.245 |
| boolq | 205 | 76.1 [70.2, 81.5] | 50.0 | 52.2 | 0.604 | 0.107 |
| clinc150 | 201 | 78.6 [72.6, 83.6] | 0.7 | 78.5 | 0.856 | 0.104 |
| hellaswag | 198 | 49.5 [42.4, 56.6] | 25.0 | 32.7 | 1.252 | 0.103 |
| mmlu_pro | 211 | 12.8 [8.5, 17.5] | 10.8 | 2.2 | 2.583 | 0.198 |
| sst5 | 212 | 47.6 [40.6, 54.2] | 20.0 | 34.6 | 1.267 | 0.048 |
| **mean** | | | | **30.4** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | ours@mode | 62 | 88.7 % | 0.895 |
| nlupp | ours@mode | 67 | 91.0 % | 0.940 |
| sata | ours@mode | 66 | 83.3 % | 0.951 |

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
| native@top1 | 36.2 [29.9, 42.9] | 0.362 | 0.362 | 0.362 | 1.000 | 0.00 | 1.00 (1.00) | 1.683 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.683 | 0.324 | 0.9 % | 0.9 % | 0.630 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 37.4 [31.1, 44.3] | 0.374 | 0.374 | 0.374 | 1.000 | 0.00 | 1.00 (1.00) | 1.604 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.604 | 0.245 | 0.5 % | 0.5 % | 0.572 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 76.1 [70.2, 81.5] | 0.761 | 0.761 | 0.761 | 1.000 | 0.00 | 1.00 (1.00) | 0.604 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.604 | 0.107 | 21.0 % | 0.5 % | 0.164 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 78.6 [72.6, 83.6] | 0.786 | 0.786 | 0.786 | 1.000 | 0.00 | 1.00 (1.00) | 0.856 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.856 | 0.104 | 81.6 % | 71.1 % | 0.045 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| ours@mode | 19.4 [14.3, 24.9] | 0.206 | 0.202 | 0.198 | 0.235 | 0.94 | 0.21 (1.09) | 2.403 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.403 | 0.243 | 0.5 % | 0.5 % | 0.850 |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| ours@mode | 37.5 [32.8, 42.2] | 0.420 | 0.409 | 0.523 | 0.471 | 0.62 | 0.56 (1.18) | 2.287 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.287 | 0.113 | 8.4 % | 6.0 % | 0.371 |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 49.5 [42.4, 56.6] | 0.495 | 0.495 | 0.495 | 1.000 | 0.00 | 1.00 (1.00) | 1.252 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.252 | 0.103 | 1.5 % | 1.5 % | 0.380 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 12.8 [8.5, 17.5] | 0.128 | 0.128 | 0.128 | 1.000 | 0.00 | 1.00 (1.00) | 2.583 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 2.583 | 0.198 | 0.5 % | 0.5 % | 0.809 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 13.7 [10.4, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| ours@mode | 30.9 [26.6, 35.4] | 0.585 | 0.513 | 0.549 | 0.356 | 1.10 | 0.94 (1.93) | 3.820 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 3.820 | 0.132 | 4.2 % | 2.8 % | 0.458 |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| ours@mode | 9.3 [7.7, 11.0] | 0.401 | 0.318 | 0.447 | 0.106 | 3.01 | 2.10 (3.60) | 6.780 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 6.780 | 0.193 | 0.3 % | 0.3 % | 0.809 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| ours@mode | 14.0 | 31.8 | -1.50 | 3.01 | 14.4 | 380 |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 47.6 [40.6, 54.2] | 0.476 | 0.476 | 0.476 | 1.000 | 0.00 | 1.00 (1.00) | 1.267 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.267 | 0.048 | 0.0 % | 0.0 % | 0.446 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| ours@mode | 99.5 [98.5, 100.0] | 0.995 | 0.995 | 0.999 | 0.995 | 0.00 | 2.80 (2.79) | 0.028 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.028 | 0.016 | 100.0 % | 100.0 % | 0.000 |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| ours@mode | 85.3 [82.2, 88.0] | 0.865 | 0.862 | 0.528 | 0.857 | 0.15 | 0.21 (0.13) | 0.786 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.786 | 0.320 | 86.6 % | 56.5 % | 0.060 |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| ours@mode | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | 0.000 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.000 | 0.000 | 100.0 % | 100.0 % | 0.000 |
