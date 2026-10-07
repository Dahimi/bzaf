"""NLU++ (PolyAI), CC BY 4.0: https://github.com/PolyAI-LDN/task-specific-datasets/tree/main/nlupp

Customer-service utterances in two domains (banking, hotels), each labelled with every intent it expresses. Intents are
modular ("how_long" + "pin" + "arrival" + "new"), so most utterances have several, and 0-6 is the range. The options
are the domain's intents plus the general ones (48 for banking, 40 for hotels), each with the dataset's own
description. Evaluation only: the whole dataset is held out of training.
"""
from __future__ import annotations

import json

from ..schema import Item
from ._util import fetch, sample

REVISION = "57ec275d8078af65b7731c2a98be812d844a6d6b"  # task-specific-datasets commit, 2022-04-29
BASE = f"https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/{REVISION}/nlupp/data"
QUESTION = "Which intents does this customer message express?"
DOMAINS = ("banking", "hotels")


def _describe(text: str) -> str:
    text = text.strip().rstrip("?")
    return text[len("is the intent "):] if text.startswith("is the intent ") else text


def load_nlupp(limit: int | None = None, seed: int = 0) -> list[Item]:
    ontology = json.loads(fetch(f"{BASE}/ontology.json", "nlupp_ontology.json").read_text(encoding="utf-8"))["intents"]
    items = []
    for dom in DOMAINS:
        names = [k for k, v in ontology.items() if dom in v["domain"] or "general" in v["domain"]]
        options = [n.replace("_", " ") for n in names]
        descriptions = [_describe(ontology[n]["description"]) for n in names]
        for fold in range(20):
            rows = json.loads(fetch(f"{BASE}/{dom}/fold{fold}.json", f"nlupp_{dom}_fold{fold}.json").read_text(encoding="utf-8"))
            for i, row in enumerate(rows):
                gold = sorted({names.index(x) for x in row.get("intents", [])})
                items.append(Item(id=f"nlupp:{dom}:{fold}:{i}", dataset="nlupp", state=row["text"], question=QUESTION,
                                  options=options, gold=gold, meta={"domain": dom, "descriptions": descriptions}))
    return sample(items, limit, seed)
