# E01c — a shipped native multi-answer type (Vela 2.0 Set)

*Pre-registered 2026-10-07, before any Vela readout.*

## Question

Vela 2.0 (vLLM Semantic Router, public since 2026-10-06, Apache-2.0) ships a native `set` question: one trained
sigmoid per option, read with all options in view, kept if above a calibrated threshold. That is our "count head off"
design (direction 2), trained and released. How good is it at multi-answer, and is the **count** still its bottleneck?

E01 showed the count is the bottleneck for *untrained* readouts (yes/no fan-out, Choice). This checks the same thing
on a *trained* per-option head, which is the strongest existing alternative to the count head.

## Setup

- Model: `vllm-sr/Vela-2.0-4B`, served by its own runtime (`cloud/vllmsr_serve.py`, `vllm-srun` pinned at
  semantic-router `246dde1`, default `exact` profile, the package's shipped calibration and thresholds).
- Items: the E01 files unchanged (SATA 400, GoEmotions 400, UNFAIR-ToS 800, synthetic 300), same dev/test split.
- Variants: `set,pick,count,noul_ctx`.
- Predictors (new ones in bold): **`set@shipped`** (as the server answers), **`set+platt`** (threshold refitted on
  dev), **`set+true_count`** (its ranking, told the count), **`set+dev_prior`**, plus the E01 predictors.
- Cost: about $1–3 on an L40S.

Commands: [cloud/README.md](../../cloud/README.md#vllm-semantic-router-models-vela-20-decision-20).

## Pre-registered reading

Main signal **V1** = `set@shipped` − `set+true_count`, exact-set, on SATA and GoEmotions (the two real datasets where
"none" does not dominate).

- **V1 ≤ −10 points with CI below 0 on both:** the count is the bottleneck for a trained sigmoid too. Plan unchanged;
  this strengthens the paper's finding (it holds for a released, trained set head, not only for untrained readouts),
  and Vela-4B is the shipped-sigmoid baseline in the model study.
- **V1 within 5 points on both:** a trained sigmoid with options in view already counts about as well as the true
  count allows. Then the count head's case rests on set probabilities (log-loss, calibration), constraints and
  keeping general quality, not on accuracy. Before spending on E03 we re-plan the headline, and G2/G3 must show the
  count head beating a trained sigmoid on set log-loss.
- **In between:** report, plan unchanged, flag in the paper notes.

Also reported (no decision attached): Vela-4B `set@shipped` against Kev-4B's and Imajev-4B's best untrained
predictor on the same items, for the model study; set log-loss of `set@shipped` and `set+platt`.

## Caveats written down in advance

- This tests the shipped model, not the sigmoid method: Vela's Set head was trained mostly on router and safety
  labels, so SATA's questions may be out of its distribution (*corrected 2026-10-08:* SATA is not exam-style; its items
  come from six multi-label sources: story reading comprehension, toxicity, Reuters topics, MeSH, EUR-Lex, business
  events; see [benchmark.md](../../docs/benchmark.md)). The method-level comparison (count head vs
  sigmoid on the same backbone and data) remains E02/E03's main ablation.
- Vela 2.0 4B keeps 74 % of Nox-4B's Decision Index score (31.63 vs 42.55, their blog), so it is not a candidate base
  for us; it is a baseline.

## Results (2026-10-07)

Run on Modal with `cloud/vllmsr_serve.py` (default `exact` profile). Tables: [results/vela-2.0-4b.md](results/vela-2.0-4b.md).
Decision 2.0 Nox-4B was read out in the same session with the E01 variants (no `set`):
[results/decision-2.0-nox-4b.md](results/decision-2.0-nox-4b.md). Its SATA file has 16 failed items (4 %, HTTP 503
while the model was loading); they count as wrong until the readout is re-run.

**Pre-registered signal V1** (`set@shipped` − `set+true_count`, exact-set, test split):

| dataset | V1 [95% CI] | shipped answer size (gold) |
|---|---|---|
| SATA | **−28.8** [−34.2, −23.4] | 2.50 (3.58), too few |
| GoEmotions | **−19.1** [−24.0, −14.6] | 2.19 (1.18), too many |
| UNFAIR-ToS (not in the rule) | −24.7 [−28.5, −21.4] | 0.38 (0.13), too many |
| synthetic (not in the rule) | −32.2 [−38.5, −25.9] | 2.40 (2.79), too few |

**Reading: first branch.** V1 ≤ −10 with CI below 0 on both SATA and GoEmotions. The count is the bottleneck for a
released, trained per-option set head too, not only for untrained readouts. Plan unchanged.

Other observations:
- **Vela's set head ranks best of all models measured** (ranking + true count: SATA 60.1, GoEmotions 37.1) but, as
  shipped, it lands where every other model does without the count (SATA 31.3, GoEmotions 18.0). Its errors go in
  both directions depending on the dataset, the same pattern E01 found for untrained yes/no.
- **Its ranking is no better than Choice's** (V2, Choice minus set ranking, both told the count: SATA −1.4 [−4.0, +1.1],
  GoEmotions −0.4 [−1.5, +0.8]). Training a per-option head improved neither ranking nor counting over Choice.
- **Refitting its threshold on dev does not fix the count on real data** (`set+platt`: SATA 34.2, GoEmotions 18.4),
  although it does on synthetic data (90.2). A single threshold per dataset cannot read the count from each item.
- **Its set probabilities are poorly calibrated as shipped:** set log-loss SATA 5.43 vs 3.83 after refitting, and 3.56
  for Vela's own Choice scores plus a dataset count prior (`pick+dev_prior`); GoEmotions 4.53 vs 3.11 and 2.83.
  The independent product of per-option probabilities is not a usable set probability without recalibration.

Best realistic (no oracle) exact-set on SATA across the models measured so far, against each model's own ranking +
true count:

| model | best realistic | ranking + true count (best field) |
|---|---|---|
| Kev-4B (E01) | 33.8 (`pick+dev_prior`) | 54.0 |
| Imajev-4B (E01) | 33.1 | 56.8 |
| Decision 2.0 Nox-4B | 32.0 (`noul_ctx+count`) | 54.0 (4 % failed items) |
| Vela 2.0 4B | 34.5 (`pick+dev_prior`) | 60.1 |

Four models from three teams, including one with a trained native set type: all rank well enough for 54–60 %
exact-set given the count, and all land at 32–35 % without it.

Not a fair test of the sigmoid *method* (see caveats): the like-for-like comparison stays E02/E03's main ablation.
