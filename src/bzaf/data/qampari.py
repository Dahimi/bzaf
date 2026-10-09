"""QAMPARI (Amouyal et al. 2022), CC0 (proof sentences from Wikipedia, CC BY-SA): list questions over Wikipedia with
5-200 answers each, every answer with a proof sentence. The train set was generated from Wikidata and tables, and its
answer lists are known to be incomplete.

Unlike the other sources, a QAMPARI row is assembled at draw time (`QampariPool`): the options are entity names,
the context lists one proof sentence per offered option ("name: sentence", shuffled), so each
option is checked against its own evidence. Distractors are answers to other questions of the
same template (same relation, another subject entity), never "same type, not in the gold list" (that would turn
missing gold into false negatives); a distractor whose proof mentions the question's own entity is skipped.
"""
from __future__ import annotations

import ast
import json
import random
import re
import zipfile
from dataclasses import dataclass

from ..schema import Item
from ._util import fetch

URL = "https://aggreg-qa.s3.amazonaws.com/qampari.zip"
PROOF_CHARS = 300
NUMERIC = re.compile(r"[\d\s\-–/.,:]+")


@dataclass
class Question:
    qid: str
    text: str
    entity: str
    template: str
    answers: list[tuple[str, str]]  # (answer name, proof sentence)


def _clip(s: str) -> str:
    s = " ".join(s.split())
    return s if len(s) <= PROOF_CHARS else s[:PROOF_CHARS].rsplit(" ", 1)[0] + " …"


def _clean(proof: str, entity: str) -> bool:
    """A usable proof: plain text (no table or HTML debris), long enough, and naming the question's subject."""
    return (len(proof) >= 30 and "&lt;" not in proof and "<br" not in proof and "|" not in proof
            and bool(entity) and entity.lower() in proof.lower())


def load_qampari_questions(split: str = "train") -> list[Question]:
    out = []
    with zipfile.ZipFile(fetch(URL, "qampari.zip")) as z, z.open(f"qampari_data/{split}_data.jsonl") as f:
        for line in f:
            r = json.loads(line)
            try:
                ents = ast.literal_eval(r["entities"]) if isinstance(r["entities"], str) else r["entities"]
                entity = ents[0]["entity_text"] if ents else ""
            except (ValueError, SyntaxError, KeyError, IndexError):
                entity = ""
            answers, seen = [], set()
            for a in r["answer_list"]:
                name = " ".join(a["answer_text"].split())
                proofs = [p["proof_text"] for p in a.get("proof") or [] if _clean(p.get("proof_text") or "", entity)]
                if name and proofs and name.lower() not in seen:  # keep answers whose proof names the subject
                    seen.add(name.lower())
                    answers.append((name, _clip(proofs[0])))
            text = r["question_text"].strip()
            template = text.replace(entity, "{E}") if entity and entity in text else ""
            if sum(bool(NUMERIC.fullmatch(a)) for a, _ in answers) * 2 > len(answers):
                continue  # dates and numbers: the proof names the work, not the value (a second hop)
            if answers and template:
                out.append(Question(r["qid"], text, entity, template, answers))
    counts: dict[str, int] = {}
    for q in out:
        counts[q.template] = counts.get(q.template, 0) + 1
    return [q for q in out if counts[q.template] >= 3]  # distractors need sibling questions


class QampariPool:
    """Rows drawn on demand: n_gold of the question's answers plus n_options - n_gold distractors."""
    name = "qampari"

    def __init__(self, questions: list[Question]):
        self.questions = questions
        self.by_template: dict[str, list[int]] = {}
        for i, q in enumerate(questions):
            self.by_template.setdefault(q.template, []).append(i)

    def __len__(self) -> int:
        return len(self.questions)

    def limits(self, i: int) -> tuple[int, int]:
        """(gold available, negatives available) for base item i."""
        siblings = len(self.by_template[self.questions[i].template]) - 1
        return len(self.questions[i].answers), 0 if siblings < 1 else 255

    def draw(self, i: int, rng: random.Random, n_gold: int, n_options: int) -> Item | None:
        q = self.questions[i]
        own = {a.lower() for a, _ in q.answers}
        siblings = [j for j in self.by_template[q.template] if j != i]
        rng.shuffle(siblings)
        negatives, seen = [], set(own)
        for j in siblings:
            for name, proof in self.questions[j].answers:
                if name.lower() in seen or (q.entity and q.entity.lower() in proof.lower()):
                    continue
                seen.add(name.lower())
                negatives.append((name, proof))
                break  # one per sibling question: spread over subjects
            if len(negatives) >= n_options - n_gold:
                break
        gold = rng.sample(q.answers, min(n_gold, len(q.answers)))
        chosen = [(a, p, True) for a, p in gold] + [(a, p, False) for a, p in negatives[: n_options - len(gold)]]
        if len(chosen) < 2:
            return None
        rng.shuffle(chosen)
        facts = [f"- {a}: {p}" for a, p, _ in chosen]
        rng.shuffle(facts)
        state = "Facts:\n" + "\n".join(facts)
        return Item(f"qampari:{q.qid}", "qampari", state, q.text, [a for a, _, _ in chosen],
                    [n for n, (_, _, ok) in enumerate(chosen) if ok])
