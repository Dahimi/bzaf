# Benchmark v0 — vela-2.0-4b

Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).

| track | items (test) | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|
| ecthr | 217 | 16.6 / 0.182 | 56.7 / 0.643 | 35.0 / 0.594 | 78.8 / 0.826 |
| goemotions | 403 | 1.2 / 0.016 | 32.0 / 0.390 | 17.6 / 0.427 | 36.5 / 0.411 |
| nlupp | 424 | — | — | — | — |
| sata | 1137 | 16.2 / 0.647 | 29.5 / 0.679 | 27.4 / 0.702 | 54.8 / 0.818 |
| synthetic | 205 | 70.7 / 0.920 | 69.3 / 0.850 | 65.9 / 0.923 | 98.5 / 0.996 |
| unfair_tos | 566 | 89.6 / 0.896 | 88.2 / 0.882 | 74.0 / 0.756 | 99.1 / 0.993 |
| wide (probe) | 215 | 100.0 / 1.000 | 72.1 / 0.773 | 96.3 / 0.981 | 100.0 / 1.000 |

## General decisions (single answer, each question in its own type)

Accuracy with its 95 % CI; chance-corrected accuracy = (accuracy − chance) / (1 − chance); log-loss and calibration error of the answer's probability.

| track | items (test) | accuracy % [95% CI] | chance % | chance-corrected % | log-loss | calibration error |
|---|---|---|---|---|---|---|
| anli | 224 | 53.1 [46.4, 59.4] | 33.3 | 29.7 | 1.035 | 0.184 |
| bbh | 219 | 63.0 [56.6, 69.4] | 31.6 | 45.9 | 0.927 | 0.058 |
| boolq | 205 | 87.3 [82.9, 91.7] | 50.0 | 74.6 | 0.339 | 0.040 |
| clinc150 | 201 | 77.6 [71.6, 83.1] | 0.7 | 77.5 | 1.075 | 0.114 |
| hellaswag | 198 | 77.8 [72.2, 83.3] | 25.0 | 70.4 | 0.595 | 0.055 |
| mmlu_pro | 211 | 42.2 [35.5, 48.8] | 10.8 | 35.2 | 1.781 | 0.128 |
| sst5 | 212 | 50.5 [43.9, 57.5] | 20.0 | 38.1 | 1.147 | 0.131 |
| **mean** | | | | **53.0** | | |

## Option-order stability

Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.

| track | predictor | items | unchanged | Jaccard |
|---|---|---|---|---|
| goemotions | noul_ctx@0.5 | 61 | 45.9 % | 0.849 |
| goemotions | noul_ctx+platt | 61 | 96.7 % | 0.967 |
| goemotions | pick@top1 | 61 | 82.0 % | 0.820 |
| goemotions | pick+count | 61 | 83.6 % | 0.874 |
| goemotions | pick+dev_prior | 61 | 82.0 % | 0.820 |
| goemotions | set@shipped | 61 | 55.7 % | 0.794 |
| sata | noul_ctx@0.5 | 66 | 57.6 % | 0.852 |
| sata | noul_ctx+platt | 66 | 63.6 % | 0.855 |
| sata | pick@top1 | 66 | 84.8 % | 0.848 |
| sata | pick+count | 66 | 68.2 % | 0.848 |
| sata | pick+dev_prior | 66 | 71.2 % | 0.826 |
| sata | set@shipped | 66 | 69.7 % | 0.877 |

## Cost and quality against the number of options (wide probe)

Median seconds per item for one yes/no question per option vs the one-pass questions; example F1.

| options | items | fan-out s | one-pass s | yes/no per option, tuned | Choice + dataset count | native set, as shipped | ceiling: ranking + true count |
|---|---|---|---|---|---|---|---|
| 10 | 55 | 2.48 | 2.69 | 1.000 | 0.854 | 1.000 | 1.000 |
| 50 | 54 | 13.38 | 9.02 | 1.000 | 0.765 | 0.981 | 1.000 |
| 100 | 53 | 27.12 | 18.92 | 1.000 | 0.818 | 0.990 | 1.000 |
| 200 | 53 | 56.10 | 39.03 | 1.000 | 0.653 | 0.950 | 1.000 |

