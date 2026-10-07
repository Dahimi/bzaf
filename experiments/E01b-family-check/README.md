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

## Results

*Not run yet.*
