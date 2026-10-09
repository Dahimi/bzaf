"""MAMS aspect-category data (Jiang et al. 2019), Apache-2.0: restaurant-review sentences, each with 2+ aspect
categories and their polarity.

Three items per sentence: which aspects the review mentions, praises, and criticises (8 categories with short
descriptions); praise and criticism questions give natural empty answers.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from ..schema import Item
from ._util import fetch

URL = "https://raw.githubusercontent.com/siat-nlp/MAMS-for-ABSA/master/data/MAMS-ACSA/raw/{split}.xml"
CATEGORIES = {
    "food": "the food or drinks", "service": "the service in general", "staff": "the staff or a person working there",
    "price": "prices or value for money", "ambience": "atmosphere, noise, decor", "menu": "the menu or choice of dishes",
    "place": "the location or the place itself", "miscellaneous": "anything else about the restaurant",
}
QUESTIONS = {
    "mention": ("Which aspects of the restaurant does this review talk about?", None),
    "praise": ("Which aspects of the restaurant does this review praise?", "positive"),
    "criticise": ("Which aspects of the restaurant does this review criticise?", "negative"),
}


def load_mams(split: str = "train") -> list[Item]:
    root = ET.parse(fetch(URL.format(split=split), f"mams-acsa-{split}.xml")).getroot()
    names = list(CATEGORIES)
    items = []
    for n, s in enumerate(root.iter("sentence")):
        text = s.findtext("text").strip()
        cats = [(c.get("category"), c.get("polarity")) for c in s.iter("aspectCategory")]
        for key, (question, polarity) in QUESTIONS.items():
            gold = sorted({names.index(c) for c, p in cats if c in CATEGORIES and (polarity is None or p == polarity)})
            items.append(Item(f"mams:{split}:{n}:{key}", "mams", f"Review: {text}", question, names, gold,
                              {"descriptions": [CATEGORIES[c] for c in names]}))
    return items
