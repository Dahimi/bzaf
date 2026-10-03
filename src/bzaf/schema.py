"""The one item format every dataset is converted to (JSONL, one item per line).

{"id": "sata:12", "dataset": "sata", "state": "...", "question": "...", "options": ["...", ...], "gold": [0, 3],
 "meta": {...}}

`gold` holds option indices; an empty list means none of the options apply.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator


@dataclass
class Item:
    id: str
    dataset: str
    state: Any
    question: str
    options: list[str]
    gold: list[int]
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.options:
            raise ValueError(f"{self.id}: no options")
        if len(set(self.options)) != len(self.options):
            raise ValueError(f"{self.id}: duplicate option texts")
        if any(not 0 <= g < len(self.options) for g in self.gold) or len(set(self.gold)) != len(self.gold):
            raise ValueError(f"{self.id}: bad gold indices {self.gold}")
        self.gold = sorted(self.gold)


def write_items(items: Iterable[Item], path: str | Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(asdict(it), ensure_ascii=False) + "\n")
            n += 1
    return n


def read_items(path: str | Path) -> Iterator[Item]:
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield Item(**json.loads(line))


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
