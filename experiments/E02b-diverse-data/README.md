# E02b — The E02 recipe on diverse, count-decoupled data

**Status:** pre-registered 2026-10-09, before any run · **Compute:** Modal, one L40S · **Code:**
[`src/bzaf/train/mix.py`](../../src/bzaf/train/mix.py), loaders in [`src/bzaf/data/`](../../src/bzaf/data/)

## Question

E02 failed G2: its count head learned the answer-count distribution of its four kinds of training data (mostly 1–3
answers, 8.7 % empty) and did not transfer to held-out families ([E02 results](../E02-count-head/)). With the same
model and recipe, does a mixture of many more task families, in which a row's answer count no longer follows from its
source, pass G2?

This is the "one targeted rerun" E02's decision rule allows after "stop and diagnose": only the data changes.

## Model and recipe (unchanged from E02)

`vllm-sr/Decision-2.0-Eos-0.8B`, our Decision 2.0 adapter, the `multi` question type, count head (0..32), LoRA r16 /
α32 on every linear layer, learning rates 2e-4 / 5e-5 / 1e-3, AdamW, cosine schedule, 30 warm-up steps, one epoch,
≤ 16k padded tokens per batch, bf16, seed 0. Loss: −log P(gold set) on multi rows, KL(base ‖ model) on single-answer
rows. Run with `--mix e02b`.

## Data (built by `bzaf.train.mix.build_e02b`)

Held-out families stay out of training ([D21](../../docs/decisions.md), strict): SATA's six families (story reading
comprehension with candidate answers, toxicity categories, news topics, MeSH headings, EUR-Lex concepts, business-news
events), legal texts, intent detection. Sources chosen from the [dataset survey](../../docs/data.md):

| rows | source | family | one row | licence |
|---|---|---|---|---|
| 7,000 | QAMPARI train | list questions over Wikipedia | which entities answer a list question; one proof sentence per option | CC0 (proofs: Wikipedia, CC BY-SA) |
| 2,500 | Qasper train | evidence in long papers | which numbered paragraphs hold the evidence (up to ~5k tokens of paper) | CC BY 4.0 |
| 1,500 | WiCE train | evidence on a web page | which sentences support a Wikipedia claim | ODC-BY (pages: Common Crawl terms) |
| 5,000 | SQuAD 2.0 train | answerability | which of these questions the passage answers (no answer spans) | CC BY-SA 4.0 (to re-check) |
| 6,000 | Amazon ESCI train (US) | product search | which products match exactly / are acceptable / are complements | Apache-2.0 |
| 2,500 | WANDS | product search | which products match exactly / are partly relevant | MIT |
| 1,500 | DBpedia-Entity v2 | entity search | which judged entities are (highly) relevant | MIT (names: DBpedia, CC BY-SA) |
| 6,000 | Re-DocRED train | relations in a document | which of 96 relations hold from A to B / with A as subject | MIT (names: Wikidata, CC0) |
| 3,000 | MAMS (aspect categories) | review aspects | which aspects a review mentions / praises / criticises | Apache-2.0 |
| 3,000 + 1,000 | GoEmotions train (single, merged) | emotions | as E02 | Apache-2.0 |
| 2,000 | DBpedia-14 merged | entry categories | as E02 | CC BY-SA 3.0 |
| 3,000 + 1,000 | synthetic orders, wide catalogue (seed 1000) | ours | as E02 | ours |
| 15,000 | BoolQ, HellaSwag, SST-5, DBpedia-14 (4,000 / 4,000 / 3,500 / 3,500) | single-answer replay (KL to base) | as E02 | as E02 (SST-5: research use, must be replaced before any release) |

How a row is drawn (the change that matters): each source is a pool of base items with all their candidate options
(gold plus judged or in-document negatives only). For every row the answer count is drawn first from
`COUNT_BUCKETS` (0: 25 %, 1: 17 %, 2–4: 25 %, 5–9: 15 %, 10–19: 11 %, 20–32: 7 %, capped by the most the source can
offer), then an item that has that many answers, then the option count, log-uniform in the source's range; options
are shuffled (numbered units stay in document order); at most 3 rows per base item; rows longer than the model's input
limit (or 7,000 tokens), measured with its tokenizer, lose negatives first or are skipped. Contamination: rows whose
state equals a benchmark v0 state, or (for outside text, replay included) shares a 13-word sequence with one, are
dropped.

