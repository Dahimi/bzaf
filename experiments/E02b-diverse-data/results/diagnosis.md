| track | test | gold size (share empty) | ours E[size] / mode size / mean P(0) | ours ranking + true count | base Choice + true count | ours ranking + dev count prior: exact / log-loss | count ↔ gold rank corr: ours / base 'how many' / base Σ yes-no | 'none' AUC: ours P(0) / base 1 − max yes-no |
|---|---|---|---|---|---|---|---|---|
| ecthr | 217 | 1.09 (0.12) | 1.00 / 0.08 / 0.50 | 61.3 | 64.5 | 39.6 / 2.27 | -0.05 / -0.07 / -0.05 | 0.48 / 0.45 |
| nlupp | 424 | 1.93 (0.14) | 0.65 / 0.33 / 0.55 | 51.9 | 53.1 | 34.4 / 4.18 | +0.50 / +0.25 / +0.31 | 0.97 / 0.92 |
| sata | 1137 | 3.60 (0.00) | 2.68 / 2.38 / 0.25 | 44.8 | 36.1 | 24.9 / 4.33 | +0.03 / +0.64 / +0.55 | nan / nan |
| unfair_tos | 566 | 0.13 (0.88) | 0.46 / 0.14 / 0.68 | 98.6 | 97.9 | 88.2 / 0.47 | +0.16 / +0.18 / +0.18 | 0.88 / 0.88 |
| goemotions | 403 | 1.18 (0.00) | 1.35 / 0.45 / 0.26 | 55.3 | 28.8 | 47.9 / 2.15 | +0.09 / +0.09 / +0.05 | nan / nan |
| synthetic | 205 | 2.79 (0.04) | 2.80 / 2.80 / 0.04 | 100.0 | 89.3 | 70.2 / 1.83 | +0.96 / +0.76 / +0.83 | 1.00 / 1.00 |
