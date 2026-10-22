# E04a — Does a bigger LLM count well without training, and does its count follow the wording?

*Pre-registered 2026-10-22, before any run. No training in this experiment.*

## Question
1. **Size:** without any training, does an instruction-tuned LLM of ~27B give a usable answer count, either asked
   ("how many of these options apply?") or summed from its per-option yes/no answers? Is it clearly better than at 4B?
2. **Wording:** when only the question's strictness changes ("match exactly" vs "at least partly relevant"), does the
   model's count move the way the gold count does?

Why now (see [D24](../../docs/decisions.md)): at 4B, the untrained base's own "how many" answer counted better than our
trained count head (E03a: SATA rank correlation 0.71 vs 0.21). Geuter et al. 2026 ("Releasing the Inner Jev",
arXiv 2610.17205) find that the plain letter readout of instruction-tuned LLMs reaches Jev's level at 27–31B with no
training, and that zero-shot decision accuracy keeps rising with size (Qwen3.5: 76.8 at 4B, 86.5 at 27B). What
stays open from E03a: the count on tasks whose labels follow a convention the item does not state (UNFAIR-ToS,
ECtHR). Question 2 tests whether stating the bar in the question is a usable zero-shot interface.

## Setup
- **Models** (instruction-tuned, read as they are, thinking off, no temperature):
  - `Qwen/Qwen3.6-27B`, the 27B the paper evaluates.
  - `Qwen/Qwen3.5-4B`, the 4B control with the same readout. The size comparison also changes the generation
    (3.5 → 3.6); if C1 passes and that matters, `Qwen/Qwen3.5-27B` is the follow-up.
  - Reference only: Decision 2.0 Nox-4B records from E01b (its own trained head, a different readout).

  Licences to confirm on the model cards (expected Apache-2.0). Inference only: no output of these runs trains
  anything.
- **Readout** ([`src/bzaf/llm.py`](../../src/bzaf/llm.py)): each question is one chat prompt in the SemIf / paper
  format.
  - System message as in the paper; user message `{"evidence", "criterion", "options": [{"letter", "description"}]}`.
  - The answer is the softmax of the next-token logits over the option letters (A–Z, then a–z above 26 options).
  - Questions about one item share a prompt prefix, which is computed once. This is exact on CPU (tests); on the GPU
    the run prints a self-check against full passes.
  - We also record the share of probability on the listed letters (paper: > 99 %).
- **Questions per item**: unchanged from E01/E01b (`bzaf.readout.build_questions`):
  - `noul_ctx`: one yes/no per option, every option listed;
  - `pick`: one Choice;
  - `count`: one Choice over 0..K.
- **Tracks**: the held-out H = SATA, NLU++, ECtHR, UNFAIR-ToS (benchmark v0, test split as in every report), plus
  `synthetic`, the clear-rule control.
- **Bar probe** ([`src/bzaf/data/bar_probe.py`](../../src/bzaf/data/bar_probe.py)): 150 product queries each from
  WANDS and ESCI, with 8 judged products per query. Each query is asked twice with the same options:
  - strict: "match … exactly";
  - loose: "at least partly relevant" (WANDS) or "acceptable (exact or substitute)" (ESCI).

  The question texts are those of the E02b loaders, written before this probe. Gold count, strict → loose: WANDS
  1.03 → 6.64, ESCI 3.93 → 7.27. File sha256 (built 2026-10-22 from the cached sources; the run prints its own):
  `bar_wands` fe40930d…54df, `bar_esci` d0388420…ffb9.