Preview of the mixture, built on 2026-10-09 without the DBpedia rows and the replay (Hugging Face downloads are
blocked in the environment that prepared this; the run's `mixture_stats.json` has the final numbers): 43,000 multi
rows; answers 0: 30 %, 1: 20 %, 2–4: 29 %, 5–9: 13 %, 10–19: 6 %, 20–32: 3 % (E02: 8.7 % empty, mostly 1–3); options
2–4: 18 %, 5–10: 33 %, 11–30: 33 %, 31–100: 17 %; share of options correct ≤ 5 %: 38 %, 6–20 %: 19 %, 21–50 %: 20 %,
> 50 %: 23 %; ~56M estimated tokens. Sources that cannot offer large answers (MAMS ≤ 5, Re-DocRED ≤ 13) keep more
small counts, so the large buckets come from QAMPARI, ESCI, WANDS and DBpedia-Entity.

## Runs

- **A (main, decides G2):** `--mix e02b`. About 2.5–3 h on an L40S, about $7.
- **B (read-out):** `--mix e02b --set-loss sigmoid`, the E02 ablation on this data: does the formulation still matter
  once the data is diverse?
- **C (read-out):** `--mix e02b --drop qampari,dbpedia_merged`, without the sources closest to held-out families
  (QAMPARI near story reading comprehension, DBpedia-14 categories near subject tagging, D21): how much do they move
  SATA's subsets?

B and C run only after A, if the budget allows; neither changes the decision on A.

## Evaluation

Benchmark v0 in-process, as E02. The base is the same model on the same benchmark, so E02's base evaluation
(`runs/e02/eval/base`) is reused: E02b runs need no `--eval-base`.

## Pre-registered decision rule (G2, unchanged from E02)

Held-out tracks H = {sata, nlupp, ecthr, unfair_tos}; B per track = the better on test of `noul_ctx+platt` and
`pick+dev_prior` (choosing on test favours the baseline).

- **G2 passes (→ the trainability check on Nox-4B, then E03 with this mixture plus more families) if all hold:**
  1. exact-set, `ours@mode` − B, macro over H: paired 95 % CI above 0;
  2. set log-loss, `ours@mode` − B (B = the lower-log-loss of the two), macro over H: CI below 0;
  3. general track, `native@top1`, ours − base, macro over 7 sets: at most 1 point lower (point estimate).
- **Condition 3 fails only:** raise the distillation weight or lower the LoRA learning rate, one rerun, then decide.
- **1 or 2 fail on some tracks only:** inspect per track (count calibration, SATA subsets, count buckets); one targeted
  fix, then decide.
- **1 and 2 fail on all of H:** data diversity alone does not make the count transfer at 0.8B. Stop and choose among:
  a count head that reads per-option evidence, teacher-labelled families (open teachers, D4), or a per-task prior
  correction, before any 4B spend.

Reported, no decision attached: E02b − E02 (the effect of the data, same comparisons), each run against the base's
label-free predictors (`pick+count`, `noul_ctx+count`, `pick@top1`) and with B's own information (ours + dev count
prior, [diagnose.py](../E02-count-head/diagnose.py)), SATA by source subset and every held-out track by gold count
([breakdown.py](breakdown.py)), in-domain tracks, order stability, the training-loss split.

## Commands

```bash
# smoke run first (~10 min, < $1): builds the mixture (the first build downloads ~1.5 GB to the cache volume)
uv run modal run cloud/train_modal.py --name e02b-smoke --args "--mix e02b --scale 0.02 --max-steps 20 --eval-limit 20"
# run A
uv run modal run --detach cloud/train_modal.py --name e02b --args "--mix e02b"
uv run modal run --detach cloud/train_modal.py --name e02b --args "--mix e02b --resume"   # only after an interruption
# results
modal volume get bzaf-runs e02b runs/
R=experiments/E02b-diverse-data/results; H=sata,nlupp,ecthr,unfair_tos; mkdir -p $R
uv run bzaf bench score runs/e02b/eval/ours --out $R/ours
uv run bzaf bench compare runs/e02b/eval/ours runs/e02/eval/base --predictor ours@mode \
  --predictor-b noul_ctx+platt,pick+dev_prior --only $H > $R/g2-exact.md
uv run bzaf bench compare runs/e02b/eval/ours runs/e02/eval/base --predictor ours@mode \
  --predictor-b noul_ctx+platt,pick+dev_prior --only $H --metric per_item_nll > $R/g2-logloss.md
uv run bzaf bench compare runs/e02b/eval/ours runs/e02/eval/base --predictor native@top1 > $R/g2-general.md
uv run bzaf bench compare runs/e02b/eval/ours runs/e02/eval/ours --predictor ours@mode --only $H > $R/vs-e02-exact.md
uv run python experiments/E02-count-head/diagnose.py runs/e02b/eval/ours runs/e02/eval/base > $R/diagnosis.md
uv run python experiments/E02b-diverse-data/breakdown.py runs/e02/eval/base e02=runs/e02/eval/ours \
  e02b=runs/e02b/eval/ours > $R/breakdown.md
cp runs/e02b/train_log.jsonl runs/e02b/config.json runs/e02b/mixture_stats.json $R/
COPYFILE_DISABLE=1 tar czf $R/eval-records.tgz -C runs/e02b eval
```

## Results

*Not run yet.*
