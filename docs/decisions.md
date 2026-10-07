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
