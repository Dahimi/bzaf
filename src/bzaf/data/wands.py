"""WANDS, the Wayfair product-search relevance set (Chen et al. 2022), MIT: 480 furniture and home queries, each with
human-judged products (Exact, Partial, Irrelevant), up to thousands per query.

Two items per query: which products match the query exactly (Exact vs Irrelevant; Partial left out, as unsure), and
which are at least partly relevant (Exact or Partial vs Irrelevant). Options are product names with the product
class as description.
"""
from __future__ import annotations

import csv

from ..schema import Item
from ._util import fetch

BASE = "https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/"
QUESTIONS = {
    "exact": ("Which of these products match the search query exactly?", {"Exact"}, {"Irrelevant"}),
    "partial": ("Which of these products are at least partly relevant to the search query?", {"Exact", "Partial"}, {"Irrelevant"}),
}


def _rows(name: str):
    csv.field_size_limit(1 << 24)
    with fetch(BASE + name, f"wands-{name}").open(encoding="utf-8") as f:
        yield from csv.DictReader(f, delimiter="\t")


def load_wands() -> list[Item]:
    products = {r["product_id"]: (r["product_name"].strip(), r["product_class"].strip()) for r in _rows("product.csv")}
    queries = {r["query_id"]: r["query"].strip() for r in _rows("query.csv")}
    labels: dict[str, list[tuple[str, str]]] = {}
    for r in _rows("label.csv"):
        labels.setdefault(r["query_id"], []).append((r["product_id"], r["label"]))
    items = []
    for qid, judged in labels.items():
        for key, (question, pos, neg) in QUESTIONS.items():
            names, desc, gold, seen = [], [], [], set()
            for pid, lab in judged:
                if pid not in products or lab not in pos | neg:
                    continue
                name, cls = products[pid]
                if not name or name in seen:
                    continue
                seen.add(name)
                if lab in pos:
                    gold.append(len(names))
                names.append(name)
                desc.append(cls or None)
            if len(names) >= 2:
                items.append(Item(f"wands:{qid}:{key}", "wands", f"Search query: {queries[qid]}", question, names, gold,
                                  {"descriptions": desc}))
    return items
