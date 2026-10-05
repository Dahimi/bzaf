# E01 — Readout baselines (no training)

**Status:** ready to run · **Hardware:** MacBook Pro M3, 18 GB

## Question

1. How good are existing open decision models at multi-answer questions, using only the question types they
   already support?
2. Is the count approach justified, i.e. does knowing *how many* answers apply turn a model's existing ranking into
   much better answer sets?
3. Which base model do we build on?

## Setup

**Models** (4B class, all serve the TypeSafe-compatible `POST /v1/systemone` format, run one at a time):

| Model | Start the server |
|---|---|
| Kev-4B | in a clone of [jaredpalmer/kev](https://github.com/jaredpalmer/kev): `uv sync --extra serve && uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009` |
| Imajev-4B | see [mohit67890/imajev](https://github.com/mohit67890/imajev) (TypeSafe wire format, self-hosted) |
| Decision 2.0 Nox-4B | see its model card; only after the lineage check (docs/roadmap.md, open items) |
| JevK5-4B (reference only, not a base; lineage) | see [allebee/jevk5](https://github.com/allebee/jevk5) |

If a model does not speak the wire format, add a small adapter rather than changing the readout.

**Data** (fixed subsets, seed 0; `bzaf prepare` downloads and converts):

| Dataset | Items | Options | Answers per item | Why |
|---|---|---|---|---|
| SATA-Bench | 400 | 3–16 | 2–11 | published Jev / open-model exact-set numbers; under-counting |
| GoEmotions (test) | 400 | 28 | mostly 1 | over-selection with yes/no per label |
| UNFAIR-ToS (test) | 800 | 8 | mostly 0 | "none of these" |
| Synthetic orders | 300 | 4–10 | 0–7 | exact gold, positive control |

**Readout** per item, all through existing question types ([`src/bzaf/readout.py`](../../src/bzaf/readout.py)):
`noul` (one yes/no per option), `noul_ctx` (same, with all options listed), `pick` (one Choice over the options),
`count` (one Choice: "how many of these options apply?", 0..K).

**Predictors** scored offline ([`src/bzaf/predictors.py`](../../src/bzaf/predictors.py)), dev/test split 30/70 by
item-id hash, fitting on dev only:

| Name | What it is |
|---|---|
| `noul@0.5`, `noul_ctx@0.5` | today's workaround, without / with the other options visible |
| `noul+platt`, `noul_ctx+platt` | the same, recalibrated on dev (two numbers per dataset) |
| `pick@top1` | today's Choice: always one answer |
| `pick+true_count` | Choice ranking told the true number of answers (upper bound for the count approach) |
| `pick+count`, `noul+count`, `noul_ctx+count` | the count approach untrained: option scores + the model's own count answer |

## How to run (step by step, on the Mac)

**How the pieces fit.** The model and our harness are two separate programs in two terminals. The model runs as a
small local web server (its own repo, its own environment) and listens on a port, e.g. `localhost:8009`. `bzaf
readout` sends it one HTTP request per item, the same format Jev's API uses, and writes the answers to `runs/`.
Nothing is shared but that port. To test another model, stop one server and start the next.

```
Terminal 1 (~/code/kev)                         Terminal 2 (~/code/bzaf)
python -m kev.serve --port 8009   <-- HTTP --   bzaf readout --base-url http://localhost:8009
(model loaded in memory)                         -> runs/e01/<model>/<dataset>.jsonl
```

**Step 0 — prepare the data (once, Terminal 2).**

```bash
cd ~/code/bzaf && git pull && uv sync --extra data
uv run bzaf prepare sata --limit 400
uv run bzaf prepare goemotions --limit 400
uv run bzaf prepare unfair_tos --limit 800      # downloads from Hugging Face
uv run bzaf prepare synthetic --limit 300
```

**Step 1 — start the model server (Terminal 1).** Start with Kev-0.8B: it loads in seconds, needs about 4 GB and
proves the whole pipeline before you spend hours on a 4B.

```bash
cd ~/code && git clone https://github.com/jaredpalmer/kev.git && cd kev   # once
uv sync --extra serve                                                     # once; installs MLX on Apple Silicon
uv run --extra serve python -m kev.serve --run jaredpalmer/kev-0.8b --port 8009
```

The first start downloads the weights from Hugging Face. Wait for the line that starts with `serving jaredpalmer/kev-0.8b`. Leave this
terminal open. To check it from Terminal 2: `curl -s localhost:8009/v1/models | head -c 300`.

**Step 2 — pilot (Terminal 2).** 20 items, to check the format and measure speed:

```bash
uv run bzaf readout --items data/items/sata.jsonl --base-url http://localhost:8009 --model kev-0.8b \
  --out runs/e01/kev-0.8b/sata.jsonl --limit 20
```

It ends with `done: 20 ok, 0 failed, X s per item`. If anything failed, the first error is printed; send it to
Claude, delete the output file, and re-run after the fix. Time estimate for the full run: X seconds × ~1,900 items.

**Step 3 — full run (Terminal 2).** Re-running the same command continues where it stopped (the pilot's 20 items
are skipped), so interruptions cost nothing. `caffeinate -i` keeps the Mac awake.

```bash
M=kev-0.8b
for d in sata goemotions unfair_tos synthetic; do
  caffeinate -i uv run bzaf readout --items data/items/$d.jsonl --base-url http://localhost:8009 --model $M --out runs/e01/$M/$d.jsonl
done
uv run bzaf score runs/e01/$M/*.jsonl --out experiments/E01-readout-baselines/results/$M
```

**Step 4 — next model.** Ctrl+C in Terminal 1, start the next one, set `M` to its name, repeat steps 2–3.

- **Kev-4B:** `--run jaredpalmer/kev-4b`. Loading briefly peaks near 16 GB on an 18 GB Mac (the adapter is merged
  into the base on load), so close other apps first. If it runs out of memory, tell Claude.
- **Imajev-4B, Decision 2.0:** start their servers per their READMEs, on port 8009 or with `--base-url` changed.

**Step 5 — share.** Commit and push `experiments/E01-readout-baselines/results/*.md` (or paste them to Claude).
Raw `runs/` stay local.

If a full run is too slow, drop a variant (`--variants noul_ctx,pick,count`) before dropping items.

## Pre-registered decision rules

- **G1 (count approach justified):** `pick+true_count` minus the best of the four yes/no predictors is at least
  **+5 exact-set points with the 95 % CI above 0** on at least **2 of the 3 real datasets**, for the chosen base.
  - Pass → E02 builds the count head.
  - Fail → direction 2 (one sigmoid per option, options in view) becomes primary; the count head becomes the ablation.
- **Base model:** rank candidates by the mean, over the three real datasets, of exact-set accuracy of their best
  untrained multi-answer predictor. Candidates within each other's CIs are tied; break ties by lineage and licence,
  then by how easily a head can be attached and trained (Kev wins that last one).
- **Signals recorded, not gates:** S2 (`pick+count` vs `pick+true_count`: how far the untrained count is from
  perfect, i.e. the headroom a trained count head must close); S3 (`noul_ctx+count` vs `noul_ctx@0.5`: the count
  dial on top of yes/no); S4 (`noul_ctx` vs `noul`: does listing the options help).

## Results

*Not run yet.* Commit each model's `results/<model>.md` here, then write the conclusion and the G1 / base decision
below, with a [decisions](../../docs/decisions.md) entry.
