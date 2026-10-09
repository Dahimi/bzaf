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
| anli | 224 | 35.3 [29.5, 41.5] | 33.3 | 2.9 | 1.645 | 0.340 |
| bbh | 219 | 42.0 [35.6, 48.4] | 31.6 | 15.2 | 1.407 | 0.182 |
| boolq | 205 | 75.1 [69.3, 80.5] | 50.0 | 50.2 | 0.577 | 0.081 |
| clinc150 | 201 | 76.6 [70.6, 82.1] | 0.7 | 76.5 | 0.919 | 0.065 |
| hellaswag | 198 | 46.0 [38.9, 53.0] | 25.0 | 27.9 | 1.259 | 0.110 |
| mmlu_pro | 211 | 18.5 [13.3, 23.7] | 10.8 | 8.6 | 2.406 | 0.111 |
| sst5 | 212 | 47.6 [41.0, 54.3] | 20.0 | 34.6 | 1.269 | 0.094 |
| **mean** | | | | **30.8** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | ours@mode | 62 | 93.5 % | 0.953 |
| nlupp | ours@mode | 67 | 91.0 % | 0.910 |
| sata | ours@mode | 66 | 97.0 % | 0.980 |

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
| native@top1 | 35.3 [29.5, 41.5] | 0.353 | 0.353 | 0.353 | 1.000 | 0.00 | 1.00 (1.00) | 1.645 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.645 | 0.340 | 0.9 % | 0.9 % | 0.612 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 42.0 [35.6, 48.4] | 0.420 | 0.420 | 0.420 | 1.000 | 0.00 | 1.00 (1.00) | 1.407 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.407 | 0.182 | 0.9 % | 0.9 % | 0.543 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 75.1 [69.3, 80.5] | 0.751 | 0.751 | 0.751 | 1.000 | 0.00 | 1.00 (1.00) | 0.577 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.577 | 0.081 | 15.1 % | 1.0 % | 0.176 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 76.6 [70.6, 82.1] | 0.766 | 0.766 | 0.766 | 1.000 | 0.00 | 1.00 (1.00) | 0.919 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.919 | 0.065 | 81.6 % | 72.6 % | 0.046 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| ours@mode | 13.4 [9.2, 18.0] | 0.138 | 0.137 | 0.078 | 0.152 | 1.05 | 0.08 (1.09) | 2.716 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.716 | 0.373 | 0.0 % | 0.0 % | 0.875 |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| ours@mode | 21.6 [17.6, 25.6] | 0.254 | 0.244 | 0.361 | 0.313 | 0.82 | 0.45 (1.18) | 2.657 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 2.657 | 0.133 | 3.7 % | 3.2 % | 0.669 |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 46.0 [38.9, 53.0] | 0.460 | 0.460 | 0.460 | 1.000 | 0.00 | 1.00 (1.00) | 1.259 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.259 | 0.110 | 1.0 % | 1.0 % | 0.380 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 18.5 [13.3, 23.7] | 0.185 | 0.185 | 0.185 | 1.000 | 0.00 | 1.00 (1.00) | 2.406 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 2.406 | 0.111 | 0.0 % | 0.0 % | 0.739 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 13.7 [10.4, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| ours@mode | 21.5 [17.7, 25.5] | 0.352 | 0.313 | 0.281 | 0.224 | 1.60 | 0.33 (1.93) | 4.896 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 4.896 | 0.424 | 5.7 % | 5.4 % | 0.575 |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| ours@mode | 7.6 [6.1, 9.1] | 0.376 | 0.300 | 0.436 | 0.088 | 3.33 | 2.38 (3.60) | 7.006 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 7.006 | 0.374 | 0.0 % | 0.0 % | 0.941 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| ours@mode | 12.8 | 30.0 | -1.22 | 3.33 | 16.3 | 467 |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 47.6 [41.0, 54.3] | 0.476 | 0.476 | 0.476 | 1.000 | 0.00 | 1.00 (1.00) | 1.269 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.269 | 0.094 | 0.0 % | 0.0 % | 0.475 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| ours@mode | 91.7 [87.8, 95.1] | 0.979 | 0.971 | 0.985 | 0.917 | 0.08 | 2.80 (2.79) | 0.324 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.324 | 0.116 | 100.0 % | 87.8 % | 0.019 |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| ours@mode | 88.3 [85.5, 90.8] | 0.889 | 0.888 | 0.536 | 0.883 | 0.13 | 0.14 (0.13) | 0.511 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.511 | 0.165 | 95.9 % | 79.5 % | 0.033 |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| ours@mode | 94.4 [91.2, 97.2] | 0.992 | 0.986 | 0.988 | 0.944 | 0.06 | 2.39 (2.44) | 0.263 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| ours@mode | 0.263 | 0.112 | 100.0 % | 98.1 % | 0.006 |
