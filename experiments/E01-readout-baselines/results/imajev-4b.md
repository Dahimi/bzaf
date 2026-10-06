# E01 readout scores — imajev-4b

## goemotions (dev 133, test 267)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|

## sata (dev 122, test 278)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
| noul@0.5 | 1.4 [0.4, 2.9] | 0.020 | 0.022 | 0.014 | 1.71 (3.58) | 1.607 |
| noul+platt | 1.4 [0.4, 2.9] | 0.020 | 0.022 | 0.014 | 1.71 (3.58) | 5.069 |
| noul_ctx@0.5 | 1.8 [0.4, 3.6] | 0.023 | 0.026 | 0.018 | 2.00 (3.58) | 1.156 |
| noul_ctx+platt | 1.4 [0.4, 2.9] | 0.021 | 0.022 | 0.018 | 1.71 (3.58) | 1.433 |
| always_none | 0.0 [0.0, 0.0] | 0.000 | 0.000 | 0.000 | 0.00 (3.58) | — |
| pick@top1 | 0.0 [0.0, 0.0] | 0.017 | 0.014 | 0.000 | 1.00 (3.58) | — |
| pick+true_count | 2.5 [0.7, 4.3] | 0.025 | 0.028 | 0.025 | 2.00 (3.58) | — |
| noul+true_count | 2.5 [0.7, 4.3] | 0.025 | 0.028 | 0.025 | 2.00 (3.58) | — |
| noul_ctx+true_count | 2.2 [0.7, 4.0] | 0.023 | 0.026 | 0.025 | 2.00 (3.58) | — |
| pick+count | 0.7 [0.0, 1.8] | 0.017 | 0.016 | 0.007 | 1.14 (3.58) | 1.234 |
| noul+count | 1.1 [0.0, 2.5] | 0.018 | 0.018 | 0.011 | 1.29 (3.58) | 1.174 |
| noul_ctx+count | 1.1 [0.0, 2.5] | 0.018 | 0.018 | 0.011 | 1.29 (3.58) | 1.317 |
| pick+dev_prior | 2.5 [0.7, 4.3] | 0.025 | 0.028 | 0.025 | 2.00 (3.58) | 0.952 |
| noul_ctx+dev_prior | 2.2 [0.7, 4.0] | 0.023 | 0.026 | 0.025 | 2.00 (3.58) | 1.035 |

| signal | a − b | mean [95% CI] |
|---|---|---|
| G1 ranking+true count vs best yes/no | pick+true_count − noul_ctx@0.5 | +0.72 pts [+0.00, +1.80] |
| R1 Choice ranking vs yes/no ranking (both told the count) | pick+true_count − noul_ctx+true_count | +0.36 pts [+0.00, +1.08] |
| C1 value of the right count over top-1 | pick+true_count − pick@top1 | +2.52 pts [+0.72, +4.32] |
| S2 asked count vs true count (headroom) | pick+count − pick+true_count | -1.80 pts [-3.60, -0.36] |
| S5 dataset count prior vs true count (item-level counting headroom) | pick+dev_prior − pick+true_count | +0.00 pts [+0.00, +0.00] |
| S3 count dial on yes/no (ctx) | noul_ctx+count − noul_ctx@0.5 | -0.72 pts [-1.80, +0.00] |
| S4 options in context (yes/no) | noul_ctx@0.5 − noul@0.5 | +0.36 pts [+0.00, +1.08] |
| S3 count dial on yes/no (ctx), log-loss | noul_ctx+count − noul_ctx@0.5 | +0.16 nats [-0.13, +0.47] |

## synthetic (dev 95, test 205)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|

## unfair_tos (dev 234, test 566)

| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |
|---|---|---|---|---|---|---|
