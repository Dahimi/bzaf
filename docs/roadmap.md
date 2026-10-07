# Roadmap

*Revised 2026-10-07 (D16–D18: the 4B ships first, the base family is chosen at 4B). Each phase ends with a gate. A
failed gate is a result, not a delay: it redirects the plan before money or weeks are spent. Experiments live in
[`experiments/`](../experiments/), one folder each, pre-registered before they run.*

| Phase | Work | Model | Gate | Budget envelope |
|---|---|---|---|---|
| 1 ✅ | [E01](../experiments/E01-readout-baselines/) readout baselines | Kev 0.8B/4B, Imajev 4B | G1 passed: the count is the bottleneck | ~$5 (spent) |
| 2a | Benchmark v0; E01b family check and model study | Kev-4B, Imajev-4B, Decision 2.0 Nox-4B | D18 rule picks the family | ~$20 |
| 2b (parallel) | Trainer v0 (Kev adapter); [E02](../experiments/E02-count-head/) count head, stage-A-lite data | Kev-0.8B (dev base) | **G2:** beats E01 baselines on held-out sets, no single-answer regression | ~$15 |
| 3 | Data v1 (stages A–B) + E03 at 4B on the chosen family: count head vs sigmoid, data ablations; **release v0.1 (4B)** | 4B | **G3:** multi-answer gains on held-out families, no regression on general benchmarks, 200-option / 8k probe passes | ~$60 (incl. first teacher labels) |
| 4 | Data v2 (stages C–D) + E04: 9B, long-context training; family re-checked at 9B (D18) | 9B | **G4:** hard requirements met, no regression; submit to JevBench and the Decision Index | ~$150 |
| 5 | Release the 9B, paper, multi-answer benchmark track | — | — | reserve ~$50–100 |

Total ceiling about $300–400, released gate by gate (D15).

## What each phase answers

**2a. Benchmark v0 and E01b — what do we measure, and which family do we build on?** Benchmark v0: all 1,650
SATA-Bench items (lettered options, also scored with SATA-Bench's own metrics), the E01 datasets, and more multi-answer
datasets across domains. New metrics: set calibration, selective automation, option-order stability, cost and quality
against the number of options. E01b runs Kev-4B, Imajev-4B and Nox-4B through it (the model study, D17), plus one fixed
Decision Index sample on Kev-4B and Nox-4B for general quality, then applies the D18 rule. The trainability check runs
only if Nox-4B wins on quality.

**2b. E02 — does the method work?** Count head on Kev-0.8B's per-option scores, trained on a small mix, evaluated on
datasets it never saw. First version of our trainer, with the Kev adapter (D16). If G2 fails: diagnose (data, head,
loss) before spending more.

**3. E03 and v0.1 — does it hold at 4B with real data?** First full data pipeline (stages A–B, [data.md](data.md)).
Main ablation: count head vs per-option sigmoid. Data ablations: what each stage adds. No-regression check on general
benchmarks, and the 200-option / 8k probe. If G3 passes, the 4B ships as v0.1.

**4. E04 — the 9B.** Stages C–D (mined hard cases, teacher labels), long-context training to meet the hard
requirements with margin. Family re-checked at 9B with the D18 rule. Independent numbers: submissions to JevBench and
the Decision Index.

**5. Release.** Weights with model cards (lineage, data licences, evaluation), the harness, the paper, and a proposal
for a native multi-answer track to the benchmark maintainers.

## Paper outline (what each phase feeds)

1. Finding: the count is the bottleneck for multi-answer questions, on the leading open decision models we measured,
   including a released, trained native set head (E01, E01c, E01b).
2. Method: count-conditioned set head, exact and single-pass; ablation vs per-option sigmoid (E02, E03).
3. Data recipe: staged data with ablations (E03, E04).
4. Benchmark: multi-answer track with set calibration, selective automation, order stability, and wide (200 options) /
   long (8k) items.
5. Models: 4B and 9B, general benchmarks matched, multi-answer leading at their size (E03, E04).

## Open items

- Licence check for every training dataset and every teacher model before use (data.md register).
- Decision 2.0 lineage: confirm whether a teacher model was used for its training data.
- Which hosted provider(s) for teachers; confirm their terms allow training on outputs.
- Vela 2.0 (same team as Decision 2.0, released 2026-10-06) has a native Set type (one sigmoid per option,
  thresholded): measured first in [E01c](../experiments/E01c-native-set/), then in the model study on benchmark v0.
