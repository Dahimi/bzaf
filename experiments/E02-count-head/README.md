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
| 4,000 | GoEmotions train (options shuffled; half offer a random 4–20 of the 28 emotions, each gold kept at p = 0.5) | set | Apache-2.0 | in-domain (test split evaluated) |
| 2,000 | 2–3 GoEmotions train comments merged, gold = union | set | Apache-2.0 | in-domain |
| 3,000 | 1–4 DBpedia-14 train entries merged, a random 4–14 of the 14 classes offered (so some gold is missing: partial and "none" cases) | set | CC BY-SA 3.0 | not in the benchmark |
| 4,000 | synthetic orders, seed 1000 | set | ours | in-domain (seed 0 evaluated) |
| 1,000 | wide probe generator, seed 1000 (10–200 options) | set | ours | in-domain (seed 0 evaluated) |
| 3,000 | BoolQ train (Noul) | distill | CC BY-SA 3.0 | general track uses validation |
| 3,000 | HellaSwag train (Choice) | distill | MIT | general track uses validation |
| 3,000 | SST-5 train (Score) | distill | research use | general track uses test |
| 2,000 | DBpedia-14 train (Choice, 14 options) | distill | CC BY-SA 3.0 | not in the benchmark |

*Changed 2026-10-08 after the smoke run (20 steps, a pipeline check, not the experiment), before the full run:* the option-subset augmentation of [approach.md](../../docs/approach.md) was only applied to DBpedia, so 3 % of set rows had an empty answer and the smoke model almost never answered "none" (UNFAIR-ToS, 12 items: mean answer size 1.17 vs 0.17). It now also applies to half the GoEmotions rows: 8.7 % of set rows are empty. No other change.

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

**Ablation (second run, same data and budget):** count head off, one sigmoid per option with binary cross-entropy
(direction 2), decoded at 0.5. Read-out, not a gate: if it matches the count head within CIs on exact-set and log-loss
(`ours@mode`, macro over H), report it and prefer the simpler model.
*Implemented 2026-10-08, after the main run's training finished and before any of its evaluation was looked at:*
`--set-loss sigmoid` ([trainer.py](../../src/bzaf/train/trainer.py)). Each option's log-odds is the candidate head's
logit plus one learned shared bias (in place of the count head, same learning rate 1e-3), because the released head's
logits are softmax logits whose level is arbitrary; the bias starts so that an average option's probability is the
training base rate. Loss Σ_i BCE = −log P(gold set) under independent options. The readout records the count
distribution those probabilities imply (Poisson-binomial), so `ours@mode` is exactly the 0.5-threshold set and its
set log-loss is the independent model's. Same data, seed, batches, LoRA and head settings; the base evaluation of the
main run is reused.

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

# ablation: count head off, one sigmoid per option
uv run modal run --detach cloud/train_modal.py --name e02-sigmoid --args "--set-loss sigmoid"
modal volume get bzaf-runs e02-sigmoid runs/
R=experiments/E02-count-head/results
uv run bzaf bench score runs/e02-sigmoid/eval/ours --out $R/sigmoid
uv run bzaf bench compare runs/e02/eval/ours runs/e02-sigmoid/eval/ours --predictor ours@mode --only $H > $R/ablation-exact.md
uv run bzaf bench compare runs/e02/eval/ours runs/e02-sigmoid/eval/ours --predictor ours@mode --only $H \
  --metric per_item_nll > $R/ablation-logloss.md
