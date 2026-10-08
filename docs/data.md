# Data plan

*Agreed 2026-10-06 (D13). Living document: the licence register at the bottom is updated before any source is used.*

## Principles

1. **Generality first.** The model must stay a general decision model (Choice, yes/no, Score) and gain multi-answer.
   Every training mix contains single-answer data (the base's own, for replay) next to multi-answer data.
2. **Zero-shot claims need held-out families.** Whole task families (not just items) are kept out of training and used
   only for evaluation ([D21](decisions.md)): SATA-Bench's six families (story reading comprehension with candidate
   answers, toxicity categories, news topics, MeSH headings, EUR-Lex concepts, business-news events), legal texts
   (UNFAIR-ToS, ECtHR), and intent detection (NLU++, CLINC150).
3. **Every row is traceable:** source, licence, generator (dataset, program or teacher model + provider + prompt
   version), and the stage it belongs to.
4. **Contamination checks** against every evaluation set (ours, public JevBench items, Decision Index) before training.

## Stages

| Stage | What | Purpose | First used |
|---|---|---|---|
| **A. Breadth** | Public multi-label and multi-answer sets with natural-language label names; public long-document sets with many candidate passages or sentences (needed for the 200-option / 8k requirement); the base's single-answer data for replay; programmatic synthetic data | Coverage of answer counts (0 → 30+), option counts (2 → 255) and lengths (short → 8k) | E02 (lite), E03 |
| **B. Free augmentation** | Random subsets and merges of label sets (new counts, "none" cases), shuffled option order, paraphrased option names, distractor options | Count diversity and order robustness at no labelling cost | E03 |
| **C. Hard cases** | Wrong options the current model ranks high (mined each round); confusable options (near neighbours in label meaning); minimally edited pairs where one changed fact changes the answer set | Precision where the count decision is made | E04 |
| **D. Teacher-labelled** | New states and questions across domains (support, policy, logs, tool routing, ...), labelled by hosted open-weight teachers | Domain coverage beyond public datasets | E03 (small), E04 |

## Teachers (stage D)

- **Where:** hosted APIs for open-weight models (Together, Fireworks, DeepInfra, OpenRouter, ...). No self-hosting.
- **Which:** only models whose licence allows training on their outputs (Apache-2.0 / MIT families, e.g. Qwen,
  DeepSeek, some Mistral models), and only via providers whose terms allow it. Checked and recorded before use.
- **How:** at least two teacher families per labelled set. Where they agree, hard label; where they disagree, soft
  target (the set distribution averaged over teachers), which our proper loss can fit directly. Items where teachers
  disagree strongly are re-checked or dropped.
- **Cost control:** teachers only where public data does not cover a need; cheaper models for bulk generation,
  stronger ones for labelling; spend logged per batch.

## Mixing

Temperature-weighted sampling across sources, so small sources are not drowned out; curriculum from short / few
options to long / many options; a fixed share of the base's single-answer data in every batch.

## Licence register

| Source | Use | Licence | Checked |
|---|---|---|---|
| SATA-Bench | evaluation only (held out) | MIT (repository) | 2026-10-03 |
| UNFAIR-ToS (LexGLUE) | evaluation only (held out) | CC BY 4.0 (per LexGLUE card) | to confirm |
| GoEmotions | train split for training, test split for evaluation | Apache-2.0 | 2026-10-03 |
| Synthetic orders (ours) | training and evaluation (different seeds) | ours | — |
| Kev `decision-v7` | replay (if Kev is the base) | per source, listed in Kev's model cards | to check |
