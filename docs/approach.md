# Approach: per-option scores plus a count

## The idea in one example

Ticket: *"I was charged twice and the app crashes when I open the billing page."*
Options: `billing`, `bug`, `refund`, `account access`, `feedback`. Correct answer: {billing, bug}.

| Method | What it outputs | Result |
|---|---|---|
| Choice (Jev, Kev, Imajev, JevK5) | billing 0.55, bug 0.40, refund 0.03 … (sums to 1) | one answer: {billing} |
| One yes/no per option (LLEV `multi`, the usual workaround) | billing 0.90, bug 0.85, refund 0.70, access 0.40 | each judged alone, over-selects: {billing, bug, refund} |
| One sigmoid per option, options in view (GLiClass) | as above but better informed | the number of answers falls out of independent thresholds |
| **Count approach (this project)** | Choice scores as above, plus *how many apply*: 1 = 0.20, 2 = 0.65, 3 = 0.15 | {billing, bug} 0.53 · {billing} 0.11 · {billing, bug, refund} 0.08 … |

The difference: "how many?" is one explicit decision, made with every option in view, instead of an accident of
separate thresholds. That is where the documented failures are: too many answers on GoEmotions, too few on
SATA-Bench (its paper calls it count bias).

## The model

For a question with K options, the model produces in **one forward pass**:

- one score per option, `z_i`, from the existing pointer head (Kev: `<decide>` hidden state against each option's
  `</opt>` hidden state; Choice is softmax(z));
- **new:** a count distribution `P(|S| = s)` for s = 0…K_max, from a single linear layer on the `<decide>` hidden
  state (about 40k parameters on a 4B model).

They define a distribution over answer sets:

```
P(S) = P(|S| = s) · Π_{i∈S} w_i / e_s(w),     w_i = exp(z_i),  s = |S|
```

`e_s(w)` is the sum of weight products over all sets of size s (the elementary symmetric polynomial), computed
exactly in O(K·s). In words: decide how many options apply, then which ones, in proportion to their weights.

From this one distribution we read off ([`src/bzaf/setdist.py`](../src/bzaf/setdist.py)):

- the most likely answer sets with probabilities (best-first search per size);
- each option's probability of being in the set (marginals);
- the count distribution, including P(none);
- count constraints at no cost: "exactly one" sets the count to 1, "at most 3" truncates it, "at least one" drops 0.

## Why this design

1. **It contains today's Choice.** With the count fixed at 1, P({i}) = softmax(z)_i exactly. We start from the base
   model's trained pointer head; only the count head starts from scratch, and single-answer behaviour is preserved
   by construction (and checked).
2. **It contains direction 2 (one sigmoid per option).** Independent per-option probabilities p_i are this same
   formula with z_i = logit(p_i) and the count fixed to the Poisson-binomial count those probabilities imply. So the
   count approach is "per-option scores plus a learned count". Switching the count head off is the main ablation.
3. **Nothing else changes.** Same single pass, same isolation between questions, same prefix caching; works on
   hybrid backbones (Qwen3.5 Gated DeltaNet) because nothing depends on attention masks.
4. **One proper training loss.** Train by minimising −log P(gold set). Single-answer data is the count = 1 case of
   the same loss (it reduces to Choice's cross-entropy), so both data types mix freely.

## Training recipe (phase 2)

- Base: chosen in E01 (Kev fallback). Continue its LoRA; train pointer head and count head together.
- Loss: −log P(gold set), plus the base's existing single-answer data as count-1 examples.
- Augmentation: shuffle option order, paraphrase option names, random subsets of each label set (this creates
  "none" cases), distractor options.
- Calibration: fit a temperature for the option scores and one for the count head on in-distribution dev data.
- Ablation: same model, count head off, trained with per-option binary cross-entropy (direction 2).

## What it cannot do (and the escalation path)

Beyond the count, options interact only through their scores, so a rule like "B implies A" is not modelled
directly. If, after training, a gap remains on real data that the count cannot explain, the next step is a small
pairwise term or a chain head over the per-option readout vectors (see [alternatives.md](alternatives.md)).

## Theory it rests on, and what is not new

**Not new:** predicting the number of labels and selecting the top-scoring ones (MetaLabeler, 2009), learning
cardinality and element scores jointly (DeepSetNet / Rezatofighi et al., 2017–2018), and the size-conditioned
likelihood itself (conditional Bernoulli / conditional Poisson). See [landscape.md](landscape.md).
**What is new here:** options defined at request time rather than a fixed label set, so the count must be inferred
from the question and the options themselves; a single pass inside a typed decision model that also serves Choice,
yes/no and Score; the measured finding that these models rank well but cannot count (E01); and calibrated set
probabilities used for decisions (constraints, "none", selective automation).


Dembczyński et al. (2012), *On label dependence and loss minimization in multi-label classification*: per-label
losses need only marginals; exact-set accuracy needs the joint mode; F-measure needs the per-label probabilities
conditioned on set size (Dembczyński et al. 2011, GFM). The count approach provides exactly that last quantity, which
is why it is a natural middle ground between independent labels and a full joint model.
