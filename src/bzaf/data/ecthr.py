"""ECtHR Task A from LexGLUE (European Court of Human Rights cases: which Convention articles were violated), from
the facts of the case. Long inputs: the facts are often several thousand words, so this is the benchmark's long-input
track. The LexGLUE card lists the source data as public (HUDOC); we use it for evaluation only.

The facts are cut to `max_chars` (default 24,000 characters, about 6k tokens) at a paragraph boundary, so every item
fits an 8k-token input with the question and options; `meta.truncated` records whether text was cut.

Needs the Hugging Face `datasets` package (`uv sync --extra data`). Not reachable from the cloud sandbox this loader
was written in, so check the first run by hand.
"""
from __future__ import annotations

from ..schema import Item
from ._util import sample

QUESTION = "Which articles of the European Convention on Human Rights did the court find were violated in this case?"
# LexGLUE label names -> the article titles (Convention and Protocol No. 1)
TITLES = {
    "2": "Article 2: right to life",
    "3": "Article 3: prohibition of torture and inhuman or degrading treatment",
    "5": "Article 5: right to liberty and security",
    "6": "Article 6: right to a fair trial",
    "8": "Article 8: right to respect for private and family life",
    "9": "Article 9: freedom of thought, conscience and religion",
    "10": "Article 10: freedom of expression",
    "11": "Article 11: freedom of assembly and association",
    "14": "Article 14: prohibition of discrimination",
    "P1-1": "Article 1 of Protocol No. 1: protection of property",
}


def _cut(paragraphs: list[str], max_chars: int) -> tuple[str, bool]:
    out, n = [], 0
    for p in paragraphs:
        if n + len(p) + 1 > max_chars:
            return "\n".join(out), True
        out.append(p); n += len(p) + 1
    return "\n".join(out), False


def load_ecthr(split: str = "test", limit: int | None = None, seed: int = 0, max_chars: int = 24_000) -> list[Item]:
    from datasets import load_dataset  # optional dependency

    ds = load_dataset("coastalcph/lex_glue", "ecthr_a", split=split)
    names = list(ds.features["labels"].feature.names)
    options = [TITLES.get(n, f"Article {n}") for n in names]
    items = []
    for i, row in enumerate(ds):
        text, cut = _cut(list(row["text"]), max_chars)
        items.append(Item(id=f"ecthr:{split}:{i}", dataset="ecthr", state=text, question=QUESTION, options=options,
                          gold=list(row["labels"]), meta={"truncated": cut}))
    return sample(items, limit, seed)
