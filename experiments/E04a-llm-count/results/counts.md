## Counts without labels (test split)

Asked: the model's answer to "how many of these options apply?" (expected value; exactly right = its most likely count is the gold count). Summed yes/no: the sum of its per-option yes probabilities (exactly right = the number of options above 0.5 is the gold count). Written: the number of letters it wrote (a few generated tokens, not one pass; unparsed answers count as wrong). Rank corr: Spearman with the gold count.

| track | model | test | gold mean | asked: mean / rank corr / exactly right | summed yes/no: mean / rank corr / exactly right | written: mean / rank corr / exactly right |
|---|---|---|---|---|---|---|
| sata | qwen3.6-27b | 1137 | 3.60 | 2.50 / +0.67 / 15.1 % | 3.18 / +0.75 / 36.8 % | 3.02 / +0.70 / 41.7 % (0 % unparsed) |
| sata | nox-4b | 1137 | 3.60 | 3.31 / +0.72 / 35.5 % | 3.32 / +0.72 / 34.3 % | – |
| nlupp | qwen3.6-27b | 424 | 1.93 | 1.34 / +0.77 / 35.4 % | 2.41 / +0.75 / 51.4 % | 1.78 / +0.75 / 54.2 % (0 % unparsed) |
| nlupp | nox-4b | 424 | 1.93 | 8.85 / -0.38 / 45.8 % | 10.80 / +0.53 / 12.5 % | – |
| ecthr | qwen3.6-27b | 217 | 1.09 | 1.23 / +0.45 / 61.3 % | 1.52 / +0.47 / 64.5 % | 1.52 / +0.36 / 56.2 % (0 % unparsed) |
| ecthr | nox-4b | 217 | 1.09 | 2.45 / +0.24 / 22.6 % | 2.66 / +0.19 / 39.2 % | – |
| unfair_tos | qwen3.6-27b | 566 | 0.13 | 0.42 / +0.46 / 74.4 % | 0.46 / +0.44 / 71.0 % | 0.44 / +0.45 / 69.3 % (0 % unparsed) |
| unfair_tos | nox-4b | 566 | 0.13 | 1.61 / +0.27 / 62.7 % | 1.78 / +0.36 / 52.3 % | – |
| synthetic | qwen3.6-27b | 205 | 2.79 | 2.66 / +0.96 / 82.4 % | 2.74 / +0.98 / 93.2 % | 2.72 / +0.98 / 92.7 % (0 % unparsed) |

## Bar wording: the same options asked strictly and loosely (all pairs: the loose answer has more options)

| source | model | pairs | gold count strict → loose | asked count strict → loose (moved ≥ 1 the right way) | summed yes/no strict → loose (moved ≥ 1 the right way) | written strict → loose (moved ≥ 1 the right way) | exact set, strict / loose: asked count | same: summed yes/no | same: written |
|---|---|---|---|---|---|---|---|---|---|
| wands | qwen3.6-27b | 150 | 1.03 → 6.64 | 0.77 → 3.25 (79 %) | 0.92 → 3.78 (87 %) | 0.97 → 4.57 (78 %) | 56.7 / 20.0 | 59.3 / 11.3 | 56.0 / 28.7 |
| esci | qwen3.6-27b | 150 | 3.93 → 7.27 | 1.74 → 3.26 (61 %) | 2.22 → 3.86 (63 %) | 2.37 → 4.13 (53 %) | 14.7 / 17.3 | 22.0 / 7.3 | 26.7 / 10.7 |
