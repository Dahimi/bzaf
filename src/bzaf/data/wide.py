"""Wide synthetic probe: one order, a catalogue of K product options (K = 10, 50, 100 or 200), and "which of these
products are in the order?". Exact gold, any count from 0 to 6, and close distractors (same product in another colour
or material), so options must be read, not just matched by noun.

The task is easy on purpose: it isolates what changes with the number of options (cost, and whether the count and
the selection hold up at 200), not reasoning. It is a probe, not a headline track.
"""
from __future__ import annotations

import random

from ..schema import Item

COLOURS = ["black", "white", "red", "blue", "green", "grey", "yellow", "orange", "purple", "brown", "pink", "navy"]
MATERIALS = ["ceramic", "steel", "wooden", "glass", "cotton", "leather", "bamboo", "plastic"]
NOUNS = ["mug", "lamp", "backpack", "notebook", "water bottle", "phone stand", "desk mat", "cushion", "plant pot",
         "wall clock", "cutting board", "picture frame", "shoe rack", "laundry basket", "coat hanger", "pen holder",
         "serving tray", "candle holder", "bread box", "spice rack"]
CATALOGUE = [f"{c} {m} {n}" for n in NOUNS for m in MATERIALS for c in COLOURS]  # 1,920 products
QUESTION = "Which of these products are in the order?"
SIZES = (10, 50, 100, 200)


def _item(rng: random.Random, k: int, idx: int) -> Item:
    in_order = rng.sample(CATALOGUE, rng.randint(1, 6))
    shown = [p for p in in_order if rng.random() < 0.75]  # some ordered products are not among the options: counts 0..6
    near = [c for p in in_order for c in CATALOGUE if c != p and c.split(" ", 2)[2] == p.split(" ", 2)[2]]
    distractors = rng.sample(sorted(set(near) - set(in_order)), min(len(near), k // 3))
    rest = [c for c in rng.sample(CATALOGUE, k * 2) if c not in in_order and c not in distractors]
    options = (shown + distractors + rest)[:k]
    rng.shuffle(options)
    order = {"order_id": f"W{idx:05d}", "lines": [{"product": p, "quantity": rng.randint(1, 3)} for p in in_order]}
    return Item(id=f"wide:{k}:{idx}", dataset="wide", state=order, question=QUESTION, options=options,
                gold=[j for j, o in enumerate(options) if o in in_order], meta={"k": k})


def load_wide(n_per_size: int = 75, seed: int = 0, sizes: tuple[int, ...] = SIZES, limit: int | None = None) -> list[Item]:
    rng = random.Random(seed)
    items = [_item(rng, k, i) for k in sizes for i in range(n_per_size)]
    return items[:limit] if limit else items
