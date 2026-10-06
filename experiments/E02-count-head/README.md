# E02 — Count head on Kev-0.8B

**Status:** planned (pre-registration) · **Compute:** Modal (A10G/L40S for 0.8B) · **Tracking:** W&B

## Question

Does a trained count head on top of Kev's per-option scores turn multi-answer questions into good answer sets,
beating every untrained strategy from E01 on datasets it never saw, without hurting single-answer Choice?

## Model

Kev-0.8B (Qwen3.5-0.8B-Base + Kev's LoRA and pointer head), continued from the released checkpoint
(`--init_from`, as Kev recommends for fine-tunes). Added:

- **count head:** one linear layer on the `<decide>` hidden state → logits for counts 0..16;
- per-option scores `z_i` from Kev's existing pointer head (unchanged structure, trained further);
- answer-set distribution from [`bzaf.setdist`](../../src/bzaf/setdist.py): P(S) = P(|S|) · Π_{i∈S} e^{z_i} / e_|S|.

Loss: −log P(gold set). On single-answer data this is exactly Kev's cross-entropy (count fixed at 1), so Kev's own
training data is mixed in unchanged to keep Choice intact.

**Ablation (same run budget):** count head off, per-option sigmoid with binary cross-entropy (direction 2). Its set
distribution is the independent product, decoded at 0.5.

## Data

Training (multi-answer, natural-language label names; licences checked and recorded before the first run):

| Source | Answers per item | Notes |
|---|---|---|
| GoEmotions train | 1–3 (mostly 1) | test split stays for evaluation (in-domain) |
| Synthetic orders, training seeds | 0–7 | exact gold; different seeds from the evaluation set |
| Further multi-label sets (candidates: SemEval-2018 E-c, MixATIS/MixSNIPS, MultiEURLEX level 1, Reuters) | various | added only if the licence allows; listed in the run config |
| Kev's own single-answer data (`decision-v7`) | 1 | keeps Choice behaviour (count = 1) |

Augmentation: shuffled option order, random subsets of each label set (creates "none" and different counts),
paraphrased option names where available.

Evaluation, **never trained on**: SATA-Bench (400) and UNFAIR-ToS (800) as held-out datasets; GoEmotions test and a
synthetic evaluation seed as in-domain sets; Kev's single-answer development split for the no-regression check.
Same items and dev/test split as E01, so E01 numbers are directly comparable.

## Baselines (from E01, same base model, same items)

Best untrained predictor per dataset, including `pick+dev_prior` (the dataset's typical count, the strongest
non-item-level baseline) and `noul_ctx+platt`. Ceiling: `pick+true_count`.

## Pre-registered decision rule

- **G2 (pass → E03 on Kev-4B):** on **both** held-out datasets (SATA, UNFAIR-ToS), the trained count model beats the
  best E01 untrained predictor for Kev-0.8B in exact-set accuracy with the 95 % paired CI above 0, **and** its
  set log-loss is lower; **and** single-answer accuracy on Kev's dev split drops by at most 1 point.
- **Fail on one held-out dataset only:** check count calibration on that dataset before deciding; one targeted fix,
  then decide.
- **Fail on both:** stop and diagnose (data mix, count head capacity, loss) before renting bigger GPUs.
- **Ablation read-out (not a gate):** count head vs sigmoid on the same data. If the sigmoid matches the count head
  within CIs on exact-set and log-loss, report it and prefer the simpler model (approach.md, "main ablation").

## Logged per run (W&B)

Code commit, dataset mix and revisions, base checkpoint revision, all hyperparameters; training loss split into count
and option terms; per-dataset exact-set, set log-loss, count accuracy, single-answer accuracy.

## Results

*Not run yet.*
