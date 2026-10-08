| track | test | gold size (share empty) | ours E[size] / mode size / mean P(0) | ours ranking + true count | base Choice + true count | ours ranking + dev count prior: exact / log-loss | count ↔ gold rank corr: ours / base 'how many' / base Σ yes-no | 'none' AUC: ours P(0) / base 1 − max yes-no |
|---|---|---|---|---|---|---|---|---|
| ecthr | 217 | 1.09 (0.12) | 1.40 / 1.08 / 0.03 | 62.2 | 64.5 | 38.7 / 2.25 | +0.07 / +0.04 / +0.02 | 0.43 / 0.45 |
| nlupp | 424 | 1.93 (0.14) | 1.02 / 0.90 / 0.13 | 54.0 | 53.1 | 31.6 / 3.96 | +0.52 / +0.22 / +0.28 | 0.95 / 0.92 |
| sata | 1137 | 3.60 (0.00) | 2.01 / 1.93 / 0.01 | 35.9 | 36.1 | 20.0 / 4.54 | -0.08 / +0.67 / +0.59 | nan / nan |
| unfair_tos | 566 | 0.13 (0.88) | 1.29 / 1.07 / 0.04 | 98.2 | 97.9 | 88.2 / 0.48 | +0.16 / +0.18 / +0.19 | 0.86 / 0.88 |
| goemotions | 403 | 1.18 (0.00) | 1.03 / 1.01 / 0.12 | 58.1 | 28.8 | 51.4 / 2.02 | +0.08 / +0.09 / +0.08 | nan / nan |
| synthetic | 205 | 2.79 (0.04) | 2.75 / 2.75 / 0.07 | 100.0 | 89.3 | 66.8 / 1.83 | +0.96 / +0.77 / +0.84 | 1.00 / 1.00 |