# Per-track details — vela-2.0-4b

## anli (dev 76, test 224, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 53.1 [46.4, 59.4] | 0.531 | 0.531 | 0.531 | 1.000 | 0.00 | 1.00 (1.00) | 1.035 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.035 | 0.184 | 0.4 % | 0.4 % | 0.389 |

## bbh (dev 81, test 219, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 63.0 [56.6, 69.4] | 0.630 | 0.630 | 0.630 | 1.000 | 0.00 | 1.00 (1.00) | 0.927 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.927 | 0.058 | 19.2 % | 10.5 % | 0.190 |

## boolq (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 87.3 [82.9, 91.7] | 0.873 | 0.873 | 0.873 | 1.000 | 0.00 | 1.00 (1.00) | 0.339 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.339 | 0.040 | 85.4 % | 59.0 % | 0.056 |

## clinc150 (dev 99, test 201, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 77.6 [71.6, 83.1] | 0.776 | 0.776 | 0.776 | 1.000 | 0.00 | 1.00 (1.00) | 1.075 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.075 | 0.114 | 86.1 % | 65.2 % | 0.041 |

## ecthr (dev 83, test 217, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 31.3 [24.9, 37.3] | 0.501 | 0.452 | 0.524 | 0.359 | 1.01 | 1.37 (1.09) | 3.570 |
| noul_ctx+platt | 16.6 [11.5, 21.7] | 0.182 | 0.178 | 0.154 | 0.180 | 1.02 | 0.16 (1.09) | 2.579 |
| always_none | 12.0 [7.8, 16.1] | 0.120 | 0.120 | 0.000 | 0.120 | 1.09 | 0.00 (1.09) | — |
| pick@top1 | 58.5 [52.1, 65.0] | 0.667 | 0.645 | 0.687 | 0.719 | 0.33 | 1.00 (1.09) | — |
| pick+true_count | 78.8 [73.3, 84.3] | 0.826 | 0.814 | 0.797 | 1.000 | 0.00 | 1.09 (1.09) | — |
| noul_ctx+true_count | 74.7 [68.7, 80.2] | 0.794 | 0.779 | 0.764 | 1.000 | 0.00 | 1.09 (1.09) | — |
| pick+count | 35.5 [29.0, 41.9] | 0.532 | 0.484 | 0.569 | 0.387 | 1.01 | 1.47 (1.09) | 2.665 |
| noul_ctx+count | 30.9 [24.9, 36.9] | 0.343 | 0.334 | 0.382 | 0.327 | 0.87 | 0.38 (1.09) | 3.246 |
| pick+dev_prior | 56.7 [50.2, 63.6] | 0.643 | 0.622 | 0.676 | 0.691 | 0.38 | 0.95 (1.09) | 1.763 |
| noul_ctx+dev_prior | 35.0 [29.0, 41.0] | 0.374 | 0.368 | 0.417 | 0.382 | 0.79 | 0.39 (1.09) | 2.344 |
| set@shipped | 35.0 [29.0, 41.5] | 0.594 | 0.530 | 0.631 | 0.406 | 0.78 | 1.55 (1.09) | 2.295 |
| set+platt | 42.4 [36.4, 49.3] | 0.528 | 0.501 | 0.597 | 0.479 | 0.64 | 0.85 (1.09) | 1.892 |
| set+true_count | 78.3 [72.8, 83.4] | 0.817 | 0.807 | 0.789 | 1.000 | 0.00 | 1.09 (1.09) | — |
| set+dev_prior | 57.1 [50.7, 63.6] | 0.653 | 0.631 | 0.680 | 0.710 | 0.35 | 0.98 (1.09) | 1.782 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.570 | 0.274 | 0.0 % | 0.0 % | 0.713 |
| noul_ctx+platt | 2.579 | 0.268 | 0.0 % | 0.0 % | 0.871 |
| pick+count | 2.665 | 0.171 | 0.0 % | 0.0 % | 0.538 |
| noul_ctx+count | 3.246 | 0.214 | 0.0 % | 0.0 % | 0.673 |
| pick+dev_prior | 1.763 | 0.232 | 2.3 % | 2.3 % | 0.295 |
| noul_ctx+dev_prior | 2.344 | 0.219 | 2.8 % | 2.8 % | 0.420 |
| set@shipped | 2.295 | 0.131 | 0.0 % | 0.0 % | 0.546 |
| set+platt | 1.892 | 0.191 | 1.4 % | 1.4 % | 0.575 |
| set+dev_prior | 1.782 | 0.199 | 2.3 % | 2.3 % | 0.311 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -43.32 pts [-49.77, -36.87] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.46 pts [-2.30, +3.23] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +22.12 pts [+15.21, +29.03] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +47.47 pts [+40.55, +53.92] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +4.15 pts [+0.46, +8.29] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +20.28 pts [+15.21, +25.81] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -43.32 pts [-49.77, -36.87] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -22.12 pts [-27.65, -16.59] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -0.46 pts [-7.37, +5.99] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.32 nats [-0.53, -0.15] |

