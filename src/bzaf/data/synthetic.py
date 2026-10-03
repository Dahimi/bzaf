"""Programmatic multi-answer items with exact gold sets: a JSON order plus statements about it.

Uses: a clean positive control (gold is computed, never noisy), every count from 0 to K including "none", and
known dependence between options (two thresholds on the same field imply each other: "total above $200" implies
"total above $50"). Later, the same generator scales into training data with no licence or teacher questions.
"""
from __future__ import annotations

import random

from ..schema import Item

COUNTRIES = ["France", "Germany", "Morocco", "Spain", "the United States", "Japan"]
PRODUCTS = ["headphones", "a laptop stand", "a phone case", "a coffee grinder", "running shoes", "a desk lamp"]
QUESTION = "Which of these statements about the order are true?"


def _order(rng: random.Random) -> dict:
    items = rng.sample(PRODUCTS, rng.randint(1, 4))
    return {
        "customer_country": rng.choice(COUNTRIES),
        "account_age_days": rng.choice([2, 10, 45, 200, 900]),
        "items": [{"product": p, "quantity": rng.randint(1, 3)} for p in items],
        "total_usd": rng.choice([12, 38, 75, 140, 260, 610]),
        "express_shipping": rng.random() < 0.4,
        "paid": rng.random() < 0.7,
        "coupon_code": rng.choice([None, None, "WELCOME10", "SPRING25"]),
    }


def _statements(o: dict) -> list[tuple[str, bool, str]]:
    """(text, truth, group). Statements in the same group are logically linked."""
    n_units = sum(i["quantity"] for i in o["items"])
    products = {i["product"] for i in o["items"]}
    out = [(f"The order total is above ${t}.", o["total_usd"] > t, "total") for t in (20, 50, 100, 200, 500)]
    out += [(f"The customer is based in {c}.", o["customer_country"] == c, "country") for c in COUNTRIES]
    out += [(f"The order includes {p}.", p in products, f"product:{p}") for p in PRODUCTS]
    out += [(f"The order contains more than {n} units in total.", n_units > n, "units") for n in (1, 3, 6)]
    out += [(f"The customer account is less than {d} days old.", o["account_age_days"] < d, "age") for d in (7, 30, 365)]
    out += [
        ("Express shipping was selected.", o["express_shipping"], "express"),
        ("The order has been paid.", o["paid"], "paid"),
        ("A coupon code was applied.", o["coupon_code"] is not None, "coupon"),
    ]
    return out


def load_synthetic(n: int = 500, seed: int = 0, min_options: int = 4, max_options: int = 10, limit: int | None = None) -> list[Item]:
    rng = random.Random(seed)
    items = []
    for i in range(n if limit is None else min(n, limit)):
        o = _order(rng)
        pool = _statements(o)
        k = rng.randint(min_options, max_options)
        chosen = rng.sample(pool, k)
        items.append(Item(
            id=f"synthetic:{seed}:{i}",
            dataset="synthetic",
            state=o,
            question=QUESTION,
            options=[t for t, _, _ in chosen],
            gold=[j for j, (_, ok, _) in enumerate(chosen) if ok],
            meta={"groups": [g for _, _, g in chosen]},
        ))
    return items
