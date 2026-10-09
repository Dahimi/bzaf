"""DBpedia-Entity v2 (Hasibi et al. 2017), judgements MIT (entity names from DBpedia, CC BY-SA): entity-search
queries with crowd-judged DBpedia entities (0 irrelevant, 1 relevant, 2 highly relevant).

Two items per query: which judged entities are relevant (1 or 2 vs 0) and which are highly relevant (2 vs 0; the
grade-1 entities are left out of that list). Only judged entities are offered: an unjudged entity is not a known
negative. Options are entity names from the DBpedia identifiers.
"""
from __future__ import annotations

from urllib.parse import unquote

from ..schema import Item
from ._util import fetch

BASE = "https://raw.githubusercontent.com/iai-group/DBpedia-Entity/master/collection/v2/"
QUESTIONS = {
    "relevant": ("Which of these entities are relevant to the search query?", 1),
    "highly": ("Which of these entities are highly relevant to the search query (a central answer, not a side match)?", 2),
}


def _name(uri: str) -> str:
    return unquote(uri.strip("<>").split(":", 1)[1]).replace("_", " ")


def load_dbpedia_entity() -> list[Item]:
    queries = dict(line.rstrip("\n").split("\t", 1) for line in
                   fetch(BASE + "queries-v2.txt", "dbpedia-entity-queries-v2.txt").read_text(encoding="utf-8").splitlines() if line)
    judged: dict[str, dict[str, int]] = {}
    for line in fetch(BASE + "qrels-v2.txt", "dbpedia-entity-qrels-v2.txt").read_text(encoding="utf-8").splitlines():
        qid, _, ent, grade = line.split()
        judged.setdefault(qid, {})[_name(ent)] = max(int(grade), judged.get(qid, {}).get(_name(ent), 0))
    items = []
    for qid, grades in judged.items():
        for key, (question, level) in QUESTIONS.items():
            names = [n for n, g in grades.items() if g >= level or g == 0]
            gold = [i for i, n in enumerate(names) if grades[n] >= level]
            if len(names) >= 2:
                items.append(Item(f"dbpedia_entity:{qid}:{key}", "dbpedia_entity", f"Search query: {queries[qid]}",
                                  question, names, gold))
    return items
