# runs/e04a-qwen3.6-27b/bench − runs/e04a-qwen3.6-27b/bench: write vs pick+count,noul_ctx@0.5 (best per track), exact

| track | items | B's predictor | mean [95% CI] |
|---|---|---|---|
| ecthr | 217 | noul_ctx@0.5 | -6.91 [-11.98, -2.30] |
| nlupp | 424 | noul_ctx@0.5 | +1.18 [-2.59, +5.19] |
| sata | 1137 | noul_ctx@0.5 | +5.54 [+3.61, +7.65] |
| synthetic | 205 | noul_ctx@0.5 | -0.49 [-3.41, +2.93] |
| unfair_tos | 566 | pick+count | -4.59 [-6.54, -2.83] |
| **macro (ecthr, nlupp, sata, synthetic, unfair_tos)** | 5 tracks | | **-1.05** [-2.58, +0.45] |
