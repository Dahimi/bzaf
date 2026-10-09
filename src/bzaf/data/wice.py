"""WiCE (Kamoi et al. 2023), annotations ODC-BY (text: Wikipedia claims, CC BY-SA; cited web pages, Common Crawl
terms): a Wikipedia claim, the sentences of the web page it cites, and every set of sentences that supports it.

One item per claim: the page as numbered sentences, "which sentences support the claim", gold = the union of the
supporting sets; unsupported claims give an empty answer.
"""
from __future__ import annotations

import json

from ..schema import Item
from ._units import window
from ._util import fetch

REVISION = "main"
URL = "https://raw.githubusercontent.com/ryokamoi/wice/{rev}/data/entailment_retrieval/claim/{split}.jsonl"
QUESTION = "Which sentences of the article support this claim? Claim: {claim}"


def load_wice(split: str = "train", budget: int = 20000) -> list[Item]:
    path = fetch(URL.format(rev=REVISION, split=split), f"wice-claim-{split}.jsonl")
    items = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            sents = [s.strip() or "…" for s in r["evidence"]]
            gold = {i for group in r["supporting_sentences"] for i in group if 0 <= i < len(sents)}
            if r["label"] != "not_supported" and not gold:
                continue
            text, keys, g = window(sents, gold, budget, tag="S")
            if not keys:
                continue
            items.append(Item(f"wice:{r['meta']['id']}", "wice", text, QUESTION.format(claim=r["claim"].strip()), keys, g,
                              {"ordered": True}))
    return items
