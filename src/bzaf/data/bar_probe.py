"""Bar-wording probe (E04a): the same products asked twice, once with a strict question and once with a loose one, so
the correct answer count changes only through the wording. Built from two graded product-search sets, with the
question texts of their training loaders (written for E02b, before this probe):

  WANDS (MIT):        strict = Exact,  loose = Exact or Partial
  ESCI (Apache-2.0):  strict = Exact,  loose = Exact or Substitute

Per query, OPTIONS of its judged products are drawn at random (keeping the natural label mix); a query is kept only if
at least one drawn product is in the loose answer but not the strict one, so the two answers differ. Deterministic for
a given seed and source files.
"""
from __future__ import annotations

import random

from ..schema import Item
from . import esci, wands
from ._util import fetch

OPTIONS = 8


def _wands() -> dict[str, tuple[str, list[tuple[str, str | None, str]]]]:
    products = {r["product_id"]: (r["product_name"].strip(), r["product_class"].strip()) for r in wands._rows("product.csv")}
    queries = {r["query_id"]: r["query"].strip() for r in wands._rows("query.csv")}
    out: dict[str, tuple[str, list]] = {}
    for r in wands._rows("label.csv"):
        if r["product_id"] in products and r["query_id"] in queries:
            name, cls = products[r["product_id"]]
            out.setdefault(r["query_id"], (queries[r["query_id"]], []))[1].append((name, cls or None, r["label"]))
    return out


def _esci(locale: str = "us", split: str = "train") -> dict[str, tuple[str, list[tuple[str, str | None, str]]]]:
    import pyarrow.parquet as pq

    ex = pq.read_table(fetch(esci.BASE + "shopping_queries_dataset_examples.parquet", "esci-examples.parquet"),
                       columns=["query_id", "query", "product_id", "product_locale", "esci_label", "split"]).to_pandas()
    ex = ex[(ex.product_locale == locale) & (ex.split == split)]
    pr = pq.read_table(fetch(esci.BASE + "shopping_queries_dataset_products.parquet", "esci-products.parquet"),
                       columns=["product_id", "product_title", "product_locale"]).to_pandas()
    titles = dict(zip(pr.product_id[pr.product_locale == locale], pr.product_title[pr.product_locale == locale]))
    del pr
    out: dict[str, tuple[str, list]] = {}
    for qid, group in ex.groupby("query_id", sort=True):
        rows = [(esci._short(titles[p]), None, lab) for p, lab in zip(group.product_id, group.esci_label)
                if isinstance(titles.get(p), str)]
        out[str(qid)] = (group["query"].iloc[0], rows)
    return out


SOURCES = {  # judged products, state template, (strict question, labels), (loose question, labels)
    "wands": (_wands, "Search query: {}", (wands.QUESTIONS["exact"][0], {"Exact"}),
              (wands.QUESTIONS["partial"][0], {"Exact", "Partial"})),
    "esci": (_esci, "Shopping query: {}", (esci.QUESTIONS["exact"][0], {"E"}),
             (esci.QUESTIONS["acceptable"][0], {"E", "S"})),
}


def load_bar_probe(source: str, n: int = 150, seed: int = 0) -> list[Item]:
    """2 * n items: for each of n queries, the strict item then the loose one (ids end in :strict / :loose)."""
    judged, state, (q_strict, strict), (q_loose, loose) = SOURCES[source]
    pairs = []
    for qid, (query, rows) in sorted(judged().items()):
        seen, uniq = set(), []
        for name, desc, lab in rows:
            if name and name not in seen:
                seen.add(name)
                uniq.append((name, desc, lab))
        if len(uniq) < OPTIONS:
            continue
        drawn = random.Random(f"{seed}:{source}:{qid}").sample(uniq, OPTIONS)
        if any(lab in loose and lab not in strict for _, _, lab in drawn):
            pairs.append((qid, query, drawn))
    pairs = sorted(random.Random(seed).sample(pairs, min(n, len(pairs))), key=lambda p: p[0])
    items = []
    for qid, query, drawn in pairs:
        names, desc = [d[0] for d in drawn], [d[1] for d in drawn]
        meta = {"pair": qid, "descriptions": desc} if all(desc) else {"pair": qid}   # all or none: no "None" in listings
        for bar, question, pos in (("strict", q_strict, strict), ("loose", q_loose, loose)):
            gold = [j for j, d in enumerate(drawn) if d[2] in pos]
            items.append(Item(f"bar_{source}:{qid}:{bar}", f"bar_{source}", state.format(query), question, names, gold,
                              dict(meta, bar=bar)))
    return items