## goemotions (dev 197, test 403, failed 10)

> **10 items failed (2 %)** and count as wrong. First error: `HTTP 503: b'{"error":{"code":"not_ready","message":"model vela-2.0-4b is loading"}}'`. Re-run the readout to retry them.

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 3.5 [1.7, 5.5] | 0.211 | 0.145 | 0.162 | 0.092 | 7.83 | 8.92 (1.18) | 17.392 |
| noul_ctx+platt | 1.2 [0.2, 2.5] | 0.016 | 0.015 | 0.037 | 0.015 | 1.28 | 0.16 (1.18) | 4.341 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.18 | 0.00 (1.18) | — |
| pick@top1 | 32.0 [27.8, 37.0] | 0.390 | 0.373 | 0.394 | 0.816 | 0.20 | 1.00 (1.18) | — |
| pick+true_count | 36.5 [32.0, 41.4] | 0.411 | 0.396 | 0.434 | 0.985 | 0.02 | 1.18 (1.18) | — |
| noul_ctx+true_count | 34.7 [30.3, 39.7] | 0.399 | 0.382 | 0.411 | 0.985 | 0.02 | 1.18 (1.18) | — |
| pick+count | 20.1 [16.1, 24.1] | 0.278 | 0.258 | 0.370 | 0.345 | 0.79 | 0.75 (1.18) | 4.323 |
| noul_ctx+count | 12.2 [9.2, 15.4] | 0.130 | 0.128 | 0.203 | 0.164 | 1.00 | 0.19 (1.18) | 4.986 |
| pick+dev_prior | 32.0 [27.8, 37.0] | 0.390 | 0.373 | 0.394 | 0.816 | 0.20 | 1.00 (1.18) | 2.773 |
| noul_ctx+dev_prior | 32.3 [28.0, 37.0] | 0.390 | 0.373 | 0.392 | 0.816 | 0.20 | 1.00 (1.18) | 3.436 |
| set@shipped | 17.6 [13.9, 21.6] | 0.427 | 0.355 | 0.407 | 0.323 | 1.10 | 2.18 (1.18) | 4.520 |
| set+platt | 18.9 [15.1, 22.8] | 0.215 | 0.208 | 0.307 | 0.303 | 0.82 | 0.38 (1.18) | 3.116 |
| set+true_count | 37.0 [32.5, 41.9] | 0.416 | 0.401 | 0.440 | 0.985 | 0.02 | 1.18 (1.18) | — |
| set+dev_prior | 32.3 [27.8, 37.0] | 0.393 | 0.375 | 0.396 | 0.816 | 0.20 | 1.00 (1.18) | 2.841 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 17.392 | 0.042 | 0.0 % | 0.0 % | 0.953 |
| noul_ctx+platt | 4.341 | 0.430 | 0.0 % | 0.0 % | 1.000 |
| pick+count | 4.323 | 0.117 | 5.0 % | 2.3 % | 0.627 |
| noul_ctx+count | 4.986 | 0.071 | 0.0 % | 0.0 % | 0.873 |
| pick+dev_prior | 2.773 | 0.049 | 5.3 % | 5.0 % | 0.494 |
| noul_ctx+dev_prior | 3.436 | 0.199 | 0.0 % | 0.0 % | 0.600 |
| set@shipped | 4.520 | 0.043 | 4.0 % | 1.3 % | 0.639 |
| set+platt | 3.116 | 0.150 | 0.0 % | 0.0 % | 0.670 |
| set+dev_prior | 2.841 | 0.110 | 5.0 % | 0.0 % | 0.492 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -19.35 pts [-23.33, -15.63] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | -0.50 pts [-1.74, +0.50] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +14.64 pts [+10.67, +18.86] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +33.00 pts [+28.54, +37.97] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +1.74 pts [-0.74, +4.47] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +4.47 pts [+2.48, +6.45] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -16.38 pts [-20.10, -12.90] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -4.47 pts [-6.45, -2.48] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +8.68 pts [+4.96, +12.41] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -12.41 nats [-13.53, -11.32] |

