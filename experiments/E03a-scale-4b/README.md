# E03a — E02b's recipe and data on Decision 2.0 Nox-4B

**Status:** pre-registered 2026-10-09, before any run ([D22](../../docs/decisions.md)) · **Compute:** Modal, one GPU
chosen by the speed test below · **Code:** unchanged from [E02b](../E02b-diverse-data/) except the base model

## Question

At 0.8B the count stayed a learned prior (E02: "always some", E02b: "none when unsure"), while the 0.8B base itself
barely judges options on unfamiliar tasks (SATA, own yes/no + Platt: 4.2 % exact; own "how many" question: 6.1 %). The
4B base does (30.0 % and 29.8 %). With everything else unchanged, does the count transfer to held-out families at 4B?

## Model and recipe

`vllm-sr/Decision-2.0-Nox-4B` through our Decision 2.0 adapter (checked first against the runtime's recorded answers,
as for Eos). Everything else exactly as E02b run A: `--mix e02b` (same sources, sizes, sampler, seed 0), count head,
LoRA r16 / α32 on every linear layer, learning rates 2e-4 / 5e-5 / 1e-3, one epoch, ≤ 16k padded tokens per batch,
bf16. Only engineering settings may differ, chosen by the speed test before the run (GPU type, gradient checkpointing
on or off); they change speed, not the model.

## Evaluation

Benchmark v0 in-process through the adapter. The base is E01b's readout of Nox-4B through the released runtime
(`runs/bench-v0/decision-2.0-nox-4b`; same benchmark files), so no base evaluation is run.

## Pre-registered decision rule

Held-out tracks H = {sata, nlupp, ecthr, unfair_tos}; B per track = the better on test of `noul_ctx+platt` and
`pick+dev_prior` of the 4B base (choosing on test favours the baseline).

**G2 (zero-shot, unchanged):** `ours@mode` − B, macro over H: exact-set CI above 0 and set log-loss CI below 0; general
track `native@top1`, ours − base, macro over 7 sets, at most 1 point lower.

**G2-cal (same information as B):** the same two comparisons with `ours+dev_prior`: our ranking and set distribution
with the count distribution taken from each track's labelled dev split, with the same add-one histogram
`pick+dev_prior` uses (no extra labels: B fits on the same dev items). Chosen from E02b's records over
`ours+dev_match`, which keeps the model's own count evidence: on E02b's records, − B, exact-set +2.8 [+1.3, +4.4] vs
+0.8 [−1.0, +2.6], log-loss +0.00 [−0.03, +0.03] vs +0.27 [+0.20, +0.33] (E02b would pass G2-cal's exact-set
condition, not its log-loss one).

- **G2 passes:** the count transfers zero-shot at 4B. Next: E03b, data v1 on top (more families), toward v0.1.
- **G2 fails, G2-cal passes:** the model is better than the baselines given the same few labels; zero-shot counting is
  still open. Next: E03b with data v1; the zero-shot question is decided there.
- **Both fail on exact-set and log-loss:** the count needs a different method, not more data or scale. Next: an
  adaptive threshold (a learned "threshold" option scored like the others; options above it are chosen), before more
  data spend.
- **General track more than 1 point lower:** raise the distillation weight or lower the LoRA learning rate, one rerun.

Reported, no decision attached: E03a − E02b (the effect of scale, same data); ranking with the true count against the
base (selection transfer); against the base's label-free predictors; `ours+dev_match` and the 16- and 64-label versions
of `ours+dev_prior` (how many labels a user would need); SATA by subset and every held-out track by gold count;
in-domain tracks; order stability.

## Commands

```bash
# 1. adapter check on the real 4B weights (CPU FP32 must agree to 1e-4; GPU within the runtime's CPU-ROCm spread)
BZAF_FLA=0 uv run modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Nox-4B --checks cpu
uv run modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Nox-4B --checks cuda,cuda-bf16
# 2. speed test, 40 steps each, no evaluation (~10 min, < $1 each); compare recent_tokens_per_s per dollar
A="--base vllm-sr/Decision-2.0-Nox-4B --mix e02b --scale 0.05 --max-steps 40 --eval-tracks none"
uv run modal run cloud/train_modal.py --name speed-l40s --args "$A"
BZAF_GPU=H100 uv run modal run cloud/train_modal.py --name speed-h100 --args "$A"
BZAF_GPU=H100 uv run modal run cloud/train_modal.py --name speed-h100-nockpt --args "$A --no-grad-checkpointing"
# 3. the run (GPU and checkpointing per the speed test)
BZAF_GPU=H100 uv run modal run --detach cloud/train_modal.py --name e03a --args "--base vllm-sr/Decision-2.0-Nox-4B --mix e02b"
# 4. results
modal volume get bzaf-runs e03a runs/
R=experiments/E03a-scale-4b/results; H=sata,nlupp,ecthr,unfair_tos; BASE=runs/bench-v0/decision-2.0-nox-4b; mkdir -p $R
uv run bzaf bench score runs/e03a/eval/ours --out $R/ours
for P in ours@mode ours+dev_prior; do for M in per_item_exact per_item_nll; do
  uv run bzaf bench compare runs/e03a/eval/ours $BASE --predictor $P --predictor-b noul_ctx+platt,pick+dev_prior \
    --only $H --metric $M > $R/g2-$P-$M.md; done; done
uv run bzaf bench compare runs/e03a/eval/ours $BASE --predictor native@top1 > $R/g2-general.md
uv run bzaf bench compare runs/e03a/eval/ours runs/e02b/eval/ours --predictor ours@mode --only $H > $R/vs-e02b-exact.md
uv run python experiments/E02-count-head/diagnose.py runs/e03a/eval/ours $BASE > $R/diagnosis.md
uv run python experiments/E02b-diverse-data/breakdown.py $BASE e02b=runs/e02b/eval/ours e03a=runs/e03a/eval/ours > $R/breakdown.md
cp runs/e03a/train_log.jsonl runs/e03a/config.json runs/e03a/mixture_stats.json $R/
COPYFILE_DISABLE=1 tar czf $R/eval-records.tgz -C runs/e03a eval
```

