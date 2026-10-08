"""DBpedia-14 (Wikipedia abstracts, 14 classes), CC BY-SA 3.0, Hugging Face `fancyzhx/dbpedia_14`. Training data only:
single-label, combined into multi-answer items by `bzaf.train.data`."""
from __future__ import annotations

from ..schema import Item
from ._util import sample

CLASSES = ["company", "educational institution", "artist", "athlete", "office holder", "means of transportation",
           "building", "natural place", "village", "animal", "plant", "album", "film", "written work"]


def load_dbpedia(split: str = "train", limit: int | None = 20000, seed: int = 0) -> list[Item]:
    from datasets import load_dataset  # optional dependency

    ds = load_dataset("fancyzhx/dbpedia_14", split=split)
    items = [Item(id=f"dbpedia:{split}:{i}", dataset="dbpedia", state=f"{row['title']}: {row['content'].strip()}",
                  question="Which category does this entry belong to?", options=list(CLASSES), gold=[int(row["label"])],
                  meta={"qtype": "choice"})
             for i, row in enumerate(ds)]
    return sample(items, limit, seed)
