# E01b — base family (Kev or Decision 2.0) and the model study, on benchmark v0

*Pre-registered 2026-10-07, before any benchmark v0 readout. Rule from [D18](../../docs/decisions.md).*

## Questions

1. **Family:** do we build v0.1 on Kev-4B or on Decision 2.0 Nox-4B?
2. **Model study (D17):** how do the leading open decision models do on multi-answer questions, measured the same
   way: Kev-4B, Nox-4B, Vela 2.0 4B (native set type) and, if cheap, Imajev-4B?

## Setup

- Benchmark v0 ([docs/benchmark.md](../../docs/benchmark.md)), all tracks plus `order`.
- Models, each served by its own runtime on Modal ([cloud/README.md](../../cloud/README.md)): `kev-4b`,
  `decision-2.0-nox-4b`, `vela-2.0-4b` (with `--with-set`), optionally `imajev-4b` (`--max-questions 8`; its 128-
  character option-name limit fails some lettered SATA items, which then count as wrong and are reported).
- Part 2 (general quality): the public Decision Index 0.3 board (the maintainers' full run), not a local sample
  (changed before any run, [D19](../../docs/decisions.md)). Board snapshot 2026-10-07: Nox-4B 45.0, Kev-4B 39.5 (v2).
  The benchmark's general track is read out too, for the record and as the baseline for later no-regression checks.

Commands, per model `M` at endpoint `URL`:

```bash
uv run bzaf bench readout --base-url $URL --model $M --limit 5           # pilot
uv run bzaf bench readout --base-url $URL --model $M --concurrency 16    # add --with-set for Vela; includes the general track
uv run bzaf bench score runs/bench-v0/$M --out experiments/E01b-family-check/results/$M
uv run bzaf bench compare runs/bench-v0/decision-2.0-nox-4b runs/bench-v0/kev-4b --predictor pick+true_count \
  > experiments/E01b-family-check/results/nox-vs-kev-ranking.md
```

## Pre-registered decision rule (D18)

Switch the family to Decision 2.0 only if **all** of these hold; otherwise stay with Kev.

1. **General quality:** Nox-4B − Kev-4B on the public Decision Index 0.3 board (full index) is larger than the board's
   own tie threshold, 0.9 points. *Snapshot: +5.5 (45.0 vs 39.5), so this condition holds unless the name mapping
   turns out wrong.*
2. **Multi-answer ranking:** Nox-4B − Kev-4B, exact-set of `pick+true_count` (the ranking our count head builds on),
   macro average over the headline tracks of benchmark v0: the paired 95 % CI does not lie entirely below 0.
3. **Trainability** (only run if 1 and 2 pass): a short LoRA run of Nox-4B with the count head and self-distillation
   to its own original answers, through our trainer's Decision 2.0 adapter, loses at most 1 point on the general
   sample.

Reported for the model study, no decision attached: the full benchmark report per model; the four-reference summary
table side by side; order stability; cost against the number of options; set probabilities (log-loss, calibration,
selective automation) for every predictor that defines them.

## Results (2026-10-08)

Reports: [kev-4b](results/kev-4b.md), [decision-2.0-nox-4b](results/decision-2.0-nox-4b.md),
[vela-2.0-4b](results/vela-2.0-4b.md) (its NLU++ and order tracks were still running when this was written: Vela is
not part of the decision). Paired comparisons: [ranking](results/nox-vs-kev-ranking.md), [general](results/nox-vs-kev-general.md).

**Rule, condition by condition (Nox-4B − Kev-4B):**

| condition | result | holds? |
|---|---|---|
| 1. general quality, public board (> 0.9) | +5.5 (45.0 vs 39.5) | yes |
| 2. multi-answer ranking, `pick+true_count` exact-set, macro over headline tracks (CI not below 0) | **+2.56 [+1.14, +4.00]** (better, not just not worse) | yes |
| our own general track, `native@top1` accuracy, macro (for the record) | +2.66 [+0.49, +4.78] | agrees with the board |
| 3. trainability (≤ 1 point lost after a short LoRA run) | not run yet: needs the trainer | pending |

Per track, Nox ranks better on GoEmotions (+8.4), NLU++ (+9.9) and SATA (+4.0), and worse on synthetic (−3.9), the wide
probe (−2.3) and ECtHR (−3.2, CI includes 0): Kev holds up better on structured and long inputs. On the general track
Nox is ahead on CLINC150 (+12.4, 151 options) and behind on BoolQ (−3.9).

**Reading:** conditions 1 and 2 hold, so Decision 2.0 goes on to the trainability check ([D20](../../docs/decisions.md)).

**Model study (benchmark v0):**
- The count is the bottleneck for all three models on the new tracks too. Best realistic vs ranking + true count,
  exact-set: Nox NLU++ 35.8 vs 62.3, SATA 30.0 vs 54.4, ECtHR 50.7 vs 77.4; Kev NLU++ 26.4 vs 52.4, ECtHR 58.5 vs 80.6.
- Vela's native set, as shipped, is below its own Choice + dataset count on every real track (SATA 27.4 vs 29.5,
  ECtHR 35.0 vs 56.7, UNFAIR-ToS 74.0 vs 88.2).
- Vela keeps less general quality than its base on our general track too (chance-corrected mean 53.0 vs Nox 62.3), the
  same direction as the board (31.6 vs 42.6 on 0.2.1): the general track detects forgetting.
- Option-order stability: one yes/no per option at 0.5 changes its answer set after a shuffle on 32–87 % of items
  (NLU++ worst); Choice-based answers change on 3–32 %; Vela's native set on 30–44 %.
- Wide probe: too easy for quality (tuned yes/no stays at F1 ≈ 1.0 up to 200 options); its timings were taken at
  concurrency 16 on a shared server, so they show the trend (Nox fan-out 2.4 × the one-pass time at 200 options) but
  are not latency measurements. A clean latency run at concurrency 1 is needed for the paper.

Open: Nox's order track has 99 failed NLU++ items (re-run with `--max-questions 8 --concurrency 4`); Vela's run is
finishing.
