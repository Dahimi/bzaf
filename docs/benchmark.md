# Multi-answer benchmark v0

*Built 2026-10-07. Code: [`src/bzaf/bench.py`](../src/bzaf/bench.py). Every track is evaluation-only: none of these
datasets (or their training splits, where they have one) goes into our training data.*

## Why

Existing benchmarks score multi-answer questions with exact-set accuracy only (SATA-Bench, the Decision Index's SATA
track), on one domain each, with at most 16 options. They cannot show what a set-level model is for: honest
probabilities for the whole answer, answers that do not depend on option order, and holding up at many options and
long inputs. v0 is the smallest benchmark that measures all of that, built from public data and two generators.

## Tracks

| track | role | items | options (mean / max) | answers per item | what it tests | source, licence |
|---|---|---|---|---|---|---|
| `sata` | headline | 1,650 (all) | 9.4 / 16 | 2–11 | six multi-label sources (by inspecting items; corrected 2026-10-08, earlier described as exam-style): reading comprehension over story plots (342 items, MultiRC-style), toxicity categories (284, Jigsaw-style), Reuters news topics (249), MeSH root categories of PubMed abstracts (260), EUR-Lex concepts (311), business-news event types (204); comparable with the SATA-Bench paper | SATA-Bench @371dd0c, MIT |
| `goemotions` | headline | 600 | 28 / 28 | 1–3 | emotions in Reddit comments; over-selection | GoEmotions test @e49bbfe, Apache-2.0 |
| `unfair_tos` | headline | 800 | 8 / 8 | 0–2, 89 % none | unfair clauses in terms of service; "none" | LexGLUE UNFAIR-ToS test, CC BY 4.0 |
| `nlupp` | headline | 600 | 45 / 48, with descriptions | 0–6 | intents in customer messages (banking, hotels) | NLU++ @57ec275, CC BY 4.0 |
| `ecthr` | headline | 300 | 10 / 10 | 0–4, mostly 1 | violated articles from court case facts; long inputs (cut to ~6k tokens) | LexGLUE ECtHR-A test (HUDOC) |
| `synthetic` | headline | 300 | 7 / 10 | 0–7 | statements about a JSON order; exact gold, linked options | ours |
| `wide` | probe | 300 (75 × K) | K = 10, 50, 100, 200 | 0–6 | products in an order: cost and quality against the number of options | ours |
| `order` | robustness | 300 | as source | as source | 100 items each of `sata`, `goemotions`, `nlupp`, options shuffled | — |

### General (single-answer) track

