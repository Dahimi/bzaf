# Benchmark v0 — kev-4b

Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).

| track | items (test) | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|
| ecthr | 217 | 51.2 / 0.601 | 58.5 / 0.660 | — | 80.6 / 0.845 |
| goemotions | 403 | 6.2 / 0.088 | 28.5 / 0.340 | — | 30.8 / 0.352 |
| nlupp | 424 | 17.9 / 0.239 | 26.4 / 0.393 | — | 52.4 / 0.765 |
| sata | 1137 | 23.9 / 0.719 | 28.1 / 0.680 | — | 50.4 / 0.809 |
| synthetic | 205 | 85.9 / 0.969 | 67.3 / 0.852 | — | 99.5 / 0.998 |
| unfair_tos | 566 | 92.2 / 0.926 | 88.2 / 0.882 | — | 98.9 / 0.992 |
| wide (probe) | 215 | 99.1 / 0.998 | 51.6 / 0.557 | — | 100.0 / 1.000 |

## General decisions (single answer, each question in its own type)

Accuracy with its 95 % CI; chance-corrected accuracy = (accuracy − chance) / (1 − chance); log-loss and calibration error of the answer's probability.

| track | items (test) | accuracy % [95% CI] | chance % | chance-corrected % | log-loss | calibration error |
|---|---|---|---|---|---|---|
| anli | 224 | 62.1 [55.8, 68.3] | 33.3 | 43.1 | 1.294 | 0.211 |
| bbh | 219 | 66.2 [60.3, 72.2] | 31.6 | 50.6 | 0.844 | 0.050 |
| boolq | 205 | 90.7 [86.3, 94.6] | 50.0 | 81.5 | 0.256 | 0.034 |
| clinc150 | 201 | 75.1 [69.7, 81.1] | 0.7 | 75.0 | 1.520 | 0.436 |
| hellaswag | 198 | 81.3 [75.8, 86.9] | 25.0 | 75.1 | 0.568 | 0.152 |
| mmlu_pro | 211 | 52.1 [45.5, 58.8] | 10.8 | 46.3 | 1.426 | 0.083 |
| sst5 | 212 | 57.1 [50.0, 63.7] | 20.0 | 46.3 | 0.996 | 0.075 |
| **mean** | | | | **59.7** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | noul_ctx@0.5 | 62 | 43.5 % | 0.748 |
| goemotions | noul_ctx+platt | 62 | 91.9 % | 0.919 |
| goemotions | pick@top1 | 62 | 85.5 % | 0.855 |
| goemotions | pick+count | 62 | 96.8 % | 0.968 |
| goemotions | pick+dev_prior | 62 | 85.5 % | 0.855 |
| nlupp | noul_ctx@0.5 | 67 | 13.4 % | 0.612 |
| nlupp | noul_ctx+platt | 67 | 95.5 % | 0.958 |
| nlupp | pick@top1 | 67 | 83.6 % | 0.836 |
| nlupp | pick+count | 67 | 79.1 % | 0.791 |
| nlupp | pick+dev_prior | 67 | 88.1 % | 0.881 |
| sata | noul_ctx@0.5 | 66 | 59.1 % | 0.844 |
| sata | noul_ctx+platt | 66 | 65.2 % | 0.890 |
| sata | pick@top1 | 66 | 83.3 % | 0.833 |
| sata | pick+count | 66 | 87.9 % | 0.886 |
| sata | pick+dev_prior | 66 | 68.2 % | 0.811 |

## Cost and quality against the number of options (wide probe)

Median seconds per item for one yes/no question per option vs the one-pass questions; example F1.

| options | items | fan-out s | one-pass s | yes/no per option, tuned | Choice + dataset count | ceiling: ranking + true count |
|---|---|---|---|---|---|---|
| 10 | 55 | 1.71 | 1.61 | 1.000 | 0.830 | 1.000 |
| 50 | 54 | 2.46 | 1.89 | 1.000 | 0.668 | 1.000 |
| 100 | 53 | 3.65 | 3.79 | 0.996 | 0.480 | 1.000 |
| 200 | 53 | 7.77 | 7.30 | 0.997 | 0.239 | 1.000 |

