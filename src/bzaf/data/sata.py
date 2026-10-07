"""SATA-Bench (select all that apply), MIT: https://github.com/sata-bench/sata-bench

1,650 questions, 3-16 options, 2-11 correct answers each (never 0 or 1). The Decision Index scores the same file
with one yes/no question per option and exact-set accuracy; Jev's published result there is 26.4 %.

39 of the 1,650 items repeat an option text, which a model cannot tell apart by name. With `lettered=True` (benchmark
v0) every option is written "A. text", as in SATA-Bench's own prompts, so all 1,650 items are kept. The default
(E01) skips those 39 items and uses the bare texts (1,611 kept).
"""
from __future__ import annotations

import json

from ..schema import Item
from ._util import fetch, sample

REVISION = "371dd0c18fe75a96fbbcf2d1507ceeaf0d5263c5"  # the commit the Decision Index pins
URL = f"https://raw.githubusercontent.com/sata-bench/sata-bench/{REVISION}/src/satabench/methods/data/sata_bench_final_2025.json"


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def load_sata(limit: int | None = None, seed: int = 0, lettered: bool = False) -> list[Item]:
    path = fetch(URL, "sata_bench_final_2025.jsonl")
    items = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            row = json.loads(line)
            options = [str(text).strip() for text, _ in row["choices"]]
            if lettered:
                options = [f"{LETTERS[j]}. {o}" for j, o in enumerate(options)]
            elif len(set(options)) != len(options):
                continue  # duplicate option texts cannot be told apart by name
            items.append(Item(
                id=f"sata:{i}",
                dataset="sata",
                state=row["paragraph"],
                question=row["question"],
                options=options,
                gold=[j for j, (_, ok) in enumerate(row["choices"]) if ok],
                meta={"source_subset": row.get("dataset"), "source_index": i},
            ))
    return sample(items, limit, seed)
