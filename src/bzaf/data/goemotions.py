"""GoEmotions (Reddit comments, 27 emotions + neutral), Apache-2.0:
https://github.com/google-research/google-research/tree/master/goemotions

Test split: 5,427 comments, 85 % with one label. The interesting failure is over-selection: asked one yes/no per
emotion, Jev's 0.80-0.95 answers matched the human label 15 % of the time (arXiv 2609.37647).
"""
from __future__ import annotations

from ..schema import Item
from ._util import fetch, sample

REVISION = "e49bbfe381c9c0e564b937f1c4e163a2273c65cc"  # google-research commit, 2026-10-07 (the data has not changed since 2020)
BASE = f"https://raw.githubusercontent.com/google-research/google-research/{REVISION}/goemotions/data"
QUESTION = "Which emotions does the author of this comment express?"


def load_goemotions(split: str = "test", limit: int | None = None, seed: int = 0) -> list[Item]:
    names = [n.strip() for n in fetch(f"{BASE}/emotions.txt", "goemotions_emotions.txt").read_text().splitlines() if n.strip()]
    path = fetch(f"{BASE}/{split}.tsv", f"goemotions_{split}.tsv")
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text, labels, cid = line.split("\t")
        items.append(Item(
            id=f"goemotions:{cid}",
            dataset="goemotions",
            state=text,
            question=QUESTION,
            options=names,
            gold=[int(x) for x in labels.split(",")],
        ))
    return sample(items, limit, seed)
