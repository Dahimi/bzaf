# Roadmap

*Revised 2026-10-06 (D11–D15). Each phase ends with a gate. A failed gate is a result, not a delay: it redirects the
plan before money or weeks are spent. Experiments live in [`experiments/`](../experiments/), one folder each,
pre-registered before they run.*

| Phase | Work | Model | Gate | Budget envelope |
|---|---|---|---|---|
| 1 ✅ | [E01](../experiments/E01-readout-baselines/) readout baselines | Kev 0.8B/4B, Imajev 4B | G1 passed: the count is the bottleneck | ~$5 (spent) |
| 2 | [E02](../experiments/E02-count-head/) count head, stage-A-lite data, own trainer | Kev-0.8B (dev base) | **G2:** beats E01 baselines on held-out sets, no single-answer regression | ~$15 |
| 2b (parallel) | E01b release-base comparison | Kev-9B vs Decision 2.0 Lux-9B (and their 4B) | Pre-registered rule picks the release base (D12) | ~$20 |
| 3 | Data v1 (stages A–B) + E03 on the release base at 4B: count head vs sigmoid, data ablations, 200-option / 8k checks | 4B | **G3:** multi-answer gains on held-out families, no regression on general benchmarks | ~$60 (incl. first teacher labels) |
| 4 | Data v2 (stages C–D) + E04: 9B release candidate, long-context training | 9B | **G4:** hard requirements met, no regression; submit to JevBench and the Decision Index | ~$150 |
| 5 | Release: weights (9B + 4B), model card, paper, multi-answer benchmark track | — | — | reserve ~$50–100 |

Total ceiling about $300–400, released gate by gate (D15).

## What each phase answers

**2. E02 — does the method work?** Count head on Kev's per-option scores, trained on a small mix, evaluated on
datasets it never saw. Also the first version of our backbone-agnostic trainer (D11). If G2 fails: diagnose (data,
head, loss) before spending more.

**2b. E01b — which base do we release on?** Inference only, plus one short LoRA run per candidate to measure
forgetting. Measures: general decision quality through our harness on the same items for both (public JevBench items,
the Decision Index subset Kev reports), multi-answer (E01 set), a probe at 200 options and 8k tokens. Rule written
before it runs.

**3. E03 — does it hold at 4B with real data?** First full data pipeline (stages A–B, [data.md](data.md)). Main
ablation: count head vs per-option sigmoid. Data ablations: what each stage adds. No-regression check on general
benchmarks.

**4. E04 — the release candidate.** 9B, stages C–D (mined hard cases, teacher labels), long-context training to meet
the hard requirements. Independent numbers: submissions to JevBench and the Decision Index.

**5. Release.** Weights with model cards (lineage, data licences, evaluation), the harness, the paper, and a proposal
for a native multi-answer track to the benchmark maintainers.

## Paper outline (what each phase feeds)

1. Finding: the count is the bottleneck for multi-answer questions, on two model families (E01).
2. Method: count-conditioned set head, exact and single-pass; ablation vs per-option sigmoid (E02, E03).
3. Data recipe: staged data with ablations (E03, E04).
4. Benchmark: multi-answer track with set calibration and wide (200 options) / long (8k) items.
5. Models: 4B and 9B, general benchmarks matched, multi-answer leading at their size (E04).

## Open items

- Licence check for every training dataset and every teacher model before use (data.md register).
- Decision 2.0 lineage: confirm whether a teacher model was used for its training data.
- Which hosted provider(s) for teachers; confirm their terms allow training on outputs.
