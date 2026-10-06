# Project brief

*Agreed 3 October 2026. Changes go through [decisions.md](decisions.md).*

## Goal

An **open-weights System One decision model with a native multi-answer question type**: one question, several
options, any number of which can be correct (including none). It answers in one forward pass with calibrated
probabilities for whole answer sets, not just for single options.

Deliverables, in order:

1. Open weights (Apache-2.0 if the base model allows) and inference code: a **9B flagship and a 4B companion** that
   match their base on general decision benchmarks (Choice, yes/no, Score) and lead on multi-answer at their size
   (D11).
2. A short paper or technical report: the method, and evidence of when it beats asking one yes/no question per
   option.
3. The evaluation harness and multi-answer test suite, ideally contributed as a track to an existing benchmark
   (the Decision Index already hosts SATA-Bench).

## Why

Decision models such as TypeSafe's Jev and its open alternatives answer typed questions (Choice, Score, yes/no) with
probabilities. Choice returns exactly one option, and its probabilities sum to 1, so two correct options split the
probability. The usual workaround is one yes/no question per option, and it fails in measurable ways:

- Each yes/no question cannot see the other options, so the model over-selects. On GoEmotions, labels Jev scored
  0.80–0.95 matched the human label only 15 % of the time ([arXiv 2609.37647](https://arxiv.org/abs/2609.37647)).
- Exact-set accuracy is low: Jev 26.4 % on SATA-Bench in the Decision Index, best open entrant 34.9 %.
- There is no answer-set probability and no way to state "exactly one", "at most 3" or "none of these".

Questions with several valid answers are common (tags, intents, policy violations, symptoms, reasons), so this is a
primitive worth having.

## Scope

**In:** the multi-answer question type: answer-set probabilities, per-option probabilities, a probability for the
number of answers, "none", and count constraints (exactly / at most / at least k).

**Hard requirements for the release model (D12):** up to **200 options** in one question and **8k tokens** of input.

**Out of scope, follow-up project (D14):** query-based evidence / context selection (pick the relevant lines of a
page for a query). It builds on this model, but it is a separate project and paper.

**Out for now (parked, see [alternatives.md](alternatives.md)):** dependence between different questions in one
request (linked question groups), chain heads, diffusion, conformal wrappers. They come back only if the evidence asks
for them.

## Constraints

- **No Jev outputs, ever, for training anything**, and no live Jev calls as a baseline. TypeSafe's Master Customer
  Agreement §2.3(b) forbids using the service or its outputs for distillation or for building a competing product.
  We use only published third-party Jev numbers.
- **Clean lineage for weights and data.** A base checkpoint must have a permissive licence and must not be distilled
  from a model whose terms forbid it. Synthetic data is generated programmatically or by a teacher whose licence
  allows training use (open-weight models are the safest).
- **Compute:** Modal GPUs for readouts and training (D8); the laptop for development. **Budget:** up to about
  $300–400 of GPU and teacher-API spend, released in phase gates and only if results justify it (D15).
- **One person, short iterations.** Every phase ends with a gate that can stop or redirect the project.
