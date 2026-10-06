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
remains a candidate second backbone for the paper.
