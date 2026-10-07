# Experiments

One folder per experiment: `E<NN>-<short-name>/`.

Each `README.md` is written **before** the experiment runs and holds:

1. **Question** — what we want to learn.
2. **Setup** — models, data (with sizes and seeds), exact commands.
3. **Pre-registered decision rule** — which result leads to which next step. Change it only before running, and
   say so in the log.
4. **Results** — filled in afterwards: the summary table (commit `results/*.md`; raw outputs stay in `runs/`, which
   is not committed), what we concluded, and what changed in the plan (with a [decisions](../docs/decisions.md) entry
   if a decision changed).

| ID | Question | Status |
|---|---|---|
| [E01](E01-readout-baselines/) | How good are existing models at multi-answer, and does knowing the count help? Which base model? | done: G1 passed, base = Kev |
| [E01c](E01c-native-set/) | Is the count still the bottleneck for a shipped, trained per-option set head (Vela 2.0 4B)? | pre-registered |
| [E02](E02-count-head/) | Does a trained count head on Kev-0.8B beat the best untrained predictor on unseen datasets? | pre-registered |
| E01b | Which base family, Kev or Decision 2.0 (at 4B now, re-checked at 9B before E04)? Its readouts on benchmark v0 are also the model study | planned |
| E03 | 4B on the chosen family with data v1; count head vs sigmoid; data ablations; ships as v0.1 | planned |
| E04 | 9B with data v2 | planned |
