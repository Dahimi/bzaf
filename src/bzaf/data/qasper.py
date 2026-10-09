"""Qasper v0.3 (Dasigi et al. 2021), CC BY 4.0: NLP papers with questions written by NLP practitioners; each answer
cites its evidence paragraphs (or is unanswerable).

One item per question: the paper as numbered paragraphs (figure and table captions included), the question "which
paragraphs contain evidence", gold = the union of every annotator's evidence paragraphs; all-unanswerable questions
give an empty answer. Papers longer than the budget keep the gold paragraphs and their neighbours.
"""
from __future__ import annotations

import json
import tarfile

from ..schema import Item
from ._units import window
from ._util import fetch

URL = "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz"
QUESTION = "Which paragraphs of the paper contain evidence needed to answer this question: {q}"


def load_qasper(split: str = "train", budget: int = 20000) -> list[Item]:
    path = fetch(URL, "qasper-train-dev-v0.3.tgz")
    with tarfile.open(path) as tar:
        data = json.load(tar.extractfile(f"qasper-{split}-v0.3.json"))
    items = []
    for paper in data.values():
        units = [p.strip() for sec in paper["full_text"] for p in sec["paragraphs"] if p and p.strip()]
        units += [f["caption"].strip() for f in paper.get("figures_and_tables") or [] if f.get("caption")]
        index = {}
        for i, u in enumerate(units):
            index.setdefault(u, i)
        for q in paper["qas"]:
            gold, answerable, unmatched = set(), False, 0
            for ann in q["answers"]:
                a = ann["answer"]
                if a["unanswerable"]:
                    continue
                answerable = True
                for ev in a["evidence"]:
                    ev = ev.strip()
                    if ev.startswith("FLOAT SELECTED:"):
                        ev = ev[len("FLOAT SELECTED:"):].strip()
                    if ev in index:
                        gold.add(index[ev])
                    else:
                        unmatched += 1
            if unmatched or (answerable and not gold):  # evidence we cannot place: skip rather than mislabel
                continue
            text, keys, g = window(units, gold, budget)
            if not keys:
                continue
            items.append(Item(f"qasper:{q['question_id']}", "qasper", f"Paper: {paper['title']}\n\n{text}",
                              QUESTION.format(q=q["question"].strip()), keys, g, {"ordered": True}))
    return items
