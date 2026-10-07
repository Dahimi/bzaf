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
  labels, so SATA's exam-style questions may be out of its distribution. The method-level comparison (count head vs
  sigmoid on the same backbone and data) remains E02/E03's main ablation.
- Vela 2.0 4B keeps 74 % of Nox-4B's Decision Index score (31.63 vs 42.55, their blog), so it is not a candidate base
  for us; it is a baseline.

## Results

*Not run yet.*
