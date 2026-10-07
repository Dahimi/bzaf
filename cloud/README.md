# Running on cloud GPUs (Modal)

Why Modal and how data, weights and metrics are organised: [docs/infrastructure.md](../docs/infrastructure.md).

## One-time setup (on your Mac)

```bash
uv tool install modal && modal setup        # opens a browser to sign in; set a monthly spending limit in the Modal dashboard
```

## E01 readouts against a cloud model

The model runs on Modal as an HTTP endpoint; `bzaf readout` runs on your Mac and sends it requests. On a GPU the server
batches concurrent requests, so use `--concurrency`.

### Kev (any size)

`kev_serve.py` is Kev's own Modal script, vendored at a pinned commit. It caches weights and compiled kernels on a
Modal volume, so only the first start of each model is slow.

```bash
export KEV_API_KEY=$(openssl rand -hex 24)          # must be exported BEFORE deploy; keep it in .env (gitignored)
export BZAF_API_KEY=$KEV_API_KEY

KEV_MODEL=jaredpalmer/kev-4b modal deploy cloud/kev_serve.py
URL=https://<workspace>--kev-api.modal.run          # the endpoint (dashboard: Endpoints), NOT the modal.com/apps/... page
curl -s -o /dev/null -w "%{http_code}\n" $URL/v1/models   # without the key: must print 401, else KEV_API_KEY was not exported at deploy
curl -L --max-time 1200 $URL/v1/models -H "authorization: Bearer $KEV_API_KEY"   # wait for the cold start

M=kev-4b
uv run bzaf readout --items data/items/sata.jsonl --base-url $URL --model $M --out runs/e01/$M/sata.jsonl --limit 20 --concurrency 16
for d in sata goemotions unfair_tos synthetic; do
  uv run bzaf readout --items data/items/$d.jsonl --base-url $URL --model $M --out runs/e01/$M/$d.jsonl --concurrency 16
done
uv run bzaf score runs/e01/$M/*.jsonl --out experiments/E01-readout-baselines/results/$M

modal app stop kev                                  # stop paying
```

Other sizes: `KEV_MODEL=jaredpalmer/kev-9b` (deploys on an H100), `jaredpalmer/kev-0.8b` (L4). The GPU follows the model.

### Imajev

```bash
IMAJEV_SIZE=4b modal deploy cloud/imajev_serve.py   # prints https://<workspace>--bzaf-imajev-serve.modal.run
URL=https://<workspace>--bzaf-imajev-serve.modal.run
curl -L --max-time 1800 $URL/v1/models              # first start downloads ~9 GB and captures CUDA graphs
M=imajev-4b
# same readout loop and score command as above, with --concurrency 4 --max-questions 8
# (Imajev answers one request at a time and refuses requests with more than 8 questions)
modal app stop bzaf-imajev
```

No API key on this endpoint: the URL is unguessable but public while the app runs, so stop it when done.

### vLLM Semantic Router models (Vela 2.0, Decision 2.0)

```bash
VLLMSR_MODEL=vllm-sr/Vela-2.0-4B modal deploy cloud/vllmsr_serve.py   # prints https://<workspace>--bzaf-vllmsr-serve.modal.run
URL=https://<workspace>--bzaf-vllmsr-serve.modal.run
curl -L --max-time 1800 $URL/v1/models              # first start downloads the weights and checks their digests
M=vela-2.0-4b                                       # must match the served name (the repo name, lower case)
uv run bzaf readout --items data/items/sata.jsonl --base-url $URL --model $M --out runs/e01/$M/sata.jsonl \
  --variants set,pick,count,noul_ctx --limit 20 --concurrency 8
for d in sata goemotions unfair_tos synthetic; do
  uv run bzaf readout --items data/items/$d.jsonl --base-url $URL --model $M --out runs/e01/$M/$d.jsonl \
    --variants set,pick,count,noul_ctx --concurrency 8
done
uv run bzaf score runs/e01/$M/*.jsonl --out experiments/E01c-native-set/results/$M
modal app stop bzaf-vllmsr
```

Decision 2.0 the same way with `VLLMSR_MODEL=vllm-sr/Decision-2.0-Nox-4B` and `M=decision-2.0-nox-4b` (no `set`
variant: it answers Choice, Noul and Score only). No API key on this endpoint: stop the app when done.

## Good habits

- **Pilot first** (`--limit 20`): it prints seconds per item and the first error, if any.
- **Stop apps when done** (`modal app stop <name>`). Kev's and Imajev's endpoints also scale to zero after 5 idle
  minutes, so a forgotten app costs little, but stopping is free.
- **Failed items are retried** automatically when you re-run the same command (e.g. timeouts during a cold start).
- **One backend per result file.** Don't mix a Mac (MLX) run and a cloud (CUDA) run in the same `runs/` file; their
  probabilities differ slightly. Start the cloud run in a fresh file.
- **Watch spend** in the Modal dashboard (Usage). Expect a few dollars per 4B readout; the pilot's seconds per item ×
  items tells you the run length.
