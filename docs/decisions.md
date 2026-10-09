# Decision log

Short records of decisions and why. Add a new entry rather than editing an old one; mark superseded entries.

## D1 — Focus on the multi-answer question type (2026-10-03)
The deliverable is an open decision model with a native multi-answer question type, plus a report. Dependence between
different questions in one request (linked groups) is out of scope until evidence asks for it.
*Why:* it is the common, concrete use case, and the cross-question problem is smaller on average than the anecdotes
suggest (mean complement violation 0.064) and has cheap workarounds.

## D2 — Primary method: per-option scores plus a count head (2026-10-03)
One extra linear head predicts how many options apply; combined with the existing per-option scores it gives a full
answer-set distribution. Main ablation: count head off (one sigmoid per option, direction 2). Escalation: chain head,
only if residual dependence is shown.
*Why:* it reduces exactly to Choice at count 1, adds ~40k parameters and no extra pass, and targets the documented
failure (wrong number of answers). See [approach.md](approach.md).

## D3 — Base model chosen by measurement, Kev as fallback (2026-10-03)
Candidates: Kev-4B, Imajev-4B, Decision 2.0 Nox-4B (after lineage check), JevK5-4B as a reference only. Chosen in E01
by multi-answer baseline quality, then single-answer strength, licence and lineage of the weights, and how easily a
head can be attached and trained.
*Why:* published scores are on different benchmarks and not comparable; the head is backbone-agnostic.

## D4 — No Jev outputs, no live Jev baseline (2026-10-03)
Never train on Jev outputs; never call Jev's API in experiments; cite published third-party Jev numbers only.
The same rule applies to any teacher whose terms forbid training on its outputs (affects JevK5/Plumb lineage).

## D5 — Local first, cloud for 4B+ training (2026-10-03)
Develop, evaluate and train 0.8B on the MacBook (M3, 18 GB). Move 4B/9B training to rented GPUs as soon as E02 shows
signal, rather than spending days of laptop time. (Kev's README puts a Kev-4B fine-tuning run at about $1 on an
H100.)

## D6 — Metrics (2026-10-03)
Primary: log-loss of the gold answer set (proper, and directly measures what set modelling buys) and exact-set
accuracy. Secondary: example and micro F1, count accuracy, stability under option shuffling, no regression on
single-answer Choice. Bootstrap CIs on everything; paired differences for comparisons.

## D7 — Data (2026-10-03)
Public multi-label datasets with natural-language label names, plus programmatic synthetic data (exact gold, any
count including none, built-in dependence). Held-out evaluation datasets are never trained on. LLM-generated data only
from teachers whose licence allows training use.

## D8 — Cloud GPUs on Modal; data and metrics homes (2026-10-05)
Model readouts and training run on Modal (serverless GPUs, per-second billing). The Mac is for development, tests and
scoring. Data homes: code in git, our datasets in private Hugging Face dataset repos, weights cached on Modal volumes,
training metrics in Weights & Biases (from E02). Details in [infrastructure.md](infrastructure.md). Supersedes D5's
"train 0.8B on the Mac": the Kev-4B readout showed the 18 GB Mac is at its limit (≈16 GB load peak, one request at a
time on Metal), while Kev on CUDA batches up to 64 requests.
*Why Modal over RunPod:* our jobs are short and bursty (readouts, ~$1 training runs), so per-second billing with no idle
or setup time outweighs RunPod's lower hourly rate; Kev already ships a Modal script. RunPod stays the option for long
continuous jobs.

## D9 — G1 passed: build the count head (2026-10-06)
Kev-4B readout (E01): given the true number of answers, the model's existing per-option ranking roughly doubles
SATA exact-set accuracy (25 → 52–54 %) and wins on all three real datasets; yes/no and Choice rankings are about
equal once the count is known; asking the model "how many apply?" does not work (9–18 % count accuracy on real data).
So E02 trains a count head on top of per-option scores, as planned in [approach.md](approach.md). The base model is
still to be chosen after the Imajev-4B readout.

## D10 — Base model: Kev (2026-10-06)
E01 base-model rule (mean best untrained predictor over SATA, UNFAIR-ToS, GoEmotions) ties Kev-4B and Imajev-4B
(51.4 each). Tie broken on trainability, as pre-registered: Kev's pointer head takes the count head directly, its
training code is documented, and its server batches on CUDA without request limits (Imajev: at most 8 questions per
request, option names ≤ 128 characters). E02 develops the count head on Kev-0.8B; E03 scales to Kev-4B. Imajev
remains a candidate second backbone for the paper. *Amended by D11/D12: this is the development base only.*

