# E04a — Does a bigger LLM count well without training, and does its count follow the wording?

*Pre-registered 2026-10-22, before any run. No training in this experiment. Amended the same day, still before any
run: the 27B runs first and the 4B only if C1 is wanted; the written answer was added as a reference (not a criterion).*

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
  - `Qwen/Qwen3.5-4B`, the 4B control with the same readout. It runs only for C1 (size), after the 27B. The size
    comparison also changes the generation (3.5 → 3.6); if C1 passes and that matters, `Qwen/Qwen3.5-27B` is the
    follow-up.
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
  - `count`: one Choice over 0..K;
  - new, a reference rather than a readout: `write`. The model writes the letters of every option that applies
    ("B, D" or "NONE"), greedily, with thinking off. That is a few generated tokens, not one pass. An answer that does
    not parse counts as wrong, and the share that parse is reported.
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
  - **written:** `write` (the reference above);
  - **ceiling:** `pick+true_count`;
  - **B:** per track, the better on test of `noul_ctx+platt` and `pick+dev_prior` of the *same* model. These use the
    dev split's labels; choosing on test favours B.
- **Cost** (estimate, one H100): 27B smoke ~$1–2 (includes the first download of ~55 GB, cached for the full run);
  27B full run ~$6–12; the optional 4B run ~$2–3.

### Commands
```bash
git pull
# 1. smoke run on the 27B: 10 items per track + 10 probe pairs (~20 min with the download). Check the log:
#    - "self-check … max |diff|" below 0.05 (the shared-prefix shortcut matches full passes on the GPU)
#    - "end of the first prompt" ends with an empty, closed think block
#    - letter mass: mean above 0.9 for count, pick, noulctx; write: "parsed" above 0.9
#    - "0 failed" for every track
modal run cloud/llm_modal.py --model Qwen/Qwen3.6-27B --name e04a-smoke-27b --limit 10
# 2. the full run (--detach: keeps running if the terminal closes; follow it with `modal app logs bzaf-llm`)
modal run --detach cloud/llm_modal.py --model Qwen/Qwen3.6-27B --name e04a-qwen3.6-27b
# 3. fetch and score
modal volume get bzaf-runs e04a-qwen3.6-27b runs/
mkdir -p runs/nox && tar xzf experiments/E01b-family-check/results/nox-4b-records.tgz -C runs/nox
R=experiments/E04a-llm-count/results; mkdir -p $R
uv run bzaf bench score runs/e04a-qwen3.6-27b/bench --out $R/qwen3.6-27b
cp runs/e04a-qwen3.6-27b/info.json $R/qwen3.6-27b-info.json
for P in pick+count noul_ctx@0.5; do   # C2: the 27B without labels vs its own B (dev labels)
  uv run bzaf bench compare runs/e04a-qwen3.6-27b/bench runs/e04a-qwen3.6-27b/bench --predictor $P \
    --predictor-b noul_ctx+platt,pick+dev_prior --only sata,nlupp,ecthr,unfair_tos > $R/c2-$P.md
done
uv run bzaf bench compare runs/e04a-qwen3.6-27b/bench runs/e04a-qwen3.6-27b/bench --predictor write \
  --predictor-b pick+count,noul_ctx@0.5 > $R/written-vs-readouts.md   # the reference: written vs the better readout
uv run bzaf bench compare runs/e04a-qwen3.6-27b/bench runs/nox --predictor pick+count \
  --only sata,nlupp,ecthr,unfair_tos > $R/vs-nox-4b.md                # reference only: different readout
uv run python experiments/E04a-llm-count/analyze.py qwen3.6-27b=runs/e04a-qwen3.6-27b nox-4b=runs/nox \
  > $R/counts.md   # count accuracy and correlation; the bar probe (C3)

# 4. optional, for C1 (size): the 4B with the same readout
modal run --detach cloud/llm_modal.py --model Qwen/Qwen3.5-4B --name e04a-qwen3.5-4b
modal volume get bzaf-runs e04a-qwen3.5-4b runs/
uv run bzaf bench score runs/e04a-qwen3.5-4b/bench --out $R/qwen3.5-4b
for P in pick+count noul_ctx@0.5; do
  uv run bzaf bench compare runs/e04a-qwen3.6-27b/bench runs/e04a-qwen3.5-4b/bench --predictor $P > $R/c1-$P.md
done
uv run python experiments/E04a-llm-count/analyze.py qwen3.5-4b=runs/e04a-qwen3.5-4b qwen3.6-27b=runs/e04a-qwen3.6-27b \
  nox-4b=runs/nox > $R/counts.md
```