Not multi-answer: the check that a trained model keeps the base's general decision quality (gates G2–G4, and the
trainability check of [D18](decisions.md)). Each question is asked in its own type and scored by accuracy,
chance-corrected accuracy, log-loss and calibration error. It is a fast proxy for the [Decision
Index](https://github.com/apolinario/decision-index), not a replacement: the public board (its maintainers' full run)
and a submission at release give the comparable number ([D19](decisions.md)).

| track | items | type | options | source, licence |
|---|---|---|---|---|
| `mmlu_pro` | 300 | Choice | 3–10 | TIGER-Lab/MMLU-Pro test, MIT |
| `bbh` | 300 | Choice | 2–18 | BIG-Bench Hard @9ee07bd, the 23 fixed-answer tasks (5,507 items, as the Decision Index), MIT; BIG-bench canary: never train on it |
| `anli` | 300 | Choice | 3 | facebook/anli test r1–r3, CC BY-NC 4.0 (evaluation only) |
| `hellaswag` | 300 | Choice | 4 | Rowan/hellaswag validation, MIT |
| `clinc150` | 300 | Choice | 151 | clinc/oos-eval @828f809, test + out-of-scope test, CC BY 3.0 |
| `boolq` | 300 | Noul | yes / no | google/boolq validation, CC BY-SA 3.0 |
| `sst5` | 300 | Score | 5 levels | SetFit/sst5 test, research use |

Sizes are fixed random subsets (seed 0) of each test split. SATA options are written "A. text" so the 39 items with
repeated option texts are kept. `bzaf bench prepare` is deterministic; the file hashes are in
[benchmark-v0-manifest.json](benchmark-v0-manifest.json) (rebuild and compare to check you have the same items).

## Protocol

- Each model is read out once per track with its existing question types (see [E01](../experiments/E01-readout-baselines/)):
  one yes/no per option with every option listed (`noul_ctx`; on `wide`, plain `noul`, the usual fan-out), one Choice
  over the options (`pick`), one Choice "how many apply?" (`count`), and the native `set` type where a model has one.
- Untrained predictors turn the readouts into answers (yes/no thresholded and Platt-tuned, Choice + asked count,
  Choice + dataset count prior, native set as shipped, and the oracle "ranking + true count" ceiling). Our trained
  model is scored the same way, with its own answers.
- Each track is split 30 / 70 into dev and test by a hash of the item id. Anything fitted (Platt scaling, the dataset
  count prior, thresholds) uses dev only; every number reported is on test.
- 95 % bootstrap CIs on every metric; comparisons between predictors or models are paired by item
  (`bzaf bench compare`), and the macro average over headline tracks weighs each track equally.

## Metrics

Plain-language reasons for each are in the project history; definitions are in [`metrics.py`](../src/bzaf/metrics.py).

| question | metrics |
|---|---|
| Is the chosen set right? | exact-set accuracy, example F1, Jaccard, micro F1 |
| How many, or which ones? | count accuracy, mean absolute count error, mean answer size vs gold |
| Can its probabilities be trusted? | set log-loss; calibration error of the predicted set's probability (10 equal-size bins); selective automation: share of items answerable at 90 % and 95 % exact-set accuracy, area under the risk-coverage curve |
| Does it hold up? | order stability (answer unchanged after shuffling, Jaccard of the two answers); seconds per item and example F1 against the number of options (`wide`) |
| Comparable with SATA-Bench? | their EM (leaves out empty answers), JI, CtDif, CtDifAbs, RStd (position bias), on `sata` |

Headline summary per track: exact-set and example F1 for four reference answers (yes/no per option tuned, Choice +
dataset count, native set as shipped, ranking + true count). At 200 options exact-set is near 0 for every model; there
the example F1, the log-loss and selective automation carry the result.

## Running it

```bash
uv sync --extra data                                   # ecthr and unfair_tos load through Hugging Face datasets
uv run bzaf bench prepare                              # -> data/bench-v0/ (about 4,900 items + 300 shuffled)
git diff --no-index docs/benchmark-v0-manifest.json data/bench-v0/manifest.json   # same hashes = same items

M=kev-4b                                               # a model endpoint, as in cloud/README.md
uv run bzaf bench readout --base-url $URL --model $M --limit 5      # pilot: 5 items per track
uv run bzaf bench readout --base-url $URL --model $M --concurrency 16
uv run bzaf bench score runs/bench-v0/$M --out experiments/E01b-family-check/results/$M
uv run bzaf bench compare runs/bench-v0/decision-2.0-nox-4b runs/bench-v0/kev-4b --predictor pick+true_count
uv run bzaf bench compare runs/bench-v0/ours runs/bench-v0/decision-2.0-nox-4b --predictor native@top1   # no-regression
```

Add `--with-set` for models with a native set type (Vela 2.0). Readouts resume where they stopped and retry failed
items. Rough size: about 115k questions per model for the multi-answer tracks (2–3 × E01) plus 2,100 for the general
track, a few dollars on an L40S. `--tracks mmlu_pro,bbh,...` runs a subset, e.g. only the general track after a
training run.

## Known limits of v0

- English only; one long-input track (ECtHR) and one wide track, which is synthetic. No item is both 200 options and
  8k tokens.
- `unfair_tos`, `ecthr` and the Hugging Face general tracks load without a pinned revision; the manifest hashes catch
  any change.
- The general track is small (300 items per set, ±5 points per set; its mean is tighter) and some base models may
  have trained on these sources. That does not bias a base-vs-ours comparison on the same items, but its absolute
  numbers are not comparable with other models' published ones.
- GoEmotions labels are noisy (raters often disagree), so its ceiling is low for every model.
- ECtHR facts are cut to ~6k tokens, which can remove the facts behind a violation; the cut is recorded per item.