# Per-track details — kev-4b

## anli (dev 76, test 224, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 62.1 [55.8, 68.3] | 0.621 | 0.621 | 0.621 | 1.000 | 0.00 | 1.00 (1.00) | 1.294 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.294 | 0.211 | 0.0 % | 0.0 % | 0.306 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 66.2 [60.3, 72.2] | 0.662 | 0.662 | 0.662 | 1.000 | 0.00 | 1.00 (1.00) | 0.844 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.844 | 0.050 | 32.4 % | 18.3 % | 0.159 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 90.7 [86.3, 94.6] | 0.907 | 0.907 | 0.907 | 1.000 | 0.00 | 1.00 (1.00) | 0.256 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.256 | 0.034 | 100.0 % | 82.0 % | 0.030 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 75.1 [69.7, 81.1] | 0.751 | 0.751 | 0.751 | 1.000 | 0.00 | 1.00 (1.00) | 1.520 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.520 | 0.436 | 60.7 % | 51.2 % | 0.083 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 41.5 [35.0, 48.4] | 0.638 | 0.581 | 0.660 | 0.484 | 0.64 | 1.24 (1.09) | 2.410 |
| noul_ctx+platt | 51.2 [44.2, 57.6] | 0.601 | 0.577 | 0.641 | 0.562 | 0.53 | 0.79 (1.09) | 1.754 |
| always_none | 12.0 [7.8, 16.6] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| pick@top1 | 59.9 [53.5, 66.4] | 0.693 | 0.667 | 0.718 | 0.719 | 0.33 | 1.00 (1.09) | — |
| pick+true_count | 80.6 [75.6, 85.7] | 0.845 | 0.833 | 0.819 | 1.000 | 0.00 | 1.09 (1.09) | — |
| noul_ctx+true_count | 76.0 [70.0, 81.6] | 0.797 | 0.785 | 0.768 | 1.000 | 0.00 | 1.09 (1.09) | — |
| pick+count | 36.4 [30.0, 42.9] | 0.385 | 0.379 | 0.428 | 0.382 | 0.80 | 0.37 (1.09) | 1.966 |
| noul_ctx+count | 32.3 [25.8, 38.2] | 0.344 | 0.339 | 0.383 | 0.336 | 0.84 | 0.33 (1.09) | 2.065 |
| pick+dev_prior | 58.5 [51.6, 65.0] | 0.660 | 0.640 | 0.693 | 0.677 | 0.41 | 0.89 (1.09) | 1.835 |
| noul_ctx+dev_prior | 53.0 [46.1, 59.4] | 0.601 | 0.582 | 0.641 | 0.627 | 0.46 | 0.79 (1.09) | 1.935 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 2.410 | 0.253 | 0.0 % | 0.0 % | 0.494 |
| noul_ctx+platt | 1.754 | 0.157 | 0.9 % | 0.9 % | 0.454 |
| pick+count | 1.966 | 0.096 | 0.5 % | 0.5 % | 0.494 |
| noul_ctx+count | 2.065 | 0.064 | 0.9 % | 0.9 % | 0.547 |
| pick+dev_prior | 1.835 | 0.296 | 0.5 % | 0.5 % | 0.287 |
| noul_ctx+dev_prior | 1.935 | 0.266 | 1.4 % | 1.4 % | 0.314 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +29.49 pts [+23.50, +35.94] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +4.61 pts [+0.46, +8.76] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +20.74 pts [+15.21, +26.28] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -44.24 pts [-50.23, -37.79] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -22.12 pts [-28.11, -16.59] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -9.22 pts [-15.21, -3.23] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.34 nats [-0.44, -0.24] |