## Checks before the run (2026-10-09)

- **Adapter on Nox-4B** (revision 25e8f67), the runtime's recorded answers: CPU FP32 max |diff| 1.1e-7 (criterion
  1e-4: passes); GPU FP32 2.1e-4 and bf16 2.7e-3, the same size as Eos (2.7e-4, 2.1e-3), i.e. kernel numerics.
- **Speed** (40 steps of the E02b mixture at 5 %, tokens per second over the last 10-step windows; early steps include
  kernel tuning): L40S ~1.4–1.8k; H100 ~2.7–4.4k; H100 without gradient checkpointing runs out of memory (80 GB).
  H100 is about twice as fast for about twice the price per hour, so similar cost and half the time: **chosen H100,
  gradient checkpointing on.** Expected ~50M tokens → ~4 h of training plus evaluation, about $18–22.

## Results

Run 2026-10-09/10 on one H100: 3,453 steps, the E02b mixture unchanged, 6.4k tokens/s. Files in [results/](results/)
(`vs-e02b-exact.md` and `breakdown.md` came out empty: the E02b records were not on the machine that scored).

### G2 and G2-cal: both failed; the general track also failed (to verify)

| condition | `ours@mode` (zero-shot) | `ours+dev_prior` (calibrated) |
|---|---|---|
| exact-set − B, macro over H | **−11.1** [−13.6, −8.8] | **+0.2** [−1.8, +2.3]: ECtHR +6.0 [+0.0, +11.5], SATA +1.2, NLU++ −2.1, UNFAIR-ToS −4.2 |
| set log-loss − B, macro over H | **+0.50** [+0.43, +0.57] | **+0.09** [+0.04, +0.14] |
| general track `native@top1` − base, macro | **−3.3** [−4.9, −1.8]: MMLU-Pro −10.9, CLINC150 −10.0, others within ±3.6 | (same) |

The general-track base here is E01b's readout through the released runtime, while ours is evaluated in-process; at
0.8B both sides were in-process and nothing regressed. Before acting on condition 3, the base is to be evaluated
in-process on the general track (one cheap run); the two losing tracks are the ones with the longest option lists.

### What scale changed, and what it did not

| held-out track, exact-set % | E02b (0.8B) | E03a (4B) | 4B base, label-free `pick+count` | 4B base, best label-free | B (4B) |
|---|---|---|---|---|---|
| SATA | 7.6 | **23.0** | 29.8 | 29.8 | 30.0 |
| NLU++ | 21.5 | **30.9** | 38.2 | 38.2 | 35.8 |
| ECtHR | 13.4 | **25.8** | 19.8 | 57.6 (`pick@top1`) | 50.7 |
| UNFAIR-ToS | 88.3 | **84.6** | 69.6 | 72.8 | 92.4 |

1. **Scale helped a lot zero-shot** (SATA ×3, ECtHR ×2), but the 4B baselines rose as much.
2. **The trained model is worse than the untrained 4B base's own two-question answer** (Choice ranking plus its native
   "how many" question) on SATA (−6.8) and NLU++ (−7.3), though better on UNFAIR-ToS (+15) and ECtHR (+6).
3. **Why: our count head does not use what the 4B base already knows.** Rank correlation of the predicted count with
   the gold count on SATA: our count head +0.21; the base's own "how many" question +0.71; the sum of its yes/no
   answers +0.70. On NLU++: ours +0.58, the base's yes/no sum +0.53. The count head is a new layer trained from zero on
   our families; the base's count knowledge lives in its pretrained candidate head, which the multi question never
   asks for a count.
4. **Selection is at the base's level** (ranking with the true count: SATA 57.4 vs 54.4, ECtHR 77.0 vs 77.4, NLU++
   62.3 vs 62.3), and the model still answers "none" when unsure (mean P(0): ECtHR 0.42, NLU++ 0.39, UNFAIR-ToS 0.66).
5. **Calibration with labels** helps (SATA 31.2, ECtHR 56.7 with the dev count histogram) but only ties the 4B
   baselines, which also got much better with labels (per-option yes/no + Platt). With 16 labels it is worse than with
   none on SATA and NLU++ (13.0, 15.6): the histogram of 16 items is too noisy.

**Reading:** the bottleneck is not model size or data alone but where the count comes from. The pre-registered branch
("both fail: the count needs a different method") applies; the evidence points to taking the count from the
pretrained head (which already counts well at 4B) rather than from a new head, and to protecting many-option Choice.