## D11 — Release target: 9B flagship + 4B companion, LoRA, own trainer (2026-10-06)
Release a 9B model and a 4B companion; develop the method at 0.8B, run ablations at 4B. Train with LoRA (rank 32–64)
plus fully trained heads; full fine-tuning is not needed at ≤ 9B (Kev did the same; it fully fine-tuned only at 27B).
Write our own backbone-agnostic trainer so the release base stays swappable and the recipe is ours to publish.
Goal on general benchmarks: match the base (no regression); improvements are a stretch goal.
*Supersedes D10 in part:* Kev-0.8B is the **development** base for E02; the release base is decided by D12.

## D12 — Release base chosen by E01b, with hard requirements (2026-10-06)
Candidates at 9B: Kev-9B (open training code and data recipe, so replay is possible; validated to 8k) and Decision 2.0
Lux-9B (stronger Decision Index score, 16k context; no public training code or data for the causal models as far as
found). Imajev-9B is excluded by the hard requirements (8 questions per request, option names ≤ 128 characters).
E01b compares them on general decision quality (same harness for both), multi-answer, a 200-option / 8k-token probe,
and forgetting after a short LoRA run, with a rule written before it runs.
Hard requirements for the release model: up to 200 options per question and 8k tokens of input.
*Amended by D18: the comparison is made at 4B first (Kev-4B vs Nox-4B), and repeated at 9B before E04.*

## D13 — Data: staged plan, hosted open-weight teachers (2026-10-06)
Data stages: A breadth (public multi-answer and single-answer sets), B free augmentation, C mined hard cases,
D teacher-labelled data; always dedup, contamination checks against every evaluation set, a licence register, and
whole task families held out for zero-shot claims. Details in [data.md](data.md).
Teachers run through hosted APIs for open-weight models (Together, Fireworks, DeepInfra, OpenRouter, ...), not
self-hosted. Only models whose licence allows training on outputs (e.g. Apache-2.0 / MIT families), and only providers
whose terms allow it; at least two families per labelled set, with agreement used as a soft target. Every generated
row records the teacher model, provider and prompt version.

## D14 — Evidence / context selection is a follow-up project (2026-10-06)
Query-based selection of relevant lines from a page is a real need (RAG context pruning; Provence is the main prior
art but non-commercial), but it is a separate project built on this model. Here it is neither a headline task nor an
evaluation track. Public datasets with long documents and many options may still be used as generic training data,
because the hard requirements (200 options, 8k tokens) need such data.

## D15 — Budget released in phase gates (2026-10-06)
Total ceiling about $300–400 (GPU + teacher APIs), committed phase by phase and only after the previous gate passes.
Planned envelopes in [roadmap.md](roadmap.md). Each run logs its cost; overruns of more than 50 % stop and re-plan.

## D16 — Release order: 4B first, 9B second; own trainer with base adapters (2026-10-07)
Ship a 4B v0.1 as soon as E03 passes, then the 9B. Reason: speed matters in a field that changes weekly, and most
attention goes to "best at 4B" results; the 9B follows with data v2.
Trainer (confirms D11): our own training loop, with one small **adapter per base family** that knows how to load the
checkpoint, render inputs in that family's format, and find the option and decision positions. The Kev adapter imports
Kev's own encoding code as a library (no fork), so continued training sees exactly the format Kev was trained on.
The count head is retrained with each base; what transfers between families is the code and the recipe, not weights.

## D17 — Model study scoped to a handful of leading models (2026-10-07)
Instead of benchmarking every open decision model: Kev, Imajev (both done in E01) and Decision 2.0 (needed anyway
for the base-family choice), optionally one more if cheap. Claim phrased accordingly: "the leading open decision
models we measured", with N stated.

## D18 — Base family chosen at 4B, before E03 (2026-10-07)
Because the 4B ships first (D16), the family choice (Kev or Decision 2.0) moves before E03 and is made at 4B:
Kev-4B vs Nox-4B. Kev-9B vs Lux-9B is checked with the same rule before E04; if it disagrees, the 9B may switch family
(one more adapter). E02 stays on Kev-0.8B either way. Both families go through the same harness: Decision 2.0's runtime
(`vllm-srun`) serves `/v1/systemone`, like Kev's server.
*Rule (details pre-registered in E01b):* switch to Decision 2.0 only if Nox-4B
1. beats Kev-4B on general decision quality (the same fixed, stratified Decision Index sample, run with the Decision
   Index's own harness) with the paired 95 % CI above 0, and is not clearly worse on multi-answer ranking (benchmark
   v0, ranking + true count: the paired CI must not lie entirely below 0); and
2. passes a trainability check: through our trainer's Decision 2.0 adapter, a short LoRA run with the count head and a
   self-distillation loss (KL to its own original answers, because its training data is not public) loses at most
   1 point on the general sample.