cp runs/e02-sigmoid/train_log.jsonl $R/sigmoid-train_log.jsonl
```

## Results

Main run 2026-10-08: 651 steps, 24,913 rows (13,999 set, 10,914 distill), ~10M tokens; ~30 min training at ~5.7k
tokens/s and ~33 min evaluating ours + base on one L40S, about $3. Files in [results/](results/): scores
(`ours.md`, `base.md`), the three G2 comparisons (`g2-*.md`), training log and config, raw answers
(`eval-records.tgz`), and the diagnosis below (`diagnosis.md`, from [diagnose.py](diagnose.py)).

### G2: failed

| condition | result | |
|---|---|---|
| 1. exact-set, `ours@mode` − B, macro over H | **−21.5** [−23.7, −19.3]: ECtHR +2.8 [−2.8, +8.3], NLU++ +1.9 [−2.8, +6.8], SATA −8.5 [−10.4, −6.7], UNFAIR-ToS −82.0 [−86.0, −77.6] | fails |
| 2. set log-loss, `ours@mode` − B, macro over H | **+1.82** [+1.72, +1.91], worse on all four tracks | fails |
| 3. general track, `native@top1`, ours − base, macro over 7 sets | **−0.11** [−1.28, +1.05] (largest drop BBH −5.0 [−10.1, 0.0]) | passes |

Pre-registered branch: condition 2 fails on every held-out track and condition 1 on two of them, so **stop and
diagnose before renting bigger GPUs**. No 4B run.

Reported, no decision attached. In-domain tracks, exact-set (best base predictor in brackets): GoEmotions 51.6 (24.8),
synthetic 88.3 (43.9), wide 95.3 (17.2). Option order shuffled, answers unchanged: GoEmotions 87 %, NLU++ 84 %,
SATA 71 % (base `pick+dev_prior` 84 / 82 / 67 %).

### Diagnosis

Test splits; "ranking + true count" keeps as many top options as the gold set has.

| track | gold size (share empty) | ours: E[size] / P(0) | ranking + true count: ours / base | count ↔ gold rank corr.: ours / base "how many" / base Σ yes-no | "none" AUC: ours P(0) / base |
|---|---|---|---|---|---|
| ECtHR | 1.09 (12 %) | 1.40 / 0.03 | 62.2 / 64.5 | +0.07 / +0.04 / +0.02 | 0.43 / 0.45 |
| NLU++ | 1.93 (14 %) | 1.02 / 0.13 | 54.0 / 53.1 | +0.52 / +0.22 / +0.28 | 0.95 / 0.92 |
| SATA | 3.60 (0 %) | 2.01 / 0.01 | 35.9 / 36.1 | −0.08 / +0.67 / +0.59 | — |
| UNFAIR-ToS | 0.13 (88 %) | 1.29 / 0.04 | 98.2 / 97.9 | +0.16 / +0.18 / +0.19 | 0.86 / 0.88 |
| GoEmotions (in-domain) | 1.18 (0 %) | 1.03 / 0.12 | 58.1 / 28.8 | +0.08 / +0.09 / +0.08 | — |

1. **Selection did not move on held-out tracks.** With the true count, ours and base pick the same sets (within
   ~2 points) on all four; in-domain, training doubled it (GoEmotions 58.1 vs 28.8). The adapters learned the trained
   families, not a general skill, and did no harm elsewhere.
2. **The count failed: it reproduces the training count distribution** (mostly 1–3, 8.7 % empty) instead of each
   task's. UNFAIR-ToS is 88 % "none" but the model gives "none" 4 % probability on average; SATA averages 3.6 answers,
   the model 2.0; NLU++ 1.9 vs 1.0.
3. **Where the count has signal, the level is wrong (a prior shift).** On UNFAIR-ToS and NLU++ the model's P(0)
   separates "none" items well (AUC 0.86, 0.95), and on NLU++ its count tracks the gold count better than the base
   (+0.52 vs +0.22).
4. **On SATA the count has no signal at all** (−0.08), while the base's own "how many" question (+0.67) and the sum
   of its yes/no answers (+0.59) do: a real loss, not only calibration.
5. **Given the information the baselines get, ours matches them.** B fits each track's dev labels (a count prior, Platt
   scaling). Ours with its own ranking and the same dev count prior: exact 38.7 / 31.6 / 20.0 / 88.2 vs B 38.7 / 26.7
   / 21.2 / 88.7; log-loss 2.25 / 3.96 / 4.54 / 0.48 vs 2.27 / 4.16 / 4.49 / 0.46 (ECtHR / NLU++ / SATA /
   UNFAIR-ToS). Against the base's label-free predictors (`pick+count`, `noul_ctx+count`, `pick@top1`): better on
   SATA (12.7 vs 6.1), equal on NLU++ (28.5 vs 29.0), worse on ECtHR (41.5 vs 47.5) and UNFAIR-ToS (6.7 vs 59.7).

**Reading:** a count head trained on five task families learns their count distribution; on families with other
count distributions (exam questions with 3–4 answers, contract clauses that are mostly fine) it does not transfer.
What should transfer is the per-option evidence: how many options are actually supported. Next, in order: the
pre-registered sigmoid ablation (does per-option evidence carry the count to new families better than a count head?),
then one targeted rerun (E02b, pre-registered before it runs) on count-diverse data — many more empty and
large answers, from more families — with whichever formulation wins.

### Ablation: one sigmoid per option (2026-10-08)

Same data, seed and settings, `--set-loss sigmoid` (~35 min, about $2). Files: `sigmoid.md`, `ablation-*.md`
(count head − sigmoid), `sigmoid-g2-*.md` (sigmoid − B, the same G2 comparisons), `sigmoid-diagnosis.md`.

| track | exact-set: count head / sigmoid / B | set log-loss: count head / sigmoid / B | mean answer size: count head / sigmoid / gold |
|---|---|---|---|
| ECtHR | **41.5** / 19.4 / 38.7 | 2.48 / 2.40 / 2.27 | 1.08 / 0.21 / 1.09 |
| NLU++ | 28.5 / **30.9** / 26.7 | 5.21 / 3.82 / 4.16 | 0.90 / 0.94 / 1.93 |
| SATA | 12.7 / 9.3 / **21.2** | 7.76 / 6.78 / 4.49 | 1.93 / 2.10 / 3.60 |
| UNFAIR-ToS | 6.7 / 85.3 / **88.7** | 3.22 / 0.79 / 0.46 | 1.07 / 0.21 / 0.13 |
| GoEmotions (in-domain) | **51.6** / 37.5 / 24.8 | 2.08 / 2.29 / 3.17 | 1.01 / 0.56 / 1.18 |
| synthetic (in-domain) | 88.3 / **99.5** / 43.9 | 0.52 / 0.03 / 2.17 | 2.75 / 2.80 / 2.79 |

- **Count head − sigmoid, macro over H:** exact-set −13.9 [−16.3, −11.4], log-loss +1.22 [+1.15, +1.30]: the sigmoid
  is better on the macro, but the per-track picture splits. It wins UNFAIR-ToS by 79 points and has lower log-loss on
  NLU++, SATA and UNFAIR-ToS; the count head wins ECtHR (+22.1 [+13.4, +30.4]) and SATA (+3.3 [+1.6, +5.1]).
- **The sigmoid also fails G2:** exact-set − B −7.6 [−10.0, −5.4]; log-loss +0.60 [+0.54, +0.66] (better than B
  only on NLU++, −0.34 [−0.49, −0.20]); general track +0.16 [−1.18, +1.49] (passes).
- **The two fail in opposite directions.** The count head always answers something (it learned the training count
  distribution); the sigmoid at 0.5 answers "none" whenever no single option is confident, which is right for
  UNFAIR-ToS (88 % none) and wrong when one answer's probability is split between similar options (ECtHR, GoEmotions:
  the sum of its probabilities is close to the gold size, 0.88 vs 1.09 and 1.10 vs 1.18, but the 0.5 threshold keeps
  too few).
- **Neither reads the count on SATA** (rank correlation with the gold count +0.10 sigmoid, −0.08 count head; the
  base's own per-option yes/no questions, summed: +0.59). With the true count, both pick the same options as the base
  on every held-out track (within ~2 points).

**Reading:** the formulation decides how the model fails on a new family, not whether it transfers. Both learned the
trained families (in-domain gains up to +78 points) and neither learned to judge new families' options in absolute
terms. The per-option evidence the base has (its yes/no answers carry the SATA count) is not reached by either.
