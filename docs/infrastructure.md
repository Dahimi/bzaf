# Infrastructure

*Agreed 2026-10-05. See [decisions.md](decisions.md), D8.*

## Where things run

| Work | Where | Why |
|---|---|---|
| Editing, tests, scoring, small checks | the Mac | fast loop, no cost |
| Model readouts (E01 and evaluations) | **Modal** (serverless GPUs) | per-second billing, scale to zero, Kev ships a Modal script |
| Training (E02 onwards) | **Modal** | same; one function per run, weights cached on a volume |
| Long continuous jobs (many hours) | RunPod pod, if ever needed | cheaper per hour when a GPU stays busy |

The Mac (M3, 18 GB) proved too tight for 4B models: ~8 GB of weights, a ~16 GB load peak, and Kev on Metal answers one
request at a time. On CUDA, Kev batches up to 64 concurrent requests.

## Where things live

| What | Home | Notes |
|---|---|---|
| Code | git (GitHub) | `main`; experiments on branches only when risky |
| Public benchmark data | rebuilt from source by `bzaf prepare` (fixed seeds) | nothing to upload; cloud jobs run `prepare` themselves |
| Our datasets (training mixes, own use-case data, frozen synthetic sets) | private Hugging Face dataset repos | versioned; licence and provenance in the dataset card |
| Base weights | Hugging Face Hub, cached on Modal volumes (`kev-hf-cache`, `bzaf-model-cache`) | downloaded once per volume |
| Our checkpoints | Hugging Face model repos (private until release) | |
| Training metrics, configs, curves | Weights & Biases (from E02) | readouts are scored locally in seconds, so E01 needs no tracker |
| Raw readouts | `runs/` locally (not in git) | |
| Summaries, decisions | git: `experiments/*/results/*.md`, `docs/decisions.md` | the record the paper is written from |

The Mac holds working copies only; nothing exists only there.

## Reproducibility rule

Every run records **code commit + dataset revision + base-model revision** (for training, in the W&B run config; for
readouts, in the result file name and the experiment README). Any number in the paper must trace back to those three.

## Costs

GPU prices change; check the providers' pricing pages. Rough orders of magnitude: L4/A10G under $1 per hour, L40S
$1–2, H100 $2–4. Kev's README puts a Kev-4B fine-tuning run at about $1 on an H100. Set a monthly spending limit in
Modal.

## Access from the Claude cloud sandbox

The sandbox where Claude writes code cannot reach Modal or Hugging Face, so cloud commands run from the Mac. To let
Claude launch runs itself: allow Modal's and Hugging Face's domains in the environment's network settings and add
Modal / HF tokens as environment secrets.
