| track | test | gold size (share empty) | ours E[size] / mode size / mean P(0) | ours ranking + true count | base Choice + true count | ours ranking + dev count prior: exact / log-loss | count ↔ gold rank corr: ours / base 'how many' / base Σ yes-no | 'none' AUC: ours P(0) / base 1 − max yes-no |
|---|---|---|---|---|---|---|---|---|
| ecthr | 217 | 1.09 (0.12) | 1.07 / 0.41 / 0.42 | 77.0 | 77.4 | 56.2 / 1.75 | +0.18 / +0.16 / +0.12 | 0.58 / 0.62 |
| nlupp | 424 | 1.93 (0.14) | 0.95 / 0.70 / 0.39 | 62.3 | 62.3 | 34.0 / 3.39 | +0.58 / -0.34 / +0.53 | 0.98 / 0.95 |
| sata | 1137 | 3.60 (0.00) | 2.54 / 2.37 / 0.16 | 57.4 | 54.4 | 31.1 / 3.46 | +0.21 / +0.71 / +0.70 | nan / nan |
| unfair_tos | 566 | 0.13 (0.88) | 0.67 / 0.32 / 0.66 | 98.8 | 99.1 | 88.2 / 0.44 | +0.34 / +0.28 / +0.33 | 0.94 / 0.95 |
| goemotions | 403 | 1.18 (0.00) | 1.44 / 0.73 / 0.21 | 53.6 | 39.2 | 47.6 / 2.10 | +0.18 / -0.10 / -0.01 | nan / nan |
| synthetic | 205 | 2.79 (0.04) | 2.81 / 2.81 / 0.04 | 100.0 | 95.6 | 75.1 / 1.83 | +0.97 / +0.95 / +0.96 | 1.00 / 1.00 |
