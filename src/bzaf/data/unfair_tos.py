"""UNFAIR-ToS from LexGLUE (terms-of-service sentences, 8 unfair-clause types), CC BY 4.0 per the LexGLUE card.

Most sentences have no label, so this tests "none of these" as much as multi-answer. Published reference: Jev's
per-label yes/no reaches micro-F1 0.50 at a 0.5 threshold and 0.75 with tuned thresholds (arXiv 2609.37647).

Needs the Hugging Face `datasets` package (pip install -e ".[data]"). Not reachable from the cloud sandbox this
loader was written in, so check the first run by hand.
"""
from __future__ import annotations

from ..schema import Item
from ._util import sample

QUESTION = "Which types of potentially unfair clause does this sentence from a terms-of-service contain?"


def load_unfair_tos(split: str = "test", limit: int | None = None, seed: int = 0) -> list[Item]:
    from datasets import load_dataset  # optional dependency

    ds = load_dataset("coastalcph/lex_glue", "unfair_tos", split=split)
    names = list(ds.features["labels"].feature.names)
    items = [
        Item(id=f"unfair_tos:{split}:{i}", dataset="unfair_tos", state=row["text"], question=QUESTION,
             options=names, gold=list(row["labels"]))
        for i, row in enumerate(ds)
    ]
    return sample(items, limit, seed)