## Predictions (written before the runs)
1. **SATA and NLU++:** the 27B is clearly better than 4B. SATA exact-set with the asked count goes from ~30 (Nox-4B:
   29.8) to 35–45, still well below the true-count ceiling.
2. **ECtHR and UNFAIR-ToS:** little change, far below B. The labelling convention is not in the item.
3. **Summing yes/no beats asking "how many"** on most tracks. Counting in one forward pass is weak even at 27–31B (the
   paper's "counting traps" family).
4. **Bar probe:** the count moves the right way for most pairs but recovers only part of the gold shift.
5. **Written answer:** about as good as the better one-pass readout on SATA (within ±3 points). The limit is what the
   model knows and the labelling convention, not the readout.

## Pre-registered criteria and decision rule
Paired bootstrap, 95 % CI, exact-set on the test split. Two label-free predictors are tested (asked count and summed
yes/no); a criterion passes if it holds for either, which is two looks and is reported as such.

- **C1 (size; only if the 4B runs):** the 27B minus Qwen3.5-4B, same predictor: SATA ≥ +5 points with CI above 0, and synthetic not worse
  (CI lower bound above −3; it may already be at ceiling).
- **C2 (without labels vs with):** the 27B's label-free predictor minus its own B: CI above 0 on SATA *and* on NLU++.
  ECtHR and UNFAIR-ToS are reported, not gated (prediction 2).
- **C3 (wording):** for the 27B, on WANDS *and* ESCI, the asked or the summed count is at least 1 higher for the loose
  question than for the strict one in ≥ 70 % of pairs.

| outcome | next step |
|---|---|
| C2 passes | Zero-training counting from the 27B works on clear-rule tasks. Write up the recipe (two or three questions per item, no training). C3 decides whether to test it on fresh tasks with criteria written from their annotation guidelines. |
| C2 fails | Labels still win on clear-rule tasks, even at 27B. Write up the recipe with that limit. C3 decides as below. |
| C1, if run | Passes: size is the reason (up to the 3.5 → 3.6 change). Fails: size does not fix one-pass counting, and the recipe can use a 4B. |
| C3 passes | A stated bar works zero-shot. Next: 2–3 fresh multi-label tasks with published guidelines, criteria written from the guidelines only (no frequencies), pre-registered. |
| C3 fails | Stated bars do not work without training. The only remaining idea is contrastive bar training (same item, different wording, different answer); decide then, closing is the default. |

**Reference, not a gate: the written answer.** Its interpretation is fixed now: written minus the better one-pass
readout (`pick+count` or `noul_ctx@0.5`, chosen per track on test, which favours the readouts).
- If it is ≥ +5 points on SATA or NLU++ with CI above 0, the model knows more than one pass reads out, and a
  trained readout could recover it. That would be the one training direction worth reopening.
- If it is within ±3, the readout is not the bottleneck.

Not gates, recorded: the letter mass per question type (a type with mean below 0.9 is flagged and its results
questioned) and the self-check difference. If the 27B's letter mass or self-check fails, the run is fixed and
repeated before anything is concluded.

## Results (Qwen3.6-27B, run 2026-10-22/23; the optional 4B run was not made, so C1 is open)

Files in [results/](results/): `qwen3.6-27b.md` (full report), `c2-*.md`, `written-vs-readouts.md`, `vs-nox-4b.md`,
`counts.md`, `qwen3.6-27b-info.json`.

**Run checks.**
- All weights loaded (26.9B, bf16).
- Shared-prefix self-check 0.031 (bf16 rounding; 1e-7 on CPU in fp32).
- Written answers 100 % parsed; probe files identical to the checksums above.
- Letter mass ≥ 0.99 on every track and question type except UNFAIR-ToS yes/no (mean 0.954; 63 questions below
  0.5). There the model's top token was " B", the letter with a leading space, which this readout did not count, so
  those answers lean towards "yes". This affects only the yes/no predictors on UNFAIR-ToS, which is not gated.
  The readout now counts both forms (commit after this run).

Exact-set %, test split. B = the better on test of `noul_ctx+platt` and `pick+dev_prior` (dev labels).

| track | asked count (`pick+count`) | summed yes/no (`noul_ctx@0.5`) | written (`write`) | B, 27B | yes/no ranking + true count | Nox-4B, best label-free* | B, Nox-4B* |
|---|---|---|---|---|---|---|---|
| SATA | 8.7 | 29.4 | **34.9** | 33.0 | 59.9 | 29.8 | 30.0 |
| NLU++ | 30.7 | 42.7 | **43.9** | 41.5 | 71.0 | 38.2 | 35.8 |
| ECtHR | 57.6 | 62.7 | 55.8 | **66.8** | 91.7 | 57.6 | 50.7 |
| UNFAIR-ToS | 73.7 | 70.8 | 69.1 | **92.8** | 99.3 | 72.8 | 92.4 |
| macro (H) | 42.7 | 51.4 | 50.9 | 58.5 | 80.5 | 49.6 | 52.2 |
| synthetic | 77.1 | 93.2 | 92.7 | 97.6 | 100.0 | – | – |

\* E03a's table: Nox-4B's best label-free predictor chosen per track on test, and its B. A different readout (its
own trained head); reference only.

Counts on the test split (from `counts.md`), mean predicted vs gold:
- SATA: asked 2.50, summed 3.18, written 3.02, gold 3.60. All under-count. The asked count is exactly right on 15 %
  of items, the summed count on 37 %.
- NLU++: asked 1.34, summed 2.41, written 1.78, gold 1.93.
- ECtHR: asked 1.23, summed 1.52, written 1.52, gold 1.09 (exactly right 61–65 %; Nox-4B 23–39 %).
- UNFAIR-ToS: 0.42–0.46 against a gold mean of 0.13.

### Criteria
- **C1 (size): not run.** Against Nox-4B (different readout), the label-free macro rises from 49.6 to 51.4:
  - NLU++ +4.5 and ECtHR +5.1;
  - SATA ties (29.4 vs 29.8) and UNFAIR-ToS −2.0.

  This compares one fixed 27B predictor with Nox-4B's best per track, chosen on test.
- **C2 (without labels vs with): failed.** Summed yes/no − B:
  - SATA −3.6 [−5.0, −2.1]; NLU++ +1.2 [−2.6, +5.0];
  - not gated: ECtHR −4.2 [−10.6, +2.3], UNFAIR-ToS −21.9 [−25.8, −18.0].

  The asked count is below B everywhere (SATA −24.3).
- **C3 (wording): failed.** Pairs whose count rose by ≥ 1 for the loose wording (asked / summed / written):
  WANDS 79 / 87 / 78 %, ESCI 61 / 63 / 53 %.
  - The count moves the right way on average, but only about halfway. Summed: WANDS 0.92 → 3.78 (gold 1.03 → 6.64);
    ESCI 2.22 → 3.86 (gold 3.93 → 7.27).
  - The model reads "at least partly relevant" and "acceptable" much more narrowly than the annotators did.
- **Reference, written answer:** written − the better one-pass readout:
  - SATA +5.5 [+3.6, +7.7], which meets the pre-registered ≥ +5;
  - NLU++ +1.2 [−2.6, +5.2]; ECtHR −6.9; UNFAIR-ToS −4.6; synthetic −0.5; macro −1.1 [−2.6, +0.5].

### Predictions, checked
1. **Wrong.** The asked count did not improve SATA; it collapsed (8.7) by under-counting.
2. **Half wrong.** ECtHR improved a lot without labels (62.7, within 4.2 of B; Nox-4B's B was 50.7). UNFAIR-ToS did
   not.
3. **Right, strongly.** Summing yes/no beats asking "how many" on SATA (+20.7), NLU++ (+12.0), ECtHR (+5.1) and
   synthetic (+16.1). On UNFAIR-ToS it is −2.9, where its yes/no answers lean towards "yes", see above.
4. **Right.** The count moves the right way, but only partly.
5. **Mostly right.** The written list is equal or worse except on SATA (+5.5).

### Reading
1. **The untrained 27B, asked option by option, is close to the label-using baselines on three of four held-out
   tracks.** It is within ~4 points on SATA and ECtHR and level on NLU++. Its label-free macro (51.4) about equals what
   labels gave at 4B (52.2). A zero-training multi-answer recipe exists:
   - one yes/no question per option, with all options listed;
   - keep the options above 0.5;
   - use the largest model affordable.
2. **Asking "how many" in one pass is the worst method,** even at 27B. The count should come from summing per-option
   judgements, never from a counting question.
3. **What remains is the same two gaps as before.**
   - UNFAIR-ToS's labelling convention: 88 % "none"; −22 vs B.
   - SATA's under-counting: 29 without labels vs 60 with the true count.
4. **Stating the bar in words moves the count but does not pin it down.** "Partly relevant" means less to the model
   than to the annotators. The stated-bar interface failed its test.
5. **Letting the model write its answer helps only on SATA** (+5.5). One-pass readouts are not the main bottleneck.

**Pre-registered consequences.**
- C2 failed: write up the recipe with that limit.
- C3 failed: stated bars do not work without training, and closing is the default.
- The written-answer reference met its trigger on SATA, barely and on one track: a trained readout is the one
  training direction left.

Whether to take it, or to close with the write-up, is decided next (see the discussion after this run).
