"""E04a: letter readouts of instruction-tuned LLMs on Modal (bzaf.llm), no training. Benchmark v0 (data/bench-v0) is
uploaded; the bar-wording probe is built on the machine from the cached source files; weights are cached on the
bzaf-model-cache volume and records written to the bzaf-runs volume (resumable: a rerun skips finished items).

    # 1. smoke run: 10 items per track, shared-prefix self-check, letter-mass check (~10 min, < $1)
    modal run cloud/llm_modal.py --model Qwen/Qwen3.5-4B --name e04a-smoke --limit 10
    # 2. full runs (--detach: survives a closed terminal)
    modal run --detach cloud/llm_modal.py --model Qwen/Qwen3.5-4B --name e04a-qwen3.5-4b
    modal run --detach cloud/llm_modal.py --model Qwen/Qwen3.6-27B --name e04a-qwen3.6-27b
    # 3. fetch, then score as in experiments/E04a-llm-count/README.md
    modal volume get bzaf-runs e04a-qwen3.6-27b runs/

Settings, read at launch: BZAF_GPU (default H100; the 27B in bf16 needs ~55 GB), BZAF_FLA=0 to skip
flash-linear-attention (the fast Gated DeltaNet kernels).
"""
import os

import modal

GPU = os.environ.get("BZAF_GPU", "H100")
FLA = os.environ.get("BZAF_FLA", "1") == "1"
TRACKS = "sata,nlupp,ecthr,unfair_tos,synthetic"   # the held-out multi-answer tracks and the clear-rule control

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch==2.14.1", "transformers==5.19.0", "safetensors==0.8.0", "tokenizers==0.23.2", "huggingface_hub==1.33.0",
    "accelerate>=1.10", "datasets>=3.3", "numpy>=1.26",
)
if FLA:
    image = image.pip_install("flash-linear-attention==0.5.2")
image = (
    image.env({"HF_HOME": "/cache/hf", "HF_HUB_DISABLE_PROGRESS_BARS": "1", "PYTHONUNBUFFERED": "1",
               "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True", "BZAF_RAW": "/cache/raw"})
    .add_local_dir("data/bench-v0", "/root/bench-v0")
    .add_local_python_source("bzaf")
)
cache = modal.Volume.from_name("bzaf-model-cache", create_if_missing=True)
runs = modal.Volume.from_name("bzaf-runs", create_if_missing=True)
app = modal.App("bzaf-llm")


@app.function(image=image, gpu=GPU, volumes={"/cache": cache, "/runs": runs}, cpu=8, memory=65536, timeout=24 * 3600)
def readout(model: str, name: str, tracks: str = TRACKS, limit: int = 0, probe: bool = True, revision: str = "") -> dict:
    import hashlib
    import json
    from pathlib import Path

    from bzaf import bench
    from bzaf.data.bar_probe import load_bar_probe
    from bzaf.llm import LLMClient, max_answer_diff
    from bzaf.readout import VARIANTS, build_questions, run_readout
    from bzaf.schema import read_items, write_items

    out = Path("/runs") / name
    try:
        client = LLMClient.load(model, revision=revision or None)
        cache.commit()   # the downloaded weights, for the next run
        cfg = client.lm.config
        info = {"model": model, "revision": revision or "main", "name": client.model, "model_type": cfg.model_type,
                "architectures": cfg.architectures, "params_b": round(sum(p.numel() for p in client.lm.parameters()) / 1e9, 2),
                "dtype": str(next(client.lm.parameters()).dtype)}
        print(json.dumps(info), flush=True)

        # self-check on the GPU numerics: shared-prefix answers vs one full pass per question (exact on CPU in fp32)
        first = next(read_items("/root/bench-v0/sata.jsonl"))
        qs = build_questions(first, [v for v in VARIANTS if v != "noul"])
        print("end of the first prompt (the answer letter comes next):", repr(client.prompt_text(first.state, qs["pick"])[-160:]),
              flush=True)
        shared = client.decide(first.state, qs)["answers"]
        client.share = False
        full = client.decide(first.state, qs)["answers"]
        client.share = True
        diff = max_answer_diff(shared, full)
        info["self_check_max_diff"] = diff
        print(f"self-check on {first.id} ({len(qs)} questions): shared prefix vs full passes, max |diff| {diff:.2e}", flush=True)

        for t in tracks.split(","):   # one track at a time, committed after each: an interruption loses little
            bench.readout(client, "/root/bench-v0", out / "bench", tracks=[t], limit=limit or None)
            print("letter mass so far:", json.dumps(client.mass_summary()), flush=True)
            runs.commit()
        if probe:
            for src in ("wands", "esci"):
                items = load_bar_probe(src)
                path = out / "bar-items" / f"bar_{src}.jsonl"
                write_items(items, path)
                info[f"bar_{src}_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                print(f"bar_{src}: {len(items)} items, sha256 {info[f'bar_{src}_sha256']}", flush=True)
                run_readout(client, items[: limit * 2 or None], out / "bar" / f"bar_{src}.jsonl", ["noul_ctx", "pick", "count"])
                runs.commit()
        info["letter_mass"] = client.mass_summary()
        (out / "info.json").write_text(json.dumps(info, indent=2) + "\n")
        print(json.dumps(info["letter_mass"], indent=2), flush=True)
    except Exception as e:  # re-raised as plain text: the local side has no torch to unpickle torch exceptions
        import traceback

        raise RuntimeError(f"{type(e).__name__}: {e}\n{traceback.format_exc()[-4000:]}") from None
    finally:
        cache.commit()
        runs.commit()
    return info


@app.local_entrypoint()
def main(model: str = "Qwen/Qwen3.5-4B", name: str = "e04a-smoke", tracks: str = TRACKS, limit: int = 0, probe: bool = True,
         revision: str = ""):
    print(readout.remote(model, name, tracks, limit, probe, revision))
