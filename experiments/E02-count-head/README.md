# E02 — Count head on Decision 2.0 Eos-0.8B

**Status:** pre-registered (revised 2026-10-08, before any run: base moved from Kev-0.8B to Eos-0.8B, [D20](../../docs/decisions.md);
evaluation moved to [benchmark v0](../../docs/benchmark.md)) · **Compute:** Modal, one L40S · **Code:** [`src/bzaf/train/`](../../src/bzaf/train/)

## Question

Does a trained count head on top of Decision 2.0's per-option scores give better answer sets than every untrained
strategy, on task families it never saw, without losing the base's general decision quality?

## Model

`vllm-sr/Decision-2.0-Eos-0.8B` (Qwen3.5-0.8B backbone + shared candidate head), the smallest model of the Nox-4B
family, loaded by our Decision 2.0 adapter ([decision2.py](../../src/bzaf/train/decision2.py)). Checks before training:

- **parity:** on the runtime's own random-weight test package, our adapter gives the same answers as the released
  runtime, to ~1e-17 (`tests/test_decision2_parity.py`);
- **real weights:** our adapter on the runtime's readiness request against its recorded answers for Eos-0.8B
  (`modal run cloud/train_modal.py::golden`); must agree to 1e-4 in FP32 before any training run.
  *Clarified 2026-10-08 after the first check, before any training:* the recorded answers are CPU FP32. On an L40S in
  FP32 our adapter differs by at most 2.7e-4 (bf16: 2.1e-3); the runtime's own recorded CPU and ROCm answers for Eos
  differ by up to 1.5e-3, so GPU kernels alone account for this size of difference (a rendering or head error would
  be ~1e-1). The 1e-4 criterion now applies to CPU FP32, the reference's own setting; GPU runs must stay within the
  runtime's CPU–ROCm spread.

Added and trained:

- a new question type, `multi`: the Decision 2.0 prompt with type name `multi` and the suffix "Select every option
  supported by the context and instructions." (the base never saw it);
- **count head:** LayerNorm → 256 → GELU → 33 logits (counts 0..32) on the query state, masked to the row's number of
  options, starting uniform;
- the released candidate head, continued (lr 5e-5); LoRA r16 / α32 on every linear layer of the backbone
  (attention, Gated DeltaNet, MLP; lr 2e-4); count head lr 1e-3; AdamW, cosine schedule, 30 warm-up steps, one epoch,
  ≤ 16k padded tokens per batch, bf16 autocast, seed 0.

Losses: −log P(gold set) on multi rows (exact; [losses.py](../../src/bzaf/train/losses.py)); KL(base ‖ model) on
single-answer rows, with the base's own answers as targets (adapters off, original head), because Decision 2.0's
training data is not public.

## Data (≈ 29k rows, built by [`bzaf.train.data.build_e02`](../../src/bzaf/train/data.py))

| rows | source | loss | licence | role in benchmark v0 |
|---|---|---|---|---|
| 4,000 | GoEmotions train (options shuffled) | set | Apache-2.0 | in-domain (test split evaluated) |
| 2,000 | 2–3 GoEmotions train comments merged, gold = union | set | Apache-2.0 | in-domain |
| 3,000 | 1–4 DBpedia-14 train entries merged, a random 4–14 of the 14 classes offered (so some gold is missing: partial and "none" cases) | set | CC BY-SA 3.0 | not in the benchmark |
| 4,000 | synthetic orders, seed 1000 | set | ours | in-domain (seed 0 evaluated) |
| 1,000 | wide probe generator, seed 1000 (10–200 options) | set | ours | in-domain (seed 0 evaluated) |
| 3,000 | BoolQ train (Noul) | distill | CC BY-SA 3.0 | general track uses validation |
| 3,000 | HellaSwag train (Choice) | distill | MIT | general track uses validation |
| 3,000 | SST-5 train (Score) | distill | research use | general track uses test |
| 2,000 | DBpedia-14 train (Choice, 14 options) | distill | CC BY-SA 3.0 | not in the benchmark |

**Held out (never trained on, no same-family data):** SATA, NLU++, ECtHR, UNFAIR-ToS. Training rows whose state
appears anywhere in benchmark v0 are dropped.

## Evaluation

Benchmark v0 in-process through the same adapter (same questions as a server readout):

- **base:** Eos-0.8B untouched, asked with its own question types (yes/no per option, Choice, "how many", native);
- **ours:** the trained model's `multi` question (predictor `ours@mode`: the most likely set) and the general track.

## Pre-registered decision rule

Held-out tracks H = {sata, nlupp, ecthr, unfair_tos}. Baseline B per track = the better on test of Eos's two
untrained references, `noul_ctx+platt` and `pick+dev_prior` (choosing on test favours the baseline).

- **G2 passes (→ the trainability check on Nox-4B, then E03) if all three hold:**
  1. exact-set, `ours@mode` − B, macro over H: paired 95 % CI above 0;
  2. set log-loss, `ours@mode` − B (B = the lower-log-loss of the two), macro over H: CI below 0;
  3. general track, `native@top1` accuracy, ours − base, macro over its 7 sets: at most 1 point lower (point
     estimate).
- **Condition 3 fails only:** raise the distillation weight or lower the LoRA learning rate, one rerun, then decide.
- **1 or 2 fail on some tracks only:** inspect count calibration per track; one targeted fix, then decide.
- **1 and 2 fail on all of H:** stop and diagnose (data mix, count head, loss) before renting bigger GPUs.

Reported, no decision attached: in-domain tracks, count accuracy, order stability, calibration and selective
automation of `ours@mode`, the training-loss split (count vs selection).

**Ablation (second run, same data and budget; to implement before it runs):** count head off, one sigmoid per option
with binary cross-entropy (direction 2), decoded at 0.5. Read-out, not a gate: if it matches the count head within
CIs on exact-set and log-loss, report it and prefer the simpler model.

## Commands

```bash
uv run modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Eos-0.8B             # adapter check, real weights
uv run modal run cloud/train_modal.py --name e02-smoke --args "--scale 0.02 --max-steps 20 --eval-limit 20 --eval-base"
uv run modal run cloud/train_modal.py --name e02 --args "--eval-base"
modal volume get bzaf-runs e02 runs/
uv run bzaf bench score runs/e02/eval/ours --out experiments/E02-count-head/results/ours
uv run bzaf bench score runs/e02/eval/base --out experiments/E02-count-head/results/base
H=sata,nlupp,ecthr,unfair_tos
uv run bzaf bench compare runs/e02/eval/ours runs/e02/eval/base --predictor ours@mode \
  --predictor-b noul_ctx+platt,pick+dev_prior --only $H > experiments/E02-count-head/results/g2-exact.md
uv run bzaf bench compare runs/e02/eval/ours runs/e02/eval/base --predictor ours@mode \
  --predictor-b noul_ctx+platt,pick+dev_prior --only $H --metric per_item_nll > experiments/E02-count-head/results/g2-logloss.md
uv run bzaf bench compare runs/e02/eval/ours runs/e02/eval/base --predictor native@top1 > experiments/E02-count-head/results/g2-general.md
cp runs/e02/train_log.jsonl runs/e02/config.json experiments/E02-count-head/results/
```

## Results

*Not run yet.*
