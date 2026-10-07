"""vLLM Semantic Router models (Vela 2.0, Decision 2.0) behind their own /v1/systemone endpoint on Modal, for readouts.

    VLLMSR_MODEL=vllm-sr/Vela-2.0-4B modal deploy cloud/vllmsr_serve.py   # -> https://<workspace>--bzaf-vela-2-0-4b-serve.modal.run
    curl -L --max-time 1800 <url>/v1/models                                # wait for the cold start (first time downloads ~9 GB)
    modal app stop bzaf-vela-2-0-4b                                        # take it down when the readout is done

It runs the team's own runtime, `vllm-srun` (github.com/vllm-project/semantic-router, src/model-runtime, Apache-2.0),
installed from a pinned commit. Built-in models are pinned there by revision and file digests and checked before load,
so a readout records exactly which weights answered. Vela 2.0 answers Choice, Noul, Score and native `set` questions
(one sigmoid per option, thresholded by the package's calibration); Decision 2.0 answers Choice, Noul and Score.

Settings, read at deploy time: VLLMSR_MODEL (default vllm-sr/Vela-2.0-4B; e.g. vllm-sr/Decision-2.0-Nox-4B),
VLLMSR_PROFILE (default exact: every request computed alone, the reference numerics; `batching` coalesces concurrent
requests for throughput, with answers that can differ by rounding), BZAF_GPU (comma-separated preference list; default
L40S then H100; the 9B models need 24 GB or more).

No API key on this endpoint: the URL is unguessable but public while the app runs, so stop the app after each readout.
"""
import os
import subprocess

import modal

SR_REF = "246dde1fe20cf66421cc457727178bad0fec3c6c"   # github.com/vllm-project/semantic-router commit (2026-10-07)
MODEL = os.environ.get("VLLMSR_MODEL", "vllm-sr/Vela-2.0-4B")
PROFILE = os.environ.get("VLLMSR_PROFILE", "exact")
GPU = os.environ.get("BZAF_GPU", "L40S,H100").split(",")
PORT = 8765

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .pip_install("torch==2.10.0")
    .run_commands(
        "git clone --filter=blob:none https://github.com/vllm-project/semantic-router.git /sr "
        f"&& cd /sr && git checkout {SR_REF}",
        "pip install /sr/src/model-runtime",
    )
    .env({"HF_HOME": "/cache/hf", "HF_HUB_DISABLE_PROGRESS_BARS": "1", "PYTHONUNBUFFERED": "1",
          "VLLMSR_MODEL": MODEL, "VLLMSR_PROFILE": PROFILE, "BZAF_GPU": ",".join(GPU)})
)
cache = modal.Volume.from_name("bzaf-model-cache", create_if_missing=True)
APP = "bzaf-" + MODEL.split("/")[-1].lower().replace(".", "-")   # one app per model, so several can run at once
app = modal.App(APP)


@app.function(image=image, gpu=GPU, volumes={"/cache": cache}, cpu=4, memory=32768, timeout=3600, scaledown_window=300)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=PORT, startup_timeout=1800)
def serve():
    print(f"{MODEL}: vllm-srun {SR_REF[:8]}, profile {PROFILE}", flush=True)
    subprocess.Popen(
        ["vllm-srun", "serve", MODEL, "--device", "cuda", "--profile", PROFILE, "--cache-dir", "/cache/hf/hub",
         "--served-model-name", MODEL.split("/")[-1].lower(), "--host", "0.0.0.0", "--port", str(PORT)],
    )