## hellaswag (dev 102, test 198, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 77.8 [72.2, 83.3] | 0.778 | 0.778 | 0.778 | 1.000 | 0.00 | 1.00 (1.00) | 0.595 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 0.595 | 0.055 | 68.2 % | 40.9 % | 0.083 |

## mmlu_pro (dev 89, test 211, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 42.2 [35.5, 48.8] | 0.422 | 0.422 | 0.422 | 1.000 | 0.00 | 1.00 (1.00) | 1.781 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.781 | 0.128 | 9.5 % | 5.2 % | 0.404 |

## nlupp (dev 176, test 424, failed 600)

> **WARNING: 600 items failed (100 %)** and count as wrong. First error: `'noul'`. Re-run the readout to retry them.

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|

## sata (dev 513, test 1137, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 16.1 [14.0, 18.2] | 0.659 | 0.544 | 0.673 | 0.216 | 2.03 | 3.79 (3.60) | 4.868 |
| noul_ctx+platt | 16.2 [14.1, 18.5] | 0.647 | 0.535 | 0.668 | 0.219 | 1.97 | 3.32 (3.60) | 4.807 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 3.60 | 0.00 (3.60) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.453 | 0.314 | 0.400 | 0.000 | 2.60 | 1.00 (3.60) | — |
| pick+true_count | 54.8 [51.9, 57.7] | 0.818 | 0.752 | 0.825 | 1.000 | 0.00 | 3.60 (3.60) | — |
| noul_ctx+true_count | 44.2 [41.3, 47.1] | 0.775 | 0.690 | 0.775 | 1.000 | 0.00 | 3.60 (3.60) | — |
| pick+count | 27.4 [24.9, 30.0] | 0.675 | 0.586 | 0.708 | 0.308 | 1.81 | 3.28 (3.60) | 3.903 |
| noul_ctx+count | 17.0 [14.8, 19.3] | 0.551 | 0.462 | 0.607 | 0.199 | 2.38 | 2.75 (3.60) | 4.644 |
| pick+dev_prior | 29.5 [26.9, 32.3] | 0.679 | 0.574 | 0.635 | 0.423 | 1.57 | 2.14 (3.60) | 3.710 |
| noul_ctx+dev_prior | 20.2 [17.9, 22.6] | 0.647 | 0.526 | 0.601 | 0.310 | 2.07 | 2.69 (3.60) | 4.450 |
| set@shipped | 27.4 [24.9, 30.2] | 0.702 | 0.601 | 0.695 | 0.322 | 1.65 | 2.68 (3.60) | 5.326 |
| set+platt | 31.8 [29.0, 34.6] | 0.756 | 0.659 | 0.735 | 0.372 | 1.56 | 3.69 (3.60) | 3.963 |
| set+true_count | 54.4 [51.4, 57.3] | 0.821 | 0.754 | 0.826 | 1.000 | 0.00 | 3.60 (3.60) | — |
| set+dev_prior | 30.3 [27.7, 33.2] | 0.689 | 0.585 | 0.645 | 0.423 | 1.56 | 2.15 (3.60) | 3.793 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 4.868 | 0.094 | 0.0 % | 0.0 % | 0.781 |
| noul_ctx+platt | 4.807 | 0.080 | 0.0 % | 0.0 % | 0.768 |
| pick+count | 3.903 | 0.083 | 0.0 % | 0.0 % | 0.597 |
| noul_ctx+count | 4.644 | 0.075 | 0.0 % | 0.0 % | 0.785 |
| pick+dev_prior | 3.710 | 0.136 | 15.2 % | 4.5 % | 0.426 |
| noul_ctx+dev_prior | 4.450 | 0.109 | 0.0 % | 0.0 % | 0.658 |
| set@shipped | 5.326 | 0.112 | 0.0 % | 0.0 % | 0.515 |
| set+platt | 3.963 | 0.124 | 7.1 % | 0.4 % | 0.431 |
| set+dev_prior | 3.793 | 0.137 | 16.3 % | 4.7 % | 0.425 |

