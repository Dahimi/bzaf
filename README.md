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
| 1. Readout baselines on existing models ([E01](experiments/E01-readout-baselines/)) | harness ready, **next: run on the Mac** |
| 2. Count head on a 0.8B model | planned |
| 3. Scale to 4B in the cloud, ablation | planned |
| 4. Release weights and report | planned |

## Documentation

| Doc | What's in it |
|---|---|
| [Project brief](docs/project-brief.md) | goal, deliverables, scope, constraints (incl. the no-Jev-outputs rule) |
| [Approach](docs/approach.md) | the count approach, the maths, why this design, training recipe, limits |
| [Alternatives](docs/alternatives.md) | every approach considered, where each stands, and when parked ones come back |
| [Landscape](docs/landscape.md) | Jev, benchmarks, open models, prior art, where the gap is (dated snapshot) |
| [Roadmap](docs/roadmap.md) | phases, gates, open items |
| [Decision log](docs/decisions.md) | what we decided and why |
| [Experiments](experiments/) | one pre-registered folder per experiment |

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,data]"
pytest                                   # maths checked against brute-force enumeration
bzaf prepare synthetic --limit 300       # -> data/items/synthetic.jsonl
```

The full week-1 recipe (start a model server, read out, score) is in
[experiments/E01-readout-baselines](experiments/E01-readout-baselines/).

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
src/bzaf/
  setdist.py          answer-set distributions (count x scores), exact in log space
  readout.py          ask a decision server with existing question types (E01)
  predictors.py       untrained multi-answer predictors built from readouts
  metrics.py, score.py  set-level metrics, bootstrap CIs, E01 report
  client.py           client for TypeSafe-compatible /v1/systemone servers
  data/               dataset converters: SATA-Bench, GoEmotions, UNFAIR-ToS, synthetic
  cli.py              `bzaf prepare | readout | score`
tests/
data/, runs/          generated, not committed
```

## Working rules

- No TypeSafe Jev outputs are used for training, and Jev is never called in experiments (see the brief).
- Every experiment is written down before it runs, with the result that would change the plan.
- Raw outputs stay in `runs/`; commit summaries (`experiments/*/results/*.md`) and decisions.

## License

To be decided before the first release (Apache-2.0 intended, subject to the base model's licence).
