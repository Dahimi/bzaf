# Landscape and prior art

*Snapshot as of 3 October 2026. The field is a few weeks old and moves weekly; re-check before relying on a number.
"Verified" means read in a primary source (repository or paper text); "reported" means seen only in search results
or secondary write-ups.*

## Jev (TypeSafe AI)

- Launched 15 September 2026; closed, hosted. Primitives: Choice (one of up to 255 options), Score (ordered rubric),
  Noul (P(true)). Questions in one request are isolated from each other by design. *Reported.*
- No native multi-select found as of this date.
- Measured weaknesses relevant to us (verified via paper abstracts/snippets):
  - Multi-label via one Noul per label over-selects: on GoEmotions, labels scored 0.80–0.95 matched the human label
    15 % of the time; tuned thresholds raise UNFAIR-ToS micro-F1 from 0.50 to 0.75
    ([2609.37647](https://arxiv.org/abs/2609.37647)).
  - "X" / "not X" probabilities miss summing to 1 by 0.064 on average (Qwen3.8-27B first-token readout: 0.293);
    three single-label probabilities sum to 1.14 on average ([2609.33209](https://arxiv.org/abs/2609.33209)).
- Licence constraint for us: MCA §2.3(b), see [project-brief.md](project-brief.md).

## Benchmarks

**JevBench** (Benchmark Heaven, [repo](https://github.com/fstandhartinger/jevbench)). v1.5: 1,624 decisions per
system (904 open + 720 sealed; sealed = 50 % of the Intelligence weight); Choice/Noul/Score weighted equally in the
headline. Board at v1.5.5: Cygnet #1 (73.7), Winnow-12B #2; Winnow Intelligence 74.4 vs Jev 72.0; Jev calibration
88.0. *Method verified, board reported.* Caveat: a Noul answer with 0.2 < P(yes) < 0.8 counts as a wrong abstention,
so calibrated hedging is penalised; Jev's low Noul score is partly this rule. **No multi-answer tasks.**

**Decision Index** (apolinario, [repo](https://github.com/apolinario/decision-index)). v0.2.1: 38 benchmarks, ~155k
requests, 67 entrants. Includes **SATA-Bench** (select all that apply, scored as one yes/no per option with all options
listed in the state; exact set) and ACOS. *Verified from the repo's board data:*

| Entrant | SATA exact-set | Index |
|---|---|---|
| Rune 26B-A4B v3 | 34.9 % | 57.44 |
| Hopper | 30.3 % | 39.67 |
| jebadiah-27b | 30.3 % | 54.67 |
| autojev-27b | 29.9 % | 56.40 |
| reflex-27b-v2 | 27.8 % | 52.16 |
| **Jev** | **26.4 %** | 57.89 |
| jpt-9b | 23.6 % | 46.89 |

SATA-Bench paper ([2506.00643](https://arxiv.org/abs/2506.00643)): best LLM 41.8 % exact match; models under-predict
the number of answers (count bias); the Choice Funnel decoding adds up to +29 points.

## Open decision models (candidate bases)

| Model | Base, licence | Head | Training data / lineage | Notes |
|---|---|---|---|---|
| [Kev 1.0](https://github.com/jaredpalmer/kev) | Qwen3.5 0.8B/4B/9B-Base LoRA; Qwen3.8-27B full FT; Apache-2.0 | pointer head (`<decide>` · `</opt>`) | public datasets + generated; "no Jev outputs" | Clean code, MLX serving, Mac training path (slow). Hybrid backbones: each question is its own row. **Fallback base.** |
| [Imajev](https://github.com/mohit67890/imajev) | Qwen3.5 2B/4B/9B LoRA r64; Apache-2.0 | 256-code readout (255 options + unknown) | ~867k decisions: public human-labelled + own 9B labels | #1 JevBench v1.4.2.2. Strongest challenger. |
| [JevK5](https://github.com/allebee/jevk5) / Plumb-4B | Qwen3.5-4B/9B; Apache-2.0 | answer-letter next-token logits | distilled from Qwen3.6-27B **and GPT-6 Luna** | Lineage risk (teacher terms). |
| [Winnow-12B](https://huggingface.co/EldanRing/Winnow-12B) | Gemma-4-12B-IT LoRA (merged); Apache-2.0 | — | private dataset, unnamed teacher | Top Intelligence on JevBench v1.5; too big to train on 18 GB. |
| [Decision 2.0](https://huggingface.co/collections/vllm-sr/decision-20) | Kai 0.6B, Eos 0.8B, Sol 2B, Nox 4B, Lux 9B, Vega 27B; Apache-2.0 | encoder (Kai); Qwen3.5 + shared candidate head (others) | not yet checked | vLLM Semantic Router team. Vega 56.47 on the Decision Index (#3). |
| Laya, Von, GLiClass, GLiNER2 | ModernBERT / mmBERT encoders | label scoring | varies | GLiClass already does multi-label with labels in context (direction 2 exists). |

Multi-answer in the ecosystem today: LLEV `multi` (one yes/no pass per option); Imajev `multi` (serving-only fan-out
to one yes/no per label, threshold 0.5, up to 32 labels); Haste Jev `set_choice` (research
prototype); JevK5-Lite sigmoid heads (encoder only). **Nobody returns calibrated answer-set probabilities or honours
count constraints.**

## Prior art (cited from the literature, not re-fetched)

- **Predicting the number of labels (closest prior art to our count head):** MetaLabeler (Tang, Rajan & Narayanan,
  WWW 2009) learns the number of labels per instance and takes the top-k of a score vector; DeepSetNet (Rezatofighi et
  al., ICCV 2017) and *Joint Learning of Set Cardinality and State Distribution* (AAAI 2018) learn cardinality and
  element scores jointly for multi-label image classification. The exact size-conditioned likelihood (conditional
  Bernoulli / conditional Poisson, computed with elementary symmetric polynomials) is classical sampling theory
  (Chen, Dempster & Liu 1994) and is used for k-subset learning (e.g. SIMPLE, Ahmed et al. 2023).
- Label dependence and loss: Dembczyński et al. 2012 (MLJ); probabilistic classifier chains, Dembczyński et al. 2010;
  F-measure maximisation (GFM), Dembczyński et al. 2011; classifier chains, Read et al. 2009.
- Constrained joint outputs: Semantic Probabilistic Layers (Ahmed et al. 2022); semantic loss (Xu et al. 2018).
- Zero-shot multi-label with runtime labels: GLiClass (Knowledgator), GLiNER2, NLI-based zero-shot.
- Consistency across questions: BeliefBank (Kassner et al. 2021), ConCoRD (Mitchell et al. 2022); coherence and
  proper scoring rules (Predd et al. 2009).
- Conformal multi-label: Cauchois, Gupta & Duchi 2021; conformal risk control (Angelopoulos et al.).

## Where the gap is

The algorithms are known, including the count-then-select idea (MetaLabeler, DeepSetNet). What is missing: (1) no typed decision model returns calibrated answer-set probabilities
or honours count constraints; (2) no benchmark in this ecosystem scores set-level calibration (the Decision Index has
only exact-set accuracy); (3) nobody has measured how much of the multi-answer gap is counting versus genuine
dependence between options. This project targets (1) with evidence for (3), and contributes (2).

## Not verified (blocked from the planning sandbox)

TypeSafe's launch post, docs and MCA text; Archer Hume's architecture probes; Hugging Face model cards; the live
JevBench board beyond search snippets; Decision 2.0's "64 questions in 63 ms" claim.
