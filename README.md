# bzaf — multi-answer questions for open decision models

Decision models (TypeSafe's Jev and its open alternatives) answer typed questions about a text with probabilities,
in one forward pass. Their Choice question returns exactly one option. Many real questions have several right
answers (tags, intents, policy violations, reasons), and the usual workaround, one yes/no question per option,
over- or under-selects and gives no probability for the answer set as a whole.

**This project builds an open-weights decision model with a native multi-answer question type:** one pass, and out
come the most likely answer sets with calibrated probabilities, each option's probability, the probability of each
number of answers (including none), and count constraints such as "exactly one" or "at most 3".

**The method in one line:** keep the model's existing per-option scores and add a tiny head that predicts *how many*
options apply; together they define an exact distribution over answer sets
([docs/approach.md](docs/approach.md)).

## Status

| Phase | State |
|---|---|
| 1. Readout baselines on existing models ([E01](experiments/E01-readout-baselines/)) | ✅ done: count is the bottleneck (G1 passed); base = Kev |
| 2. [Benchmark v0](docs/benchmark.md) ✅; base family ([E01b](experiments/E01b-family-check/)) ✅ Decision 2.0; trainer v0 ✅; count head on Eos-0.8B ([E02](experiments/E02-count-head/)) | **next** |
| 3. Data v1 + E03 at 4B on the chosen family, then release v0.1 (4B) | planned |
| 4. Data v2 + E04: 9B | planned |
| 5. Release the 9B, paper, benchmark track | planned |

## Documentation

| Doc | What's in it |
|---|---|
| [Project brief](docs/project-brief.md) | goal, deliverables, scope, constraints (incl. the no-Jev-outputs rule) |
| [Approach](docs/approach.md) | the count approach, the maths, why this design, training recipe, limits |
| [Alternatives](docs/alternatives.md) | every approach considered, where each stands, and when parked ones come back |
| [Landscape](docs/landscape.md) | Jev, benchmarks, open models, prior art, where the gap is (dated snapshot) |
| [Roadmap](docs/roadmap.md) | phases, gates, budget envelopes, paper outline |
| [Data plan](docs/data.md) | data stages, teachers, mixing, licence register |
| [Decision log](docs/decisions.md) | what we decided and why |
| [Infrastructure](docs/infrastructure.md) | where things run (Mac vs Modal) and where data, weights and metrics live |
| [Benchmark v0](docs/benchmark.md) | the multi-answer evaluation tracks, protocol and metrics |
| [Experiments](experiments/) | one pre-registered folder per experiment |

## Quickstart

Needs [uv](https://docs.astral.sh/uv/) (`brew install uv` on macOS).

```bash
uv sync --extra data                         # creates .venv from uv.lock (Python 3.12, dev tools included)
uv run pytest                                # maths checked against brute-force enumeration
uv run bzaf prepare synthetic --limit 300    # -> data/items/synthetic.jsonl
```

The full week-1 recipe (start a model server, read out, score) is in
[experiments/E01-readout-baselines](experiments/E01-readout-baselines/); for cloud GPUs see [cloud/](cloud/).

```python
from bzaf import SetDistribution

# option scores (e.g. Choice probabilities) + "how many apply?" probabilities for 0..K
d = SetDistribution.from_scores([0.55, 0.40, 0.03, 0.01, 0.01], [0.0, 0.20, 0.65, 0.15, 0.0, 0.0])
d.top_sets(3)                 # [((0, 1), 0.53), ((0,), 0.11), ((0, 1, 2), 0.08)]
d.marginals()                 # P(option i is in the answer)
d.restrict_count(0, 1).mode() # with an "at most one" constraint
```

## Repository layout

```
docs/                 project documentation (start with the brief)
experiments/          one folder per experiment: pre-registration, then results
cloud/                Modal apps: model endpoints (Kev, Imajev, Vela / Decision 2.0), training (train_modal.py), runbook
src/bzaf/
  setdist.py          answer-set distributions (count x scores), exact in log space
  readout.py          ask a decision server with existing question types (E01)
  predictors.py       untrained multi-answer predictors built from readouts
  metrics.py, score.py  set-level metrics (accuracy, calibration, selective automation), bootstrap CIs, reports
  bench.py            benchmark v0: tracks, readout plan, report, paired model comparison
  train/              trainer: Decision 2.0 adapter (parity-tested), count head, set loss, distillation, in-process eval
  client.py           client for TypeSafe-compatible /v1/systemone servers
  data/               dataset converters: SATA-Bench, GoEmotions, UNFAIR-ToS, NLU++, ECtHR, synthetic, wide
  cli.py              `bzaf prepare | readout | score | bench`
tests/
data/, runs/          generated, not committed
```

## Working rules

- No TypeSafe Jev outputs are used for training, and Jev is never called in experiments (see the brief).
- Every experiment is written down before it runs, with the result that would change the plan.
- Raw outputs stay in `runs/`; commit summaries (`experiments/*/results/*.md`) and decisions.
- Tooling is uv: add dependencies with `uv add` (or `uv add --dev`) and commit `uv.lock`.
- Day-to-day changes go straight to `main`; anything risky or experimental gets its own branch.

## License

To be decided before the first release (Apache-2.0 intended, subject to the base model's licence).