SATA-Bench's own metrics (its definitions: EM leaves out empty answers; RStd = spread of recall across option positions).

| predictor | EM % | JI % | CtDif | CtDifAbs | RStd | empty answers |
|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 16.9 | 54.4 | +0.18 | 2.03 | 11.0 | 51 |
| noul_ctx+platt | 17.2 | 53.5 | -0.28 | 1.97 | 10.8 | 69 |
| always_none | 0.0 | 0.0 | -3.60 | 3.60 | 0.0 | 1137 |
| pick@top1 | 0.0 | 31.4 | -2.60 | 2.60 | 9.6 | 0 |
| pick+true_count | 54.8 | 75.2 | +0.00 | 0.00 | 6.2 | 0 |
| noul_ctx+true_count | 44.2 | 69.0 | +0.00 | 0.00 | 5.8 | 0 |
| pick+count | 30.3 | 58.6 | -0.32 | 1.81 | 7.2 | 106 |
| noul_ctx+count | 21.5 | 46.2 | -0.85 | 2.38 | 8.7 | 241 |
| pick+dev_prior | 29.5 | 57.4 | -1.47 | 1.57 | 14.2 | 0 |
| noul_ctx+dev_prior | 20.2 | 52.6 | -0.92 | 2.07 | 15.7 | 0 |
| set@shipped | 28.0 | 60.1 | -0.92 | 1.65 | 13.1 | 24 |
| set+platt | 31.9 | 65.9 | +0.09 | 1.56 | 11.9 | 4 |
| set+true_count | 54.4 | 75.4 | +0.00 | 0.00 | 5.6 | 0 |
| set+dev_prior | 30.3 | 58.5 | -1.45 | 1.56 | 14.3 | 0 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -26.91 pts [-29.64, -24.36] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.44 pts [-0.88, +1.76] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +2.90 pts [+0.62, +5.28] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +38.61 pts [+35.80, +41.42] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +10.55 pts [+8.27, +13.02] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +54.79 pts [+51.89, +57.70] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -27.35 pts [-29.99, -24.71] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -25.33 pts [-28.06, -22.78] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +0.88 pts [-1.23, +2.99] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.22 nats [-0.30, -0.16] |

