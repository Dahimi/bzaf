"""Amazon Shopping Queries (ESCI, Reddy et al. 2022), Apache-2.0: shopping queries with up to ~200 result products,
each manually labelled Exact, Substitute, Complement or Irrelevant. US locale, train split only.

Three items per query: which products match exactly (E vs S, C, I), which are acceptable (E or S vs C, I), and
which would complement what the shopper wants (C vs E, S, I; often none). Options are product titles (shortened).
"""
from __future__ import annotations

from ..schema import Item
from ._util import fetch

BASE = "https://media.githubusercontent.com/media/amazon-science/esci-data/main/shopping_queries_dataset/"
QUESTIONS = {
    "exact": ("Which of these products match the shopping query exactly?", {"E"}),
    "acceptable": ("Which of these products would be acceptable for the shopping query (an exact match or a "
                   "reasonable substitute)?", {"E", "S"}),
    "complement": ("Which of these products are not what the shopper asked for but would go well with it "
                   "(complements)?", {"C"}),
}
TITLE_CHARS = 90


def _short(title: str) -> str:
    title = " ".join(title.split())
    return title if len(title) <= TITLE_CHARS else title[:TITLE_CHARS].rsplit(" ", 1)[0] + " …"


def load_esci(locale: str = "us", split: str = "train", limit_queries: int | None = None) -> list[Item]:
    import pyarrow.parquet as pq

    ex = pq.read_table(fetch(BASE + "shopping_queries_dataset_examples.parquet", "esci-examples.parquet"),
                       columns=["query_id", "query", "product_id", "product_locale", "esci_label", "split"]).to_pandas()
    ex = ex[(ex.product_locale == locale) & (ex.split == split)]
    pr = pq.read_table(fetch(BASE + "shopping_queries_dataset_products.parquet", "esci-products.parquet"),
                       columns=["product_id", "product_title", "product_locale"]).to_pandas()
    titles = dict(zip(pr.product_id[pr.product_locale == locale], pr.product_title[pr.product_locale == locale]))
    del pr
    items = []
    for n, (qid, group) in enumerate(ex.groupby("query_id", sort=True)):
        if limit_queries is not None and n >= limit_queries:
            break
        query = group["query"].iloc[0]
        rows = [(_short(titles[p]), lab) for p, lab in zip(group.product_id, group.esci_label) if isinstance(titles.get(p), str)]
        for key, (question, pos) in QUESTIONS.items():
            names, gold, seen = [], [], set()
            for title, lab in rows:
                if title and title not in seen:
                    seen.add(title)
                    if lab in pos:
                        gold.append(len(names))
                    names.append(title)
            if len(names) >= 2:
                items.append(Item(f"esci:{qid}:{key}", "esci", f"Shopping query: {query}", question, names, gold))
    return items
