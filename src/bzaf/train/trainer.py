"""Training loop: a Decision 2.0 base + LoRA + count head, trained on set rows (−log P(gold set)) and distill rows
(KL to the base's own answers). Writes the adapter, the heads, a JSON-lines log, and the benchmark v0 evaluation of the
trained model (and, with --eval-base, of the untouched base) in readout format, scored like any other model.

    python -m bzaf.train.trainer --base vllm-sr/Decision-2.0-Eos-0.8B --out /runs/e02 --eval-base
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import torch

from .data import E02_SIZES, TrainRow, build_e02
from .decision2 import Decision2Model, Package, Row, render_question
from .losses import distill, set_nll, sigmoid_nll

LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj",
                "gate_proj", "up_proj", "down_proj"]


@dataclass
class TrainConfig:
    base: str = "vllm-sr/Decision-2.0-Eos-0.8B"
    revision: str | None = None
    out: str = "runs/e02"
    bench: str = "data/bench-v0"
    seed: int = 0
    sizes: dict = field(default_factory=lambda: dict(E02_SIZES))
    lora_r: int = 16
    lora_alpha: int = 32
    lr_lora: float = 2e-4
    lr_head: float = 5e-5          # the released candidate head, continued
    lr_count: float = 1e-3         # the new count head (or, with set_loss=sigmoid, the new per-option bias)
    set_loss: str = "count"        # count: count head + exact set NLL; sigmoid: the ablation, one sigmoid per option
    weight_decay: float = 0.0
    epochs: float = 1.0
    max_steps: int | None = None
    warmup_steps: int = 30
    max_tokens: int = 16384        # padded tokens per batch
    distill_weight: float = 1.0
    grad_checkpointing: bool = True    # store layer inputs only, recompute in backward (~10x less memory)
    eval_base: bool = False
    eval_limit: int | None = None  # items per track (smoke tests)
    eval_tracks: list | None = None
    log_every: int = 10
    save_every: int = 200          # steps between checkpoints (adapter, heads, optimizer, step)
    resume: bool = False           # continue from <out>/checkpoint.pt (same data order), or skip to evaluation


@dataclass
class Example:
    row: Row
    loss: str
    gold: list[int]
    source: str


def render_rows(rows: list[TrainRow], pkg: Package, tok, log=print) -> list[Example]:
    out, skipped = [], 0
    for r in rows:
        try:
            out.append(Example(render_question(tok, r.state, r.question, pkg.max_input_tokens), r.loss, r.gold, r.source))
        except ValueError:
            skipped += 1
    if skipped:
        log(f"  skipped {skipped} rows longer than the model limit")
    return out


def make_batches(examples: list[Example], max_tokens: int, rng: random.Random) -> list[list[int]]:
    """Batches of one loss type, similar lengths, at most `max_tokens` padded tokens; in random order."""
    batches = []
    for kind in ("set", "distill"):
        idx = [i for i, e in enumerate(examples) if e.loss == kind]
        rng.shuffle(idx)
        idx.sort(key=lambda i: len(examples[i].row.ids) // 64)  # length buckets, shuffled within
        batch, longest = [], 0
        for i in idx:
            n = len(examples[i].row.ids)
            if batch and max(longest, n) * (len(batch) + 1) > max_tokens:
                batches.append(batch)
                batch, longest = [], 0
            batch.append(i)
            longest = max(longest, n)
        if batch:
            batches.append(batch)
    rng.shuffle(batches)
    return batches


def build_model(cfg: TrainConfig, device: str):
    from peft import LoraConfig, get_peft_model

    pkg = Package.open(cfg.base, revision=cfg.revision)
    tok = pkg.tokenizer()
    dtype = torch.bfloat16 if device != "cpu" else torch.float32
    model = Decision2Model.from_package(pkg, dtype=dtype, device=device)
    model.keep_base()
    model.backbone = get_peft_model(model.backbone, LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_alpha, lora_dropout=0.0,
                                                              target_modules=LORA_TARGETS))
    if cfg.set_loss == "sigmoid":  # the ablation: no count head; z_i + b is each option's own log-odds
        model.count_head.requires_grad_(False)
        model.set_bias = torch.nn.Parameter(torch.zeros((), device=device))
    elif cfg.set_loss != "count":
        raise ValueError(f"set_loss must be count or sigmoid, not {cfg.set_loss!r}")
    if cfg.grad_checkpointing:
        model.backbone.enable_input_require_grads()
        model.backbone.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    return model.to(device), pkg, tok


@torch.no_grad()
def init_set_bias(model, examples: list[Example], tok, device: str, log=print, n: int = 64) -> None:
    """Sigmoid ablation: start the shared bias so that an average option's probability is the training base rate
    (the released head's logits are softmax logits, whose level is arbitrary)."""
    from .decision2 import collate

    sets = [e for e in examples if e.loss == "set"]
    rate = sum(len(e.gold) for e in sets) / max(1, sum(len(e.row.keys) for e in sets))
    sample = sorted(sets[:n], key=lambda e: len(e.row.ids))
    total, count = 0.0, 0
    for i in range(0, len(sample), 8):
        batch = {k: v.to(device) for k, v in collate([e.row for e in sample[i : i + 8]], tok.pad_id).items()}
        with torch.autocast(device_type=torch.device(device).type, dtype=torch.bfloat16, enabled=device != "cpu"):
            scores, _ = model(batch)
        mask = batch["candidate_mask"]
        total += float(scores.float().masked_fill(~mask, 0).sum())
        count += int(mask.sum())
    model.set_bias.fill_(math.log(rate / (1 - rate)) - total / max(1, count))
    log(f"sigmoid ablation: base rate {rate:.3f}, initial bias {model.set_bias.item():.2f}")


def train(cfg: TrainConfig, device: str | None = None, rows: list[TrainRow] | None = None, log=print,
          on_checkpoint=None) -> dict:
    """`on_checkpoint()` is called after every checkpoint and evaluation file (Modal: commit the volume, so an
    interrupted run keeps them)."""
    from . import evaluate
    from .decision2 import collate

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(cfg.seed)
    rng = random.Random(cfg.seed)
    out = Path(cfg.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(asdict(cfg), indent=2))
    model, pkg, tok = build_model(cfg, device)
    log(f"base {cfg.base} ({pkg.manifest.get('model_name')}), device {device}")

    if rows is None:
        log("building the training mixture")
        rows = build_e02(cfg.seed, cfg.sizes, cfg.bench, log=log)
    examples = render_rows(rows, pkg, tok, log)
    log(f"{len(examples)} training rows: " + ", ".join(f"{k} {sum(e.loss == k for e in examples)}" for k in ("set", "distill")))

    groups = [
        {"params": [p for n, p in model.backbone.named_parameters() if p.requires_grad], "lr": cfg.lr_lora},
        {"params": list(model.head.parameters()), "lr": cfg.lr_head},
        {"params": [model.set_bias] if cfg.set_loss == "sigmoid" else list(model.count_head.parameters()),
         "lr": cfg.lr_count},
    ]
    opt = torch.optim.AdamW(groups, weight_decay=cfg.weight_decay)
    batches_per_epoch = len(make_batches(examples, cfg.max_tokens, random.Random(0)))
    total = cfg.max_steps or max(1, int(math.ceil(cfg.epochs * batches_per_epoch)))
    base_lrs = [g["lr"] for g in groups]

    def lr_scale(step):
        if step < cfg.warmup_steps:
            return (step + 1) / cfg.warmup_steps
        return 0.5 * (1 + math.cos(math.pi * min(1.0, (step - cfg.warmup_steps) / max(1, total - cfg.warmup_steps))))

    if cfg.set_loss == "sigmoid":
        init_set_bias(model, examples, tok, device, log)
    ckpt_path = out / "checkpoint.pt"
    trainable = {n: p for n, p in model.named_parameters() if p.requires_grad}
    skip, done = 0, False
    if cfg.resume and ckpt_path.exists():
        ck = torch.load(ckpt_path, map_location=device)
        missing = set(trainable) - set(ck["trainable"])
        if missing:
            raise ValueError(f"checkpoint lacks {len(missing)} parameters, e.g. {sorted(missing)[0]}")
        with torch.no_grad():
            for n, p in trainable.items():
                p.copy_(ck["trainable"][n].to(p.device, p.dtype))
        opt.load_state_dict(ck["optimizer"])
        skip, done = ck["step"], ck.get("done", False)
        log(f"resumed from step {skip}" + (" (training finished; evaluation only)" if done else ""))

    def save_checkpoint(step: int, finished: bool = False) -> None:
        tmp = ckpt_path.with_suffix(".tmp")
        torch.save({"step": step, "done": finished, "optimizer": opt.state_dict(),
                    "trainable": {n: p.detach().cpu() for n, p in trainable.items()}}, tmp)
        os.replace(tmp, ckpt_path)
        if on_checkpoint:
            on_checkpoint()

    model.train()
    log_file = (out / "train_log.jsonl").open("a" if skip else "w")
    step, t0, tokens, window = 0, time.perf_counter(), 0, []
    first = True
    if done:
        step = total
    while step < total:
        batches = make_batches(examples, cfg.max_tokens, rng)
        if first:  # the largest batch first: a run that does not fit in memory fails in its first step, not hours later
            big = max(range(len(batches)), key=lambda b: len(batches[b]) * max(len(examples[i].row.ids) for i in batches[b]))
            batches.insert(0, batches.pop(big))
            first = False
        for idx in batches:
            if step >= total:
                break
            if step < skip:  # resuming: replay the same batch order without computing
                step += 1
                continue
            exs = [examples[i] for i in idx]
            # lengths rounded up to 128: few distinct shapes, so the Gated DeltaNet kernels tune once, not per batch
            batch = {k: v.to(device) for k, v in collate([e.row for e in exs], tok.pad_id, multiple=128).items()}
            for g, lr in zip(opt.param_groups, base_lrs):
                g["lr"] = lr * lr_scale(step)
            with torch.autocast(device_type=torch.device(device).type, dtype=torch.bfloat16, enabled=device != "cpu"):
                scores, counts = model(batch)
                if exs[0].loss == "set":
                    gold = torch.zeros_like(batch["candidate_mask"])
                    for j, e in enumerate(exs):
                        gold[j, e.gold] = True
                    if cfg.set_loss == "sigmoid":
                        loss = sigmoid_nll(scores + model.set_bias, gold, batch["candidate_mask"]).mean()
                        stats = {"set_nll": loss.item()}
                    else:
                        parts = set_nll(scores, counts, gold, batch["candidate_mask"])
                        loss = parts["nll"].mean()
                        stats = {"set_nll": loss.item(), "count_nll": parts["count_nll"].mean().item(),
                                 "select_nll": parts["select_nll"].mean().item()}
                else:
                    with torch.no_grad():
                        base_scores, _ = model.base_forward(batch)
                    kl = distill(scores, base_scores, batch["candidate_mask"]).mean()
                    loss = cfg.distill_weight * kl
                    stats = {"distill_kl": kl.item()}
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_([p for g in groups for p in g["params"]], 1.0)
            opt.step()
            tokens += int(batch["attention_mask"].sum())
            window.append(stats)
            step += 1
            if step % cfg.log_every == 0 or step == total:
                avg = {k: sum(w[k] for w in window if k in w) / max(1, sum(k in w for w in window))
                       for k in {k for w in window for k in w}}
                rec = {"step": step, "of": total, "lr_scale": round(lr_scale(step), 4),
                       "tokens_per_s": round(tokens / (time.perf_counter() - t0)),
                       "eta_min": round((time.perf_counter() - t0) / (step - skip) * (total - step) / 60, 1),
                       **{k: round(v, 4) for k, v in avg.items()}}
                log_file.write(json.dumps(rec) + "\n")
                log_file.flush()
                log(json.dumps(rec))
                window = []
            if step % cfg.save_every == 0 and step < total:
                save_checkpoint(step)
    log_file.close()
    if not done:
        save_checkpoint(total, finished=True)

    model.backbone.save_pretrained(out / "adapter")
    heads = {"head": model.head.state_dict(), "count_head": model.count_head.state_dict()}
    if cfg.set_loss == "sigmoid":
        heads["set_bias"] = model.set_bias.detach().cpu()
    torch.save(heads, out / "heads.pt")
    model.eval()
    log("evaluating the trained model")
    evaluate.run(model, pkg, tok, cfg.bench, out / "eval" / "ours", "ours", device, tracks=cfg.eval_tracks,
                 limit=cfg.eval_limit, log=log, on_track=on_checkpoint)
    if cfg.eval_base:  # after training, so a training failure costs minutes; the base = adapters off + original head
        log("evaluating the base model (untrained baselines)")
        evaluate.run(model, pkg, tok, cfg.bench, out / "eval" / "base", "base", device, tracks=cfg.eval_tracks,
                     limit=cfg.eval_limit, base=True, log=log, on_track=on_checkpoint)
    return {"steps": step, "resumed_from": skip, "seconds": round(time.perf_counter() - t0), "out": str(out)}


def main(argv: list[str] | None = None, on_checkpoint=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in TrainConfig.__dataclass_fields__.values():
        if f.name in ("sizes", "eval_tracks"):
            continue
        kind = type(f.default) if f.default is not None else (int if f.name in ("max_steps", "eval_limit") else str)
        if kind is bool and f.default:
            ap.add_argument(f"--no-{f.name.replace('_', '-')}", dest=f.name, action="store_false")
        elif kind is bool:
            ap.add_argument(f"--{f.name.replace('_', '-')}", action="store_true")
        else:
            ap.add_argument(f"--{f.name.replace('_', '-')}", type=kind, default=f.default)
    ap.add_argument("--scale", type=float, default=1.0, help="multiply every source size (0.05 for a smoke run)")
    ap.add_argument("--eval-tracks", default=None, help="comma list of benchmark tracks to evaluate (default all)")
    a = ap.parse_args(argv)
    kw = {k: v for k, v in vars(a).items() if k in TrainConfig.__dataclass_fields__ and k != "eval_tracks"}
    cfg = TrainConfig(**kw, sizes={k: max(1, int(v * a.scale)) for k, v in E02_SIZES.items()},
                      eval_tracks=a.eval_tracks.split(",") if a.eval_tracks else None)
    print(train(cfg, os.environ.get("BZAF_DEVICE"), on_checkpoint=on_checkpoint))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
