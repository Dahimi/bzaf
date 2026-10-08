"""Training rows for E02 (and the template for data v1).

Two kinds of row:
  set      a multi-answer question (our "multi" type) with its gold set; loss −log P(gold set) (count + selection)
  distill  a single-answer question (Choice / Noul / Score) with no label in the loss; loss KL(base ‖ model), so the
           model keeps the base's answers on general questions

Nothing here comes from a held-out track of benchmark v0 (SATA, NLU++, ECtHR, UNFAIR-ToS) or a general-track test
split; GoEmotions, synthetic and wide rows use the train split / other seeds of tracks that are in-domain by design.
Rows whose state also appears in benchmark v0 are dropped.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..schema import Item, read_items

E02_SIZES = {  # rows per source
    "goemotions": 4000, "goemotions_merged": 2000, "dbpedia_merged": 3000, "synthetic": 4000, "wide": 1000,
    "boolq_distill": 3000, "hellaswag_distill": 3000, "sst5_distill": 3000, "dbpedia_distill": 2000,
}


@dataclass
class TrainRow:
    id: str
    source: str
    loss: str                 # "set" or "distill"
    state: Any
    question: dict            # System One question, or {"type": "multi", ...}
    gold: list[int]           # option indices (set rows: the gold set; distill rows: the label, for reporting only)


def multi_question(item: Item) -> dict:
    desc = item.meta.get("descriptions") or [None] * len(item.options)
    return {"type": "multi", "instructions": item.question, "criteria": dict(zip(item.options, desc))}


def native_question(item: Item) -> dict:
    qtype = item.meta.get("qtype", "choice")
    if qtype == "noul":
        return {"type": "noul", "instructions": item.question}
    if qtype == "score":
        return {"type": "score", "instructions": item.question, "criteria": list(item.options)}
    desc = item.meta.get("descriptions") or [None] * len(item.options)
    return {"type": "choice", "instructions": item.question, "criteria": dict(zip(item.options, desc))}


def shuffled(item: Item, rng: random.Random) -> Item:
    """Options in a random order (the model must not learn positions)."""
    order = list(range(len(item.options)))
    rng.shuffle(order)
    meta = dict(item.meta)
    if "descriptions" in meta:
        meta["descriptions"] = [meta["descriptions"][i] for i in order]
    gold = set(item.gold)
    return Item(item.id, item.dataset, item.state, item.question, [item.options[i] for i in order],
                [j for j, i in enumerate(order) if i in gold], meta)


def merged(items: list[Item], n: int, rng: random.Random, name: str, question: str, label: str,
           k_range: tuple[int, int], option_range: tuple[int, int] | None = None) -> list[Item]:
    """Multi-answer items made of 1..k single items: the state lists the texts, the gold is the union of their labels.
    With `option_range`, each item offers a random subset of the label set (sometimes without some or all gold
    labels, which gives "none" and partial cases)."""
    labels = items[0].options
    out = []
    for i in range(n):
        parts = rng.sample(items, rng.randint(*k_range))
        gold = sorted({parts_item.options[g] for parts_item in parts for g in parts_item.gold})
        options = list(labels)
        if option_range:
            m = rng.randint(*option_range)
            keep = [g for g in gold if rng.random() < 0.85]
            rest = [o for o in labels if o not in keep]
            options = keep + rng.sample(rest, max(0, min(len(rest), m - len(keep))))
        rng.shuffle(options)
        state = "\n\n".join(f"{label} {j + 1}:\n{p.state}" for j, p in enumerate(parts))
        out.append(Item(f"{name}:{i}", name, state, question, options, [j for j, o in enumerate(options) if o in gold]))
    return out


def eval_states(bench_dir: str | Path) -> set[str]:
    """Every state in benchmark v0, to drop training rows that repeat one."""
    states = set()
    for f in Path(bench_dir).glob("*.jsonl"):
        for it in read_items(f):
            states.add(it.state if isinstance(it.state, str) else json.dumps(it.state, sort_keys=True))
    return states


def build_e02(seed: int = 0, sizes: dict | None = None, bench_dir: str | Path | None = "data/bench-v0",
              loaders: dict[str, Callable[[], list[Item]]] | None = None, log=print) -> list[TrainRow]:
    """The E02 mixture. `loaders` overrides sources (tests use small offline ones)."""
    from ..data import load_goemotions, load_synthetic, load_wide
    from ..data.dbpedia import load_dbpedia
    from ..data.general import load_boolq, load_hellaswag, load_sst5

    sizes = {**E02_SIZES, **(sizes or {})}
    rng = random.Random(seed)
    src = {
        "goemotions": lambda: load_goemotions("train"),
        "synthetic": lambda: load_synthetic(n=sizes["synthetic"], seed=1000 + seed),
        "wide": lambda: load_wide(n_per_size=max(1, sizes["wide"] // 4), seed=1000 + seed),
        "dbpedia": lambda: load_dbpedia("train", limit=40000, seed=seed),
        "boolq": lambda: load_boolq(limit=None, split="train"),
        "hellaswag": lambda: load_hellaswag(limit=None, split="train"),
        "sst5": lambda: load_sst5(limit=None, split="train"),
        **(loaders or {}),
    }
    cache: dict[str, list[Item]] = {}

    def get(name):
        if name not in cache:
            cache[name] = src[name]()
        return cache[name]

    seen = eval_states(bench_dir) if bench_dir and Path(bench_dir).exists() else set()
    rows: list[TrainRow] = []

    def add(items: list[Item], source: str, loss: str, n: int):
        kept = 0
        for it in rng.sample(items, min(n, len(items))):
            key = it.state if isinstance(it.state, str) else json.dumps(it.state, sort_keys=True)
            if key in seen:
                continue
            if loss == "set":
                it = shuffled(it, rng)
                rows.append(TrainRow(it.id, source, "set", it.state, multi_question(it), list(it.gold)))
            else:
                rows.append(TrainRow(it.id, source, "distill", it.state, native_question(it), list(it.gold)))
            kept += 1
        log(f"  {source}: {kept} rows")

    if sizes.get("goemotions"):
        add(get("goemotions"), "goemotions", "set", sizes["goemotions"])
    if sizes.get("goemotions_merged"):
        add(merged(get("goemotions"), sizes["goemotions_merged"], rng, "goemotions_merged",
                   "Which emotions do the authors of these comments express?", "Comment", (2, 3)),
            "goemotions_merged", "set", sizes["goemotions_merged"])
    if sizes.get("dbpedia_merged"):
        add(merged(get("dbpedia"), sizes["dbpedia_merged"], rng, "dbpedia_merged",
                   "Which categories do these entries belong to?", "Entry", (1, 4), option_range=(4, 14)),
            "dbpedia_merged", "set", sizes["dbpedia_merged"])
    for name in ("synthetic", "wide"):
        if sizes.get(name):
            add(get(name), name, "set", sizes[name])
    for name in ("boolq", "hellaswag", "sst5", "dbpedia"):
        if sizes.get(f"{name}_distill"):
            add(get(name), f"{name}_distill", "distill", sizes[f"{name}_distill"])
    rng.shuffle(rows)
    return rows
