"""SQuAD 2.0 (Rajpurkar et al. 2018), CC BY-SA 4.0 (dataset page; to re-check, docs/data.md): crowd-written questions
on Wikipedia paragraphs, a third of them written to look answerable but unanswerable from the paragraph.

One item per paragraph, asked the other way round: "which of these questions does the passage answer?" Options are
the paragraph's own questions (answerable ones are gold, the unanswerable ones are hard negatives) plus questions on
other paragraphs of the same article whose answers do not occur in this paragraph. Extractive answer spans are not
used (span options would be the held-out reading-comprehension family, D21).
"""
from __future__ import annotations

import json

from ..schema import Item
from ._util import fetch

URL = "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/train-v2.0.json"
QUESTION = "Which of these questions can be answered from the passage?"


def load_squad2(extra_per_paragraph: int = 12) -> list[Item]:
    data = json.loads(fetch(URL, "squad-train-v2.0.json").read_text(encoding="utf-8"))["data"]
    items = []
    for article in data:
        paras = article["paragraphs"]
        for pi, p in enumerate(paras):
            ctx = p["context"]
            gold = [q["question"].strip() for q in p["qas"] if not q["is_impossible"]]
            neg = [q["question"].strip() for q in p["qas"] if q["is_impossible"]]
            extra = []
            for pj, other in enumerate(paras):  # neighbours first: same topic, harder
                if pj == pi:
                    continue
                for q in other["qas"]:
                    answers = [a["text"] for a in q["answers"] or q.get("plausible_answers", [])]
                    if answers and not any(a.lower() in ctx.lower() for a in answers):
                        extra.append((abs(pj - pi), q["question"].strip()))
            extra = [q for _, q in sorted(extra, key=lambda x: x[0])][:extra_per_paragraph]
            options, seen = [], set()
            for q in gold + neg + extra:
                if q and q.lower() not in seen:
                    seen.add(q.lower())
                    options.append(q)
            gold_set = {q.lower() for q in gold}
            g = [i for i, q in enumerate(options) if q.lower() in gold_set]
            if len(options) >= 2:
                items.append(Item(f"squad2:{article['title']}:{pi}", "squad2", f"{article['title'].replace('_', ' ')}\n\n{ctx}",
                                  QUESTION, options, g))
    return items