- **Predictors** (all existing, none fitted unless noted):
  - **asked count:** `pick+count` (Choice ranking + the model's "how many" distribution);
  - **summed yes/no:** `noul_ctx@0.5` (each option kept if its yes-probability is above 0.5);
  - **ceiling:** `pick+true_count`;
  - **B:** per track, the better on test of `noul_ctx+platt` and `pick+dev_prior` of the *same* model. These use the
    dev split's labels; choosing on test favours B.
- **Cost** (estimate): smoke < $1; Qwen3.5-4B ~$2–3; Qwen3.6-27B ~$5–10 on one H100, including the first download of
  ~55 GB.

### Commands
```bash
# 1. smoke run: Qwen3.5-4B, 10 items per track + 10 probe pairs (~10 min). Check in the log: self-check max |diff|
#    below 0.05, letter mass above 0.9 for every question type, no failed items.
modal run cloud/llm_modal.py --model Qwen/Qwen3.5-4B --name e04a-smoke --limit 10
# 2. full runs (independent; can run at the same time)
modal run --detach cloud/llm_modal.py --model Qwen/Qwen3.5-4B --name e04a-qwen3.5-4b
modal run --detach cloud/llm_modal.py --model Qwen/Qwen3.6-27B --name e04a-qwen3.6-27b
# 3. fetch and score
modal volume get bzaf-runs e04a-qwen3.5-4b runs/
modal volume get bzaf-runs e04a-qwen3.6-27b runs/
mkdir -p runs/nox && tar xzf experiments/E01b-family-check/results/nox-4b-records.tgz -C runs/nox
R=experiments/E04a-llm-count/results; mkdir -p $R
for m in qwen3.5-4b qwen3.6-27b; do
  uv run bzaf bench score runs/e04a-$m/bench --out $R/$m; cp runs/e04a-$m/info.json $R/$m-info.json
done
for P in pick+count noul_ctx@0.5; do   # C1: 27B vs 4B, same predictor; C2: 27B without labels vs the 27B's own B
  uv run bzaf bench compare runs/e04a-qwen3.6-27b/bench runs/e04a-qwen3.5-4b/bench --predictor $P > $R/c1-$P.md
  uv run bzaf bench compare runs/e04a-qwen3.6-27b/bench runs/e04a-qwen3.6-27b/bench --predictor $P \
    --predictor-b noul_ctx+platt,pick+dev_prior --only sata,nlupp,ecthr,unfair_tos > $R/c2-$P.md
done
uv run python experiments/E04a-llm-count/analyze.py qwen3.5-4b=runs/e04a-qwen3.5-4b qwen3.6-27b=runs/e04a-qwen3.6-27b \
  nox-4b=runs/nox > $R/counts.md   # count accuracy and correlation; the bar probe (C3)
```

## Predictions (written before the runs)
1. **SATA and NLU++:** the 27B is clearly better than 4B. SATA exact-set with the asked count goes from ~30 (Nox-4B:
   29.8) to 35–45, still well below the true-count ceiling.
2. **ECtHR and UNFAIR-ToS:** little change, far below B. The labelling convention is not in the item.
3. **Summing yes/no beats asking "how many"** on most tracks. Counting in one forward pass is weak even at 27–31B (the
   paper's "counting traps" family).
4. **Bar probe:** the count moves the right way for most pairs but recovers only part of the gold shift.

## Pre-registered criteria and decision rule
Paired bootstrap, 95 % CI, exact-set on the test split. Two label-free predictors are tested (asked count and summed
yes/no); a criterion passes if it holds for either, which is two looks and is reported as such.

- **C1 (size):** the 27B minus Qwen3.5-4B, same predictor: SATA ≥ +5 points with CI above 0, and synthetic not worse
  (CI lower bound above −3; it may already be at ceiling).
- **C2 (without labels vs with):** the 27B's label-free predictor minus its own B: CI above 0 on SATA *and* on NLU++.
  ECtHR and UNFAIR-ToS are reported, not gated (prediction 2).
- **C3 (wording):** for the 27B, on WANDS *and* ESCI, the asked or the summed count is at least 1 higher for the loose
  question than for the strict one in ≥ 70 % of pairs.

| outcome | next step |
|---|---|
| C1 and C2 pass | Zero-training counting from a bigger LLM works on clear-rule tasks. Write up the recipe (two or three questions per item, no training). The bar question decides whether to test it on fresh tasks with criteria written from their annotation guidelines. |
| C1 passes, C2 fails | Size helps but labels still win on clear-rule tasks. Write up the recipe with that limit. C3 decides as below. |
| C1 fails | Size does not fix one-pass counting. Write up the 4B zero-training recipe and close bzaf. |
| C3 passes | A stated bar works zero-shot. Next: 2–3 fresh multi-label tasks with published guidelines, criteria written from the guidelines only (no frequencies), pre-registered. |
| C3 fails | Stated bars do not work without training. The only remaining idea is contrastive bar training (same item, different wording, different answer); decide then, closing is the default. |

Not gates, recorded: the letter mass per question type (a type with mean below 0.9 is flagged and its results
questioned) and the self-check difference. If the 27B's letter mass or self-check fails, the run is fixed and
repeated before anything is concluded.

## Results
*(to fill after the runs)*
