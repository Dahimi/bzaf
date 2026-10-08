"""Benchmark v0 read out in-process through a trained (or base) Decision 2.0 model: the same questions and record
format as `bzaf bench readout` against a server, so `bzaf bench score / compare` work on the result unchanged."""
from __future__ import annotations

import time
from pathlib import Path

import torch

from ..bench import readout_plan
from ..readout import build_questions, parse_answers
from ..schema import Item, read_items
from .decision2 import Decision2Model, Package, Row, Tokenizer, answer, collate, render_question


def _batches(rows: list[Row], max_tokens: int):
    order = sorted(range(len(rows)), key=lambda i: len(rows[i].ids))
    batch, longest = [], 0
    for i in order:
        longest = max(longest, len(rows[i].ids))
        if batch and longest * (len(batch) + 1) > max_tokens:
            yield batch
            batch, longest = [], len(rows[i].ids)
        batch.append(i)
    if batch:
        yield batch


@torch.no_grad()
def answer_items(model: Decision2Model, pkg: Package, tok: Tokenizer, items: list[Item], variants: list[str],
                 device: str, max_tokens: int = 32768, base: bool = False) -> list[dict]:
    """One readout record per item. `base=True` answers with the LoRA adapters off and the original candidate head."""
    rows, owners, errors = [], [], {}
    for n, it in enumerate(items):
        for key, q in build_questions(it, variants).items():
            try:
                rows.append(render_question(tok, it.state, q, pkg.max_input_tokens))
                owners.append((n, key))
            except ValueError as e:
                errors.setdefault(n, f"{key}: {e}")
    answers: list[dict] = [{} for _ in items]
    t0 = time.perf_counter()
    for idx in _batches(rows, max_tokens):
        batch = {k: v.to(device) for k, v in collate([rows[i] for i in idx], tok.pad_id).items()}
        with torch.autocast(device_type=torch.device(device).type, dtype=torch.bfloat16, enabled=device != "cpu"):
            scores, counts = model.base_forward(batch) if base else model(batch)
        for j, i in enumerate(idx):
            row, (n, key) = rows[i], owners[i]
            z = scores[j, : len(row.keys)].float()
            if row.kind == "multi":
                answers[n][key] = {"type": "multi", "logits": z.tolist(), "count": torch.softmax(counts[j].float(), -1).tolist()}
            else:
                answers[n][key] = answer(pkg, row, z.tolist())
    seconds = time.perf_counter() - t0
    recs = []
    for n, it in enumerate(items):
        rec = {"id": it.id, "dataset": it.dataset, "model": "", "k": len(it.options), "gold": it.gold, "variants": sorted(variants)}
        if "perm" in it.meta:
            rec["perm"] = it.meta["perm"]
        if n in errors:
            rec["error"] = errors[n]
        else:
            rec.update(parse_answers(it, answers[n]))
            rec["latency_ms"] = round(1000 * seconds / max(1, len(items)), 1)  # batch average, not a latency measurement
        recs.append(rec)
    return recs


def run(model: Decision2Model, pkg: Package, tok: Tokenizer, bench: str | Path, out: str | Path, name: str, device: str,
        variants_for: dict[str, list[str]] | None = None, tracks: list[str] | None = None, limit: int | None = None,
        base: bool = False, log=print, on_track=None) -> Path:
    """Write <out>/<track>.jsonl for every part of the benchmark plan, with the given variants per track
    (default: ours = multi on multi-answer tracks, native on the general track)."""
    import json

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    model.eval()
    for items_file, stem, plan_variants in readout_plan(Path(bench), False, tracks):
        if not items_file.exists():
            continue
        if base:
            variants = plan_variants                      # the base model's own question types, as `bench readout`
        elif plan_variants == ["native"]:
            variants = ["native"]
        elif stem.endswith("__fanout"):
            continue                                      # a fan-out readout is a base-model baseline only
        else:
            variants = ["multi"]
        variants = (variants_for or {}).get(stem, variants)
        items = list(read_items(items_file))[:limit]
        target = out / f"{stem}.jsonl"
        if target.exists() and sum(1 for _ in target.open()) == len(items):  # already done (a resumed run)
            log(f"  eval {stem}: kept ({len(items)} items)")
            continue
        recs = answer_items(model, pkg, tok, items, variants, device, base=base)
        tmp = target.with_suffix(".tmp")
        with tmp.open("w") as f:
            for r in recs:
                r["model"] = name
                f.write(json.dumps(r) + "\n")
        tmp.replace(target)
        log(f"  eval {stem}: {len(recs)} items ({','.join(variants)})")
        if on_track:
            on_track()
    return out