## sst5 (dev 88, test 212, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.000 | 1.00 | 0.00 (1.00) | — |
| native@top1 | 50.5 [43.9, 57.5] | 0.505 | 0.505 | 0.505 | 1.000 | 0.00 | 1.00 (1.00) | 1.147 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| native@top1 | 1.147 | 0.131 | 0.5 % | 0.5 % | 0.511 |

## synthetic (dev 95, test 205, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 69.3 [62.9, 75.6] | 0.916 | 0.876 | 0.929 | 0.717 | 0.35 | 2.87 (2.79) | 1.362 |
| noul_ctx+platt | 70.7 [64.4, 77.1] | 0.920 | 0.883 | 0.933 | 0.727 | 0.33 | 2.70 (2.79) | 0.887 |
| always_none | 4.4 [2.0, 7.3] | 0.044 | 0.044 | 0.000 | 0.044 | 2.79 | 0.00 (2.79) | — |
| pick@top1 | 19.5 [13.7, 24.9] | 0.567 | 0.449 | 0.505 | 0.195 | 1.88 | 1.00 (2.79) | — |
| pick+true_count | 98.5 [96.6, 100.0] | 0.996 | 0.994 | 0.995 | 1.000 | 0.00 | 2.79 (2.79) | — |
| noul_ctx+true_count | 94.6 [91.2, 97.6] | 0.982 | 0.973 | 0.981 | 1.000 | 0.00 | 2.79 (2.79) | — |
| pick+count | 79.0 [73.2, 84.4] | 0.957 | 0.934 | 0.961 | 0.795 | 0.21 | 2.81 (2.79) | 1.119 |
| noul_ctx+count | 78.0 [72.2, 83.9] | 0.956 | 0.931 | 0.957 | 0.785 | 0.22 | 2.67 (2.79) | 1.306 |
| pick+dev_prior | 69.3 [62.9, 75.6] | 0.850 | 0.814 | 0.854 | 0.693 | 0.75 | 2.35 (2.79) | 1.930 |
| noul_ctx+dev_prior | 56.6 [49.8, 63.4] | 0.798 | 0.745 | 0.805 | 0.566 | 1.02 | 2.46 (2.79) | 2.117 |
| set@shipped | 65.9 [59.5, 72.2] | 0.923 | 0.882 | 0.916 | 0.659 | 0.42 | 2.40 (2.79) | 0.872 |
| set+platt | 90.2 [85.9, 94.1] | 0.971 | 0.962 | 0.981 | 0.902 | 0.11 | 2.78 (2.79) | 0.395 |
| set+true_count | 98.5 [96.6, 100.0] | 0.996 | 0.993 | 0.995 | 1.000 | 0.00 | 2.79 (2.79) | — |
| set+dev_prior | 63.9 [57.1, 70.2] | 0.858 | 0.813 | 0.861 | 0.639 | 0.72 | 2.41 (2.79) | 1.886 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 1.362 | 0.318 | 39.5 % | 31.7 % | 0.139 |
| noul_ctx+platt | 0.887 | 0.050 | 49.3 % | 33.2 % | 0.119 |
| pick+count | 1.119 | 0.377 | 35.6 % | 30.2 % | 0.107 |
| noul_ctx+count | 1.306 | 0.407 | 29.8 % | 23.4 % | 0.121 |
| pick+dev_prior | 1.930 | 0.518 | 2.0 % | 2.0 % | 0.171 |
| noul_ctx+dev_prior | 2.117 | 0.397 | 0.5 % | 0.5 % | 0.374 |
| set@shipped | 0.872 | 0.129 | 63.4 % | 49.3 % | 0.097 |
| set+platt | 0.395 | 0.039 | 100.0 % | 84.4 % | 0.021 |
| set+dev_prior | 1.886 | 0.450 | 2.0 % | 2.0 % | 0.256 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -32.68 pts [-39.02, -25.85] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.00 pts [-1.46, +1.46] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | -1.95 pts [-8.78, +4.39] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +27.80 pts [+21.46, +34.15] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +3.90 pts [+0.49, +7.80] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +79.02 pts [+73.66, +84.88] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -19.51 pts [-24.89, -14.15] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -29.27 pts [-35.61, -22.93] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +8.78 pts [+2.44, +15.12] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -0.06 nats [-0.18, +0.07] |

