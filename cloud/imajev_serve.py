"""Imajev behind a TypeSafe-compatible endpoint on Modal, for E01 readouts (`bzaf readout --base-url <url>`).

    modal deploy cloud/imajev_serve.py                   # imajev-4b on an L40S -> prints https://<workspace>--bzaf-imajev-serve.modal.run
    curl -L --max-time 1200 <url>/v1/models              # wait for the cold start (first time: downloads ~9 GB, captures graphs)
    modal app stop bzaf-imajev                           # take it down when the readout is done

Settings, read at deploy time: IMAJEV_SIZE (2b, 4b or 9b; default 4b), IMAJEV_ADAPTER_REV (Hub revision of the adapter;
default main, printed at start-up so results can record it), BZAF_GPU (comma-separated preference list; default L40S then
H100), BZAF_FLA=1 (also install flash-linear-attention for faster Qwen3.5 DeltaNet kernels; off by default because it is
not tested with Imajev's pinned transformers).

Serving choices, so the comparison with Kev stays fair: one option order (--rotations 1, Kev does not average orders
either), Imajev's shipped calibration file (Kev applies its fitted temperature too), --fast (CUDA graphs, same decisions
as the eager path, per Imajev's docs). --max-input-tokens is raised from 4096 to 8192 so long SATA items are answered
rather than refused; note this goes beyond Imajev's training length.

Imajev's server answers requests one at a time (a lock around the GPU), so readout concurrency above ~4 only hides
network latency. The URL is public while the app runs and there is no API key: stop the app after each readout.
"""
import os
import subprocess

import modal

IMAJEV_REF = "ccf586d43d2a580319b6535c893668904d909eb9"   # github.com/mohit67890/imajev commit (2026-10-01)
SIZE = os.environ.get("IMAJEV_SIZE", "4b")
ADAPTER_REV = os.environ.get("IMAJEV_ADAPTER_REV", "main")
GPU = os.environ.get("BZAF_GPU", "L40S,H100").split(",")
FLA = os.environ.get("BZAF_FLA", "0") == "1"
BUNDLE = {"2b": "artifacts/model.json", "4b": "artifacts/model-qwen4b.json", "9b": "artifacts/model-qwen9b.json"}[SIZE]
PORT = 8765

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .run_commands(f"git clone https://github.com/mohit67890/imajev.git /imajev && cd /imajev && git checkout {IMAJEV_REF}",
                  "cd /imajev && pip install -e '.[serve,torch-text]'")
)
if FLA:
    image = image.pip_install("flash-linear-attention==0.5.2", "triton>=3.7.1")
image = (
    image.env({"HF_HOME": "/cache/hf", "HF_HUB_DISABLE_PROGRESS_BARS": "1", "PYTHONUNBUFFERED": "1",
          "IMAJEV_SIZE": SIZE, "IMAJEV_ADAPTER_REV": ADAPTER_REV, "BZAF_GPU": ",".join(GPU), "BZAF_FLA": "1" if FLA else "0"})
)
cache = modal.Volume.from_name("bzaf-model-cache", create_if_missing=True)
app = modal.App("bzaf-imajev")


@app.function(image=image, gpu=GPU, volumes={"/cache": cache}, cpu=4, memory=32768, timeout=3600, scaledown_window=300)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=PORT, startup_timeout=1800)
def serve():
    from huggingface_hub import HfApi, snapshot_download

    # Base model: Imajev's own pinned Qwen3.5 checkpoint, written into its bundle file. Cached on the volume after the first run.
    subprocess.run(["python", "scripts/download_model.py", "--model", SIZE], cwd="/imajev", check=True)
    repo = f"mohit67890/imajev-{SIZE}"
    sha = HfApi().model_info(repo, revision=ADAPTER_REV).sha
    adapter = snapshot_download(repo, revision=sha, local_dir=f"/cache/adapters/imajev-{SIZE}-{sha[:8]}")
    cache.commit()
    print(f"imajev-{SIZE}: code {IMAJEV_REF[:8]}, adapter {repo}@{sha[:8]}", flush=True)
    subprocess.Popen(
        ["python", "scripts/playground/server.py", "--backend", "torch", "--model-bundle", BUNDLE,
         "--adapter", adapter, "--calibration", f"{adapter}/calibration.json", "--model-name", f"imajev-{SIZE}",
         "--rotations", "1", "--fast", "--max-input-tokens", "8192", "--host", "0.0.0.0", "--port", str(PORT)],
        cwd="/imajev", env={**os.environ, "PYTHONPATH": "src:scripts"},
    )
