"""Training and adapter checks on Modal. Our code and benchmark v0 (data/bench-v0, built with `bzaf bench prepare`)
are uploaded; weights are cached on the bzaf-model-cache volume, runs are written to the bzaf-runs volume.

    # 1. our adapter against the released model's recorded answers (real weights; CPU FP32, GPU FP32 and bf16)
    BZAF_FLA=0 modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Eos-0.8B --checks cpu
    modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Eos-0.8B --checks cuda,cuda-bf16

    # 2. a training run (a smoke run first: tiny mixture, few steps, 20 items per track)
    modal run cloud/train_modal.py --name e02-smoke --args "--scale 0.02 --max-steps 20 --eval-limit 20 --eval-base"
    modal run --detach cloud/train_modal.py --name e02 --args "--eval-base"   # --detach: survives a closed terminal
    modal run --detach cloud/train_modal.py --name e02 --args "--eval-base --resume"   # after an interruption
    modal run --detach cloud/train_modal.py --name e02-sigmoid --args "--set-loss sigmoid"   # E02 ablation
    modal run --detach cloud/train_modal.py --name e02b --args "--mix e02b"                  # E02b: the diverse mixture
    # E03a (Nox-4B): adapter check (CPU part without the GPU-only kernels), then speed tests (40 steps, no evaluation)
    BZAF_FLA=0 modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Nox-4B --checks cpu
    modal run cloud/train_modal.py::golden --model vllm-sr/Decision-2.0-Nox-4B --checks cuda,cuda-bf16
    BZAF_GPU=H100 modal run cloud/train_modal.py --name speed-h100 \
        --args "--base vllm-sr/Decision-2.0-Nox-4B --mix e02b --scale 0.05 --max-steps 40 --eval-tracks none"

    # 3. fetch the evaluation records and score them like any readout
    modal volume get bzaf-runs e02/eval runs/e02/
    uv run bzaf bench score runs/e02/eval/ours --out experiments/E02-count-head/results/ours
    uv run bzaf bench score runs/e02/eval/base --out experiments/E02-count-head/results/base

Settings, read at launch: BZAF_GPU (default L40S; H100 for 4B and up), BZAF_FLA=0 to skip flash-linear-attention (the
fast Gated DeltaNet kernels; without them transformers uses its slower reference implementation).
"""
import os
import shlex
import subprocess

import modal

GPU = os.environ.get("BZAF_GPU", "L40S")
FLA = os.environ.get("BZAF_FLA", "1") == "1"

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch==2.14.1", "transformers==5.19.0", "peft==0.21.2", "safetensors==0.8.0", "tokenizers==0.23.2",
    "huggingface_hub==1.33.0", "datasets>=3.3", "numpy>=1.26",
)
if FLA:
    image = image.pip_install("flash-linear-attention==0.5.2")
image = (
    image.env({"HF_HOME": "/cache/hf", "HF_HUB_DISABLE_PROGRESS_BARS": "1", "PYTHONUNBUFFERED": "1",
               "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
               "BZAF_RAW": "/cache/raw"})  # downloaded source files, kept on the cache volume (E02b: ~1.5 GB)
    .add_local_dir("data/bench-v0", "/root/bench-v0")
    .add_local_python_source("bzaf")
)
cache = modal.Volume.from_name("bzaf-model-cache", create_if_missing=True)
runs = modal.Volume.from_name("bzaf-runs", create_if_missing=True)
app = modal.App("bzaf-train")


# timeout: Modal's maximum (24 h); a run that hit a shorter one would lose its evaluation
@app.function(image=image, gpu=GPU, volumes={"/cache": cache, "/runs": runs}, cpu=8, memory=65536, timeout=24 * 3600)
def train(name: str, args: str = "") -> dict:
    from bzaf.train.trainer import main

    argv = ["--out", f"/runs/{name}", "--bench", "/root/bench-v0", *shlex.split(args)]
    print("args:", argv, flush=True)
    subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], check=False)
    try:
        main(argv, on_checkpoint=runs.commit)   # checkpoints and finished evaluation files survive an interruption
    except Exception as e:  # re-raised as plain text: the local side has no torch to unpickle torch exceptions
        import traceback

        raise RuntimeError(f"{type(e).__name__}: {e}\n{traceback.format_exc()[-4000:]}") from None
    finally:
        cache.commit()
        runs.commit()
    return {"name": name}


@app.function(image=image, gpu=GPU, volumes={"/cache": cache}, memory=65536, timeout=3600)  # 4B in FP32 on CPU: ~16 GB
def golden(model: str = "vllm-sr/Decision-2.0-Eos-0.8B", checks: str = "cpu,cuda,cuda-bf16") -> list[dict]:
    """`checks`: cpu (FP32, the reference's own setting; needs BZAF_FLA=0, as the flash-linear-attention kernels are
    GPU-only), cuda (FP32), cuda-bf16 (the training setting)."""
    import json

    from bzaf.train.decision2 import golden_check

    results = []
    # CPU FP32 is the reference's own setting (expect ~1e-6); GPU FP32 and bf16 differ by kernel numerics, as the
    # runtime's own CPU and ROCm references do (up to ~1.5e-3 for Eos)
    settings = {"cpu": ("cpu", False), "cuda": ("cuda", False), "cuda-bf16": ("cuda", True)}
    for device, autocast in (settings[c] for c in checks.split(",")):
        r = golden_check(model, device=device, autocast=autocast)
        print(json.dumps({k: v for k, v in r.items() if k != "questions"}), flush=True)
        for qid, q in r["questions"].items():
            print(f"  {qid}: max |diff| {q['max_abs_diff']:.2e}  expected {q['expected']}  ours {q['ours']}", flush=True)
        results.append(r)
    cache.commit()
    return results


@app.local_entrypoint()
def main(name: str = "e02-smoke", args: str = "--scale 0.02 --max-steps 20 --eval-limit 20 --eval-base"):
    print(train.remote(name, args))