## unfair_tos (dev 234, test 566, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul_ctx@0.5 | 70.5 [66.8, 74.2] | 0.738 | 0.725 | 0.154 | 0.710 | 1.27 | 1.39 (0.13) | 2.583 |
| noul_ctx+platt | 89.6 [87.1, 92.0] | 0.896 | 0.896 | 0.333 | 0.896 | 0.11 | 0.04 (0.13) | 0.355 |
| always_none | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | — |
| pick@top1 | 10.4 [8.0, 12.9] | 0.110 | 0.109 | 0.201 | 0.110 | 0.89 | 1.00 (0.13) | — |
| pick+true_count | 99.1 [98.2, 99.8] | 0.993 | 0.992 | 0.931 | 1.000 | 0.00 | 0.13 (0.13) | — |
| noul_ctx+true_count | 98.8 [97.9, 99.6] | 0.991 | 0.990 | 0.903 | 1.000 | 0.00 | 0.13 (0.13) | — |
| pick+count | 74.9 [71.0, 78.4] | 0.771 | 0.766 | 0.460 | 0.751 | 0.27 | 0.38 (0.13) | 0.895 |
| noul_ctx+count | 83.7 [80.7, 86.7] | 0.849 | 0.846 | 0.522 | 0.841 | 0.18 | 0.27 (0.13) | 0.974 |
| pick+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.455 |
| noul_ctx+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.534 |
| set@shipped | 74.0 [70.3, 77.6] | 0.756 | 0.753 | 0.453 | 0.742 | 0.27 | 0.38 (0.13) | 0.736 |
| set+platt | 88.3 [85.9, 91.0] | 0.887 | 0.886 | 0.370 | 0.883 | 0.12 | 0.06 (0.13) | 0.277 |
| set+true_count | 98.8 [97.9, 99.6] | 0.990 | 0.989 | 0.903 | 1.000 | 0.00 | 0.13 (0.13) | — |
| set+dev_prior | 88.2 [85.5, 90.8] | 0.882 | 0.882 | 0.000 | 0.882 | 0.13 | 0.00 (0.13) | 0.455 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul_ctx@0.5 | 2.583 | 0.308 | 76.9 % | 70.0 % | 0.056 |
| noul_ctx+platt | 0.355 | 0.034 | 97.5 % | 87.3 % | 0.015 |
| pick+count | 0.895 | 0.147 | 64.8 % | 58.7 % | 0.071 |
| noul_ctx+count | 0.974 | 0.307 | 88.7 % | 74.9 % | 0.031 |
| pick+dev_prior | 0.455 | 0.046 | 48.2 % | 0.7 % | 0.103 |
| noul_ctx+dev_prior | 0.534 | 0.046 | 48.2 % | 0.7 % | 0.103 |
| set@shipped | 0.736 | 0.115 | 51.6 % | 38.3 % | 0.102 |
| set+platt | 0.277 | 0.028 | 97.2 % | 86.0 % | 0.017 |
| set+dev_prior | 0.455 | 0.046 | 48.2 % | 0.7 % | 0.103 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -24.73 pts [-28.45, -21.38] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.35 pts [+0.00, +0.88] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | +14.13 pts [+9.89, +18.90] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx+platt | +9.54 pts [+7.24, +11.84] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.35 pts [+0.00, +0.88] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +88.69 pts [+86.04, +91.34] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -24.20 pts [-27.92, -20.85] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -10.95 pts [-13.43, -8.30] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | +13.25 pts [+10.42, +16.25] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | -1.61 nats [-1.83, -1.38] |