Step 2 runs only if step 1 passes. Otherwise Kev.
*Why:* Kev's training data and format code are open, so continued training can replay its data and see its exact
format. Decision 2.0 is ahead on the leaderboard but offers neither, so it must win clearly to be worth that risk.
The same readouts are the model study (D17).

## D19 — General quality from the public Decision Index board; a small general track for our own gates (2026-10-07)
Building the Decision Index locally (≈7 GB of sources, one gated set) is not worth it. For the family check (D18 step 1)
we use the public 0.3 board instead: the maintainers' full run, with the board's own rule that scores less than
0.9 points apart are a tie as the "clearly better" threshold. Snapshot read on 2026-10-07 (names from a transcription
of the board page, matched to models by size; to confirm on the page): Decision 2.0 Nox-4B 45.0; Kev-4B 39.5 (its v2
row; v1 36.7); Lux-9B 45.2; Kev-9B 43.3 (v2). Nox-4B is the highest-scoring model of about 4B on the board.
For our own no-regression gates (G2–G4, the D18 trainability check) benchmark v0 gets a general track: seven public
single-answer test sets, 300 items each, asked in each model's own question types (see
[benchmark.md](benchmark.md)). At release we submit to the board for the comparable number.
*Changes the E01b pre-registration before any run: the Decision Index sample is replaced by the board numbers.*

## D20 — Base family: Decision 2.0, subject to the trainability check (2026-10-08)
E01b: Nox-4B beats Kev-4B on general quality (board +5.5; our general track +2.66 [+0.49, +4.78]) and on multi-answer
ranking (+2.56 [+1.14, +4.00] macro over benchmark v0's headline tracks), so D18 steps 1 and 2 hold. Decision 2.0
becomes the working family: the trainer's first adapter is Decision 2.0, E02 moves from Kev-0.8B to Eos-0.8B (same
family as Nox, so the adapter and recipe are built once), and the trainability check (D18 step 3) runs on Nox-4B
after E02. If it fails, we fall back to Kev, whose adapter is the second one to write.
*Lineage:* the Decision 2.0 cards state Apache-2.0 but not the training data or teacher models. Accepted as a known
risk for development (published by the vLLM Semantic Router project, Apache-2.0 weights); before release we ask the
authors to confirm that no Jev outputs or restricted-teacher outputs were used (D4), and state the answer in our card.

## D21 — Strict family hold-out (2026-10-08)
The held-out tracks keep their whole task families out of training, not only their source datasets, as E02
pre-registered ("no same-family data"). SATA-Bench turned out to be six families (story reading comprehension with
candidate answers, toxicity categories, news topics, MeSH headings, EUR-Lex concepts, business-news event types; see
[benchmark.md](benchmark.md)), so the held-out families are: those six, legal texts (UNFAIR-ToS, ECtHR, EUR-Lex,
contracts), and intent detection in customer messages (NLU++, CLINC150). Boundary: the same decision over the same kind
of label set and the same text genre. Subject tagging of other genres (arXiv, patents, Stack Exchange; DBpedia-14 was
already used in E02) is kept but measured: the first mix trains with and without it and reports SATA per subset.
Sources allowed only under a looser rule (MAVEN, DROP / TAT-QA multi-span, hate-speech target sets) may appear in a
separate "seen-family" run, reported apart, never in the main line. Teacher data must not recreate a held-out family.
Why: only a family-level hold-out tests whether a better data mix fixes E02's failure to transfer across families;
loosening the rule after seeing E02's result would weaken every zero-shot claim.

## D22 — Move the count question to 4B without E02 passing G2 (2026-10-09)
E02 and E02b failed G2 at 0.8B. E02b showed that diverse data makes option selection transfer to an unseen family
(SATA +8.7 with the true count) but that the count stays a learned prior. The untrained bases explain why more 0.8B
variants are low-leverage: judging options on their own, which the count needs, is weak at 0.8B and present at 4B
(SATA, own yes/no per option + Platt: Eos-0.8B 4.2 vs Nox-4B 30.0; own "how many" question, no labels: 6.1 vs 29.8;
NLU++ "how many": 29.0 vs 38.2, above the label-using baseline at 4B). So the next experiment (E03a) is E02b's recipe
and data, unchanged, on Nox-4B. G2's bar is unchanged (and higher at 4B, since the 4B baseline is stronger); a
calibrated gate, pre-registered with E03a, adds the comparison with the same labelled examples the baselines use.
The extra 0.8B runs (count head reading option scores, sigmoid on E02b data, run C) are dropped. Money comes from the
4B phase (~$60); data v1 (many more task families, open-teacher labels) is built in parallel for E03b.
