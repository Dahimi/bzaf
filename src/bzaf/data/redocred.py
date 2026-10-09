"""Re-DocRED (Tan et al. 2022), MIT: DocRED's Wikipedia documents re-annotated to fix missing relation labels; 96
Wikidata relation types between the entities of each document.

Two kinds of item per document: which relations hold from one entity to another (most entity pairs have none, so
some unrelated pairs are added as empty answers), and which relations an entity has as the subject. The
document-level "which relation types appear" question is left out (close to the held-out business-event family,
D21). Relation names are Wikidata property labels (CC0).
"""
from __future__ import annotations

import json
import random

from ..schema import Item
from ._util import fetch

URL = "https://raw.githubusercontent.com/tonytan48/Re-DocRED/main/data/{split}_revised.json"
RELATIONS = {
    "P6": "head of government", "P17": "country", "P19": "place of birth", "P20": "place of death", "P22": "father",
    "P25": "mother", "P26": "spouse", "P27": "country of citizenship", "P30": "continent", "P31": "instance of",
    "P35": "head of state", "P36": "capital", "P37": "official language", "P39": "position held", "P40": "child",
    "P50": "author", "P54": "member of sports team", "P57": "director", "P58": "screenwriter", "P69": "educated at",
    "P86": "composer", "P102": "member of political party", "P108": "employer", "P112": "founded by", "P118": "league",
    "P123": "publisher", "P127": "owned by", "P131": "located in the administrative territorial entity",
    "P136": "genre", "P137": "operator", "P140": "religion", "P150": "contains administrative territorial entity",
    "P155": "follows", "P156": "followed by", "P159": "headquarters location", "P161": "cast member",
    "P162": "producer", "P166": "award received", "P170": "creator", "P171": "parent taxon", "P172": "ethnic group",
    "P175": "performer", "P176": "manufacturer", "P178": "developer", "P179": "series", "P190": "sister city",
    "P194": "legislative body", "P205": "basin country", "P206": "located in or next to body of water",
    "P241": "military branch", "P264": "record label", "P272": "production company", "P276": "location",
    "P279": "subclass of", "P355": "subsidiary", "P361": "part of", "P364": "original language of work",
    "P400": "platform", "P403": "mouth of the watercourse", "P449": "original network", "P463": "member of",
    "P488": "chairperson", "P495": "country of origin", "P527": "has part", "P551": "residence",
    "P569": "date of birth", "P570": "date of death", "P571": "inception",
    "P576": "dissolved, abolished or demolished", "P577": "publication date", "P580": "start time",
    "P582": "end time", "P585": "point in time", "P607": "conflict", "P674": "characters", "P676": "lyrics by",
    "P706": "located on terrain feature", "P710": "participant", "P737": "influenced by",
    "P740": "location of formation", "P749": "parent organization", "P800": "notable work", "P807": "separated from",
    "P840": "narrative location", "P937": "work location", "P1001": "applies to jurisdiction",
    "P1056": "product or material produced", "P1198": "unemployment rate", "P1336": "territory claimed by",
    "P1344": "participant of", "P1365": "replaces", "P1366": "replaced by", "P1376": "capital of",
    "P1412": "languages spoken, written or signed", "P1441": "present in work", "P3373": "sibling",
}
PAIR = "Which of these relations does the text state from «{h}» to «{t}» (read as: «{h}» — relation — «{t}»)?"
SUBJECT = "Which of these relations does the text state with «{e}» as the subject (read as: «{e}» — relation — another entity)?"


def _text(doc: dict) -> str:
    return " ".join(" ".join(s) for s in doc["sents"])


def load_redocred(split: str = "train", seed: int = 0) -> list[Item]:
    docs = json.loads(fetch(URL.format(split=split), f"redocred-{split}_revised.json").read_text(encoding="utf-8"))
    rng = random.Random(seed)
    pids = list(RELATIONS)
    names = [RELATIONS[p] for p in pids]
    items = []
    for d, doc in enumerate(docs):
        ents = [v[0]["name"] for v in doc["vertexSet"]]
        unique = {i for i, e in enumerate(ents) if ents.count(e) == 1}
        pairs: dict[tuple[int, int], set[int]] = {}
        subj: dict[int, set[int]] = {}
        for lab in doc["labels"]:
            if lab["r"] in RELATIONS:
                r = pids.index(lab["r"])
                pairs.setdefault((lab["h"], lab["t"]), set()).add(r)
                subj.setdefault(lab["h"], set()).add(r)
        text = f"{doc['title']}\n\n{_text(doc)}"
        related = [p for p in pairs if p[0] in unique and p[1] in unique]
        others = [(h, t) for h in unique for t in unique if h != t and (h, t) not in pairs]
        for h, t in related + rng.sample(others, min(len(others), len(related))):
            items.append(Item(f"redocred:{split}:{d}:{h}-{t}", "redocred", text, PAIR.format(h=ents[h], t=ents[t]), names,
                              sorted(pairs.get((h, t), set()))))
        for e in sorted(unique):
            if e in subj or rng.random() < 0.3:
                items.append(Item(f"redocred:{split}:{d}:{e}", "redocred", text, SUBJECT.format(e=ents[e]), names,
                                  sorted(subj.get(e, set()))))
    return items