## wide (dev 85, test 215, failed 0)

| predictor | exact-set % [95% CI] | example F1 | Jaccard | micro F1 | count acc | count error | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|---|---|
| noul@0.5 | 98.1 [96.3, 99.5] | 0.996 | 0.994 | 0.996 | 0.981 | 0.02 | 2.46 (2.44) | 4.432 |
| noul+platt | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | 0.001 |
| always_none | 7.0 [3.7, 10.7] | 0.070 | 0.070 | 0.000 | 0.070 | 2.44 | 0.00 (2.44) | — |
| pick@top1 | 23.7 [18.6, 29.3] | 0.591 | 0.482 | 0.541 | 0.237 | 1.58 | 1.00 (2.44) | — |
| pick+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | — |
| noul+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | — |
| pick+count | 78.1 [72.6, 83.3] | 0.914 | 0.891 | 0.945 | 0.781 | 0.28 | 2.60 (2.44) | 2.341 |
| noul+count | 93.5 [89.8, 96.3] | 0.966 | 0.961 | 0.982 | 0.935 | 0.09 | 2.43 (2.44) | 2.323 |
| pick+dev_prior | 72.1 [66.0, 77.7] | 0.773 | 0.759 | 0.747 | 0.721 | 1.00 | 1.53 (2.44) | 2.620 |
| set@shipped | 96.3 [93.5, 98.6] | 0.981 | 0.978 | 0.992 | 0.963 | 0.04 | 2.48 (2.44) | 0.715 |
| set+platt | 99.5 [98.6, 100.0] | 0.998 | 0.998 | 0.999 | 0.995 | 0.00 | 2.45 (2.44) | 0.088 |
| set+true_count | 100.0 [100.0, 100.0] | 1.000 | 1.000 | 1.000 | 1.000 | 0.00 | 2.44 (2.44) | — |
| set+dev_prior | 75.3 [69.8, 80.9] | 0.812 | 0.797 | 0.811 | 0.753 | 0.80 | 1.79 (2.44) | 2.396 |

Set probabilities (predictors that give one): calibration error of the predicted set's probability (0 = honest), and selective automation: share of items answerable at 90 % / 95 % exact-set accuracy, area under the risk-coverage curve (lower is better).

| predictor | set log-loss | calibration error | answerable @90 % | answerable @95 % | risk-coverage area |
|---|---|---|---|---|---|
| noul@0.5 | 4.432 | 0.792 | 100.0 % | 100.0 % | 0.006 |
| noul+platt | 0.001 | 0.001 | 100.0 % | 100.0 % | 0.000 |
| pick+count | 2.341 | 0.564 | 47.0 % | 21.4 % | 0.119 |
| noul+count | 2.323 | 0.737 | 100.0 % | 97.7 % | 0.020 |
| pick+dev_prior | 2.620 | 0.613 | 53.5 % | 22.3 % | 0.111 |
| set@shipped | 0.715 | 0.342 | 100.0 % | 100.0 % | 0.004 |
| set+platt | 0.088 | 0.009 | 100.0 % | 100.0 % | 0.001 |
| set+dev_prior | 2.396 | 0.637 | 59.1 % | 5.6 % | 0.119 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| V1 native set as shipped vs its ranking + true count | set@shipped − set+true_count | -3.72 pts [-6.51, -1.40] |
| V2 Choice ranking vs native-set ranking (both told the count) | pick+true_count − set+true_count | +0.00 pts [+0.00, +0.00] |
| V3 dataset count prior on native-set scores vs shipped threshold | set+dev_prior − set@shipped | -20.93 pts [-26.98, -14.88] |
| G1 ranking+true count vs best yes/no | pick+true_count − noul+platt | +0.00 pts [+0.00, +0.00] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +76.28 pts [+70.70, +81.40] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -21.86 pts [-27.44, -16.74] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | -27.91 pts [-33.95, -22.31] |