## goemotions (dev 197, test 403, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.2 [1.7, 5.2] | 0.258 | 0.186 | 0.288 | 0.166 | 1.80 | 2.68 (1.18) | 7.183 |
| noul_ctx+platt | 6.2 [4.0, 8.7] | 0.088 | 0.082 | 0.154 | 0.114 | 1.02 | 0.20 (1.18) | 3.766 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| pick@top1 | 28.5 [24.1, 33.0] | 0.340 | 0.326 | 0.337 | 0.829 | 0.18 | 1.00 (1.18) | — |
| pick+true_count | 30.8 [26.3, 35.2] | 0.352 | 0.337 | 0.357 | 1.000 | 0.00 | 1.18 (1.18) | — |
| noul_ctx+true_count | 26.6 [21.8, 31.0] | 0.313 | 0.297 | 0.324 | 1.000 | 0.00 | 1.18 (1.18) | — |
| pick+count | 5.7 [3.5, 8.2] | 0.067 | 0.065 | 0.112 | 0.082 | 1.08 | 0.10 (1.18) | 4.534 |
| noul_ctx+count | 5.5 [3.5, 7.7] | 0.066 | 0.063 | 0.112 | 0.079 | 1.08 | 0.10 (1.18) | 4.598 |
| pick+dev_prior | 28.5 [24.1, 33.0] | 0.340 | 0.326 | 0.337 | 0.829 | 0.18 | 1.00 (1.18) | 3.223 |
| noul_ctx+dev_prior | 24.8 [20.3, 29.3] | 0.299 | 0.286 | 0.298 | 0.829 | 0.18 | 1.00 (1.18) | 3.287 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 7.183 | 0.026 | 0.0 % | 0.0 % | 0.954 |
| noul_ctx+platt | 3.766 | 0.290 | 0.0 % | 0.0 % | 0.973 |
| pick+count | 4.534 | 0.102 | 1.7 % | 1.7 % | 0.872 |
| noul_ctx+count | 4.598 | 0.105 | 1.5 % | 1.5 % | 0.868 |
| pick+dev_prior | 3.223 | 0.085 | 1.7 % | 1.7 % | 0.633 |
| noul_ctx+dev_prior | 3.287 | 0.077 | 0.7 % | 0.7 % | 0.672 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +24.57 pts [+20.60, +28.78] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +4.22 pts [+0.99, +7.69] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +2.23 pts [+0.99, +3.72] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -25.06 pts [-29.28, -20.84] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -2.23 pts [-3.72, -0.99] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +2.23 pts [-0.74, +4.96] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -2.58 nats [-2.74, -2.42] |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 81.3 [75.8, 86.9] | 0.813 | 0.813 | 0.813 | 1.000 | 0.00 | 1.00 (1.00) | 0.568 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.568 | 0.152 | 81.8 % | 60.6 % | 0.049 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 52.1 [45.5, 58.8] | 0.521 | 0.521 | 0.521 | 1.000 | 0.00 | 1.00 (1.00) | 1.426 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.426 | 0.083 | 26.1 % | 11.4 % | 0.248 |

