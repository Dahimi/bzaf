# Roadmap

Each phase ends with a gate. A failed gate is a result, not a delay: it redirects the plan before money or weeks are
spent. Experiments live in [`experiments/`](../experiments/), one folder each, pre-registered before they run.

| Phase | When | Where | Experiment | Gate |
|---|---|---|---|---|
| 1. Readout baselines | week 1 | Mac, no training | [E01](../experiments/E01-readout-baselines/) | **G1:** ranking + true count beats the best yes/no predictor. Pick the base model. |
| 2. Count head, small | weeks 2–3 | Mac, 0.8B | E02 | **G2:** trained count model beats the best E01 predictor on held-out datasets (set log-loss and exact-set) without hurting single-answer Choice. |
| 3. Scale + ablation | week 4 | cloud, 4B (9B if useful) | E03 | **G3:** count head vs count head off (direction 2); residual dependence check decides on the chain head. |
| 4. Release | weeks 5–6 | — | — | Weights, model card, report; submit to the Decision Index (SATA-Bench, ACOS). |

## Phase details

**1. Readout baselines (E01).** Ask 3–4 candidate 4B decision models about SATA-Bench, UNFAIR-ToS, GoEmotions and
synthetic items, using only the question types they support. Score untrained predictors offline. Outputs: the
baseline table for the paper, the base-model choice, and the G1 decision.
*If G1 fails* (knowing the count does not help), the count approach loses its justification: make direction 2 (one
sigmoid per option, options in view) the primary model and keep the count head as the ablation.

**2. Count head on 0.8B (E02).** Implement the count head on the chosen base (Kev fallback), train locally on the
data mix in [approach.md](approach.md), evaluate on held-out datasets (SATA-Bench, UNFAIR-ToS and one emotion and one
topic dataset never trained on). *If G2 fails,* stop and diagnose before renting GPUs.

**3. Scale and ablation (E03).** LoRA on the 4B in the cloud (a handful of GPU-hours per run). Main ablation: count
head off. Residual-dependence check: fit pairwise terms on dev residuals; if they buy a clear gain on real data, the
chain head comes back (see [alternatives.md](alternatives.md)).

**4. Release.** Apache-2.0 weights (subject to base licence), model card with lineage, the harness, results; Decision
Index submission for an independent number.

## Open items

- Your own 20–50 real multi-answer questions as an extra held-out set (most honest test).
- Licence check for every training dataset before phase 2 (recorded in the model card).
- Decision 2.0 lineage check before it is a candidate base.
