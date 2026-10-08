| track | test | gold size (share empty) | ours E[size] / mode size / mean P(0) | ours ranking + true count | base Choice + true count | ours ranking + dev count prior: exact / log-loss | count ↔ gold rank corr: ours / base 'how many' / base Σ yes-no | 'none' AUC: ours P(0) / base 1 − max yes-no |
|---|---|---|---|---|---|---|---|---|
| ecthr | 217 | 1.09 (0.12) | 0.88 / 0.21 / 0.39 | 62.2 | 64.5 | 37.8 / 2.22 | +0.09 / +0.04 / +0.02 | 0.43 / 0.45 |
| nlupp | 424 | 1.93 (0.14) | 1.35 / 0.94 / 0.23 | 54.5 | 53.1 | 28.8 / 4.00 | +0.54 / +0.22 / +0.28 | 0.95 / 0.92 |
| sata | 1137 | 3.60 (0.00) | 2.30 / 2.10 / 0.16 | 37.7 | 36.1 | 21.1 / 4.32 | +0.10 / +0.67 / +0.59 | nan / nan |
| unfair_tos | 566 | 0.13 (0.88) | 0.68 / 0.21 / 0.49 | 98.1 | 97.9 | 88.2 / 0.47 | +0.19 / +0.18 / +0.19 | 0.91 / 0.88 |
| goemotions | 403 | 1.18 (0.00) | 1.10 / 0.56 / 0.23 | 57.1 | 28.8 | 49.6 / 2.01 | +0.05 / +0.09 / +0.08 | nan / nan |
| synthetic | 205 | 2.79 (0.04) | 2.79 / 2.80 / 0.04 | 100.0 | 89.3 | 66.3 / 1.83 | +0.97 / +0.77 / +0.84 | 1.00 / 1.00 |