## nlupp (dev 176, test 424, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 2.8 [1.4, 4.5] | 0.258 | 0.172 | 0.191 | 0.050 | 13.29 | 15.16 (1.93) | 25.546 |
| noul_ctx+platt | 17.9 [14.4, 21.7] | 0.239 | 0.221 | 0.143 | 0.182 | 1.77 | 0.18 (1.93) | 6.010 |
| always_none | 13.7 [10.6, 17.2] | 0.137 | 0.137 | 0.000 | 0.137 | 1.93 | 0.00 (1.93) | — |
| pick@top1 | 18.2 [14.6, 21.9] | 0.512 | 0.417 | 0.518 | 0.224 | 1.21 | 1.00 (1.93) | — |
| pick+true_count | 52.4 [47.6, 57.1] | 0.765 | 0.696 | 0.707 | 1.000 | 0.00 | 1.93 (1.93) | — |
| noul_ctx+true_count | 38.9 [34.4, 43.4] | 0.649 | 0.568 | 0.553 | 1.000 | 0.00 | 1.93 (1.93) | — |
| pick+count | 25.5 [21.5, 29.7] | 0.377 | 0.343 | 0.285 | 0.255 | 1.60 | 0.33 (1.93) | 5.390 |
| noul_ctx+count | 17.9 [14.4, 21.7] | 0.217 | 0.207 | 0.104 | 0.179 | 1.82 | 0.11 (1.93) | 7.236 |
| pick+dev_prior | 26.4 [22.4, 30.7] | 0.393 | 0.360 | 0.357 | 0.300 | 1.46 | 0.53 (1.93) | 4.291 |
| noul_ctx+dev_prior | 14.6 [11.6, 18.2] | 0.149 | 0.149 | 0.015 | 0.146 | 1.92 | 0.02 (1.93) | 6.137 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 25.546 | 0.028 | 0.0 % | 0.0 % | 0.903 |
| noul_ctx+platt | 6.010 | 0.138 | 0.2 % | 0.2 % | 0.687 |
| pick+count | 5.390 | 0.125 | 0.2 % | 0.2 % | 0.614 |
| noul_ctx+count | 7.236 | 0.112 | 1.2 % | 1.2 % | 0.672 |
| pick+dev_prior | 4.291 | 0.195 | 0.0 % | 0.0 % | 0.638 |
| noul_ctx+dev_prior | 6.137 | 0.108 | 0.0 % | 0.0 % | 0.737 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +34.43 pts [+29.95, +38.92] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +13.44 pts [+9.67, +17.22] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +34.20 pts [+29.95, +38.92] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -26.89 pts [-31.13, -22.64] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -25.94 pts [-29.95, -21.70] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +15.09 pts [+11.32, +18.87] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -18.31 nats [-19.65, -17.00] |

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 25.9 [23.5, 28.6] | 0.708 | 0.610 | 0.733 | 0.338 | 1.35 | 3.11 (3.60) | 4.007 |
| noul_ctx+platt | 23.9 [21.5, 26.4] | 0.719 | 0.617 | 0.739 | 0.307 | 1.38 | 3.42 (3.60) | 3.984 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.448 | 0.310 | 0.396 | 0.000 | 2.60 | 1.00 (3.60) | — |
| pick+true_count | 50.4 [47.6, 53.2] | 0.809 | 0.735 | 0.812 | 1.000 | 0.00 | 3.60 (3.60) | — |
| noul_ctx+true_count | 53.5 [50.6, 56.2] | 0.820 | 0.749 | 0.822 | 1.000 | 0.00 | 3.60 (3.60) | — |
| pick+count | 12.6 [10.6, 14.5] | 0.320 | 0.272 | 0.350 | 0.129 | 2.84 | 0.80 (3.60) | 4.588 |
| noul_ctx+count | 12.0 [10.1, 13.9] | 0.305 | 0.260 | 0.351 | 0.123 | 2.84 | 0.80 (3.60) | 4.629 |
| pick+dev_prior | 28.1 [25.4, 30.8] | 0.680 | 0.573 | 0.634 | 0.407 | 1.61 | 2.16 (3.60) | 3.850 |
| noul_ctx+dev_prior | 27.7 [25.1, 30.3] | 0.684 | 0.575 | 0.640 | 0.402 | 1.62 | 2.18 (3.60) | 3.891 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 4.007 | 0.085 | 0.0 % | 0.0 % | 0.572 |
| noul_ctx+platt | 3.984 | 0.079 | 0.1 % | 0.1 % | 0.589 |
| pick+count | 4.588 | 0.164 | 0.0 % | 0.0 % | 0.831 |
| noul_ctx+count | 4.629 | 0.161 | 0.0 % | 0.0 % | 0.863 |
| pick+dev_prior | 3.850 | 0.144 | 16.2 % | 5.5 % | 0.430 |
| noul_ctx+dev_prior | 3.891 | 0.136 | 2.6 % | 2.5 % | 0.492 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 27.2 | 61.0 | -0.49 | 1.35 | 8.4 | 54 |
| noul_ctx+platt | 24.8 | 61.7 | -0.18 | 1.38 | 8.2 | 39 |
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| pick@top1 | 0.0 | 31.0 | -2.60 | 2.60 | 7.9 | 0 |
| pick+true_count | 50.4 | 73.5 | +0.00 | 0.00 | 5.3 | 0 |
| noul_ctx+true_count | 53.5 | 74.9 | +0.00 | 0.00 | 5.1 | 0 |
| pick+count | 28.4 | 27.2 | -2.80 | 2.84 | 8.4 | 633 |
| noul_ctx+count | 28.4 | 26.0 | -2.81 | 2.84 | 6.4 | 658 |
| pick+dev_prior | 28.1 | 57.3 | -1.45 | 1.61 | 13.3 | 0 |
| noul_ctx+dev_prior | 27.7 | 57.5 | -1.42 | 1.62 | 14.4 | 0 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +24.45 pts [+21.81, +27.26] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -3.08 pts [-4.93, -1.23] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +50.40 pts [+47.58, +53.21] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -37.82 pts [-40.63, -35.00] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -22.34 pts [-24.89, -20.05] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -13.98 pts [-16.36, -11.61] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.62 nats [+0.54, +0.70] |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 57.1 [50.0, 63.7] | 0.571 | 0.571 | 0.571 | 1.000 | 0.00 | 1.00 (1.00) | 0.996 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.996 | 0.075 | 1.9 % | 1.9 % | 0.371 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 86.3 [81.5, 90.7] | 0.970 | 0.956 | 0.976 | 0.863 | 0.14 | 2.84 (2.79) | 0.856 |
| noul_ctx+platt | 85.9 [81.0, 90.2] | 0.969 | 0.955 | 0.975 | 0.859 | 0.14 | 2.80 (2.79) | 0.388 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| pick@top1 | 19.5 [14.1, 24.9] | 0.567 | 0.449 | 0.505 | 0.195 | 1.88 | 1.00 (2.79) | — |
| pick+true_count | 99.5 [98.5, 100.0] | 0.998 | 0.998 | 0.998 | 1.000 | 0.00 | 2.79 (2.79) | — |
| noul_ctx+true_count | 99.5 [98.5, 100.0] | 0.998 | 0.998 | 0.998 | 1.000 | 0.00 | 2.79 (2.79) | — |
| pick+count | 62.4 [56.1, 68.8] | 0.826 | 0.791 | 0.857 | 0.624 | 0.71 | 2.20 (2.79) | 1.500 |
| noul_ctx+count | 59.0 [52.7, 65.9] | 0.836 | 0.795 | 0.859 | 0.590 | 0.71 | 2.21 (2.79) | 1.480 |
| pick+dev_prior | 67.3 [61.0, 73.7] | 0.852 | 0.816 | 0.858 | 0.673 | 0.75 | 2.45 (2.79) | 2.014 |
| noul_ctx+dev_prior | 64.4 [57.6, 70.7] | 0.832 | 0.790 | 0.831 | 0.644 | 0.87 | 2.39 (2.79) | 1.994 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 0.856 | 0.375 | 84.4 % | 49.3 % | 0.049 |
| noul_ctx+platt | 0.388 | 0.060 | 88.8 % | 68.8 % | 0.037 |
| pick+count | 1.500 | 0.300 | 17.6 % | 14.1 % | 0.228 |
| noul_ctx+count | 1.480 | 0.257 | 19.5 % | 13.2 % | 0.246 |
| pick+dev_prior | 2.014 | 0.510 | 1.5 % | 1.5 % | 0.187 |
| noul_ctx+dev_prior | 1.994 | 0.482 | 16.1 % | 4.9 % | 0.177 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +13.17 pts [+8.29, +18.05] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.00 pts [-1.46, +1.46] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +80.00 pts [+74.63, +85.37] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -37.07 pts [-43.41, -30.73] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -32.20 pts [-38.54, -25.85] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -27.32 pts [-34.15, -20.00] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.62 nats [+0.55, +0.70] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 61.3 [57.4, 65.2] | 0.656 | 0.642 | 0.258 | 0.613 | 0.73 | 0.86 (0.13) | 2.355 |
| noul_ctx+platt | 92.2 [89.9, 94.3] | 0.926 | 0.925 | 0.589 | 0.922 | 0.08 | 0.07 (0.13) | 0.277 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [8.0, 12.9] | 0.108 | 0.107 | 0.194 | 0.110 | 0.89 | 1.00 (0.13) | — |
| pick+true_count | 98.9 [98.1, 99.6] | 0.992 | 0.991 | 0.917 | 1.000 | 0.00 | 0.13 (0.13) | — |
| noul_ctx+true_count | 99.1 [98.2, 99.8] | 0.994 | 0.993 | 0.931 | 1.000 | 0.00 | 0.13 (0.13) | — |
| pick+count | 82.9 [79.7, 85.9] | 0.834 | 0.833 | 0.510 | 0.832 | 0.17 | 0.24 (0.13) | 0.763 |
| noul_ctx+count | 85.9 [83.0, 88.7] | 0.862 | 0.861 | 0.530 | 0.862 | 0.14 | 0.19 (0.13) | 0.782 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.470 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.489 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 2.355 | 0.399 | 46.1 % | 38.9 % | 0.138 |
| noul_ctx+platt | 0.277 | 0.037 | 100.0 % | 89.0 % | 0.013 |
| pick+count | 0.763 | 0.278 | 79.5 % | 50.4 % | 0.078 |
| noul_ctx+count | 0.782 | 0.330 | 92.2 % | 76.3 % | 0.031 |
| pick+dev_prior | 0.470 | 0.048 | 48.2 % | 0.7 % | 0.102 |
| noul_ctx+dev_prior | 0.489 | 0.048 | 48.2 % | 0.7 % | 0.102 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +6.71 pts [+4.77, +8.83] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | -0.18 pts [-0.71, +0.35] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.52 pts [+86.04, +91.17] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -16.08 pts [-19.08, -13.25] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.78 pts [-13.26, -8.30] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +24.56 pts [+20.67, +28.45] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.57 nats [-1.69, -1.47] |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul@0.5 | 96.7 [94.4, 99.1] | 0.995 | 0.992 | 0.993 | 0.967 | 0.03 | 2.47 (2.44) | 9.630 |
| noul+platt | 99.1 [97.7, 100.0] | 0.998 | 0.997 | 0.998 | 0.991 | 0.01 | 2.44 (2.44) | 0.042 |
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| pick@top1 | 23.7 [18.1, 30.2] | 0.591 | 0.482 | 0.541 | 0.237 | 1.58 | 1.00 (2.44) | — |
| pick+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | — |
| noul+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | — |
| pick+count | 63.7 [57.7, 70.2] | 0.659 | 0.655 | 0.678 | 0.637 | 1.19 | 1.26 (2.44) | 3.012 |
| noul+count | 74.4 [68.8, 80.0] | 0.793 | 0.785 | 0.818 | 0.744 | 0.75 | 1.69 (2.44) | 2.436 |
| pick+dev_prior | 51.6 [45.1, 58.1] | 0.557 | 0.548 | 0.513 | 0.516 | 1.60 | 0.86 (2.44) | 3.508 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul@0.5 | 9.630 | 0.862 | 100.0 % | 100.0 % | 0.013 |
| noul+platt | 0.042 | 0.012 | 100.0 % | 100.0 % | 0.002 |
| pick+count | 3.012 | 0.445 | 67.9 % | 56.3 % | 0.092 |
| noul+count | 2.436 | 0.527 | 79.1 % | 69.8 % | 0.051 |
| pick+dev_prior | 3.508 | 0.433 | 35.3 % | 32.1 % | 0.200 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul+platt | +0.93 pts [+0.00, +2.33] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +76.28 pts [+69.77, +81.86] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -36.28 pts [-42.34, -29.77] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -48.37 pts [-54.88, -41.86] |
