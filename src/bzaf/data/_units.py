"""Unit-selection items: a long text cut into numbered units (paragraphs or sentences), each offered as an option."""
from __future__ import annotations

UNIT_CHARS = 2000  # one unit longer than this is cut (a few huge tables or lists)


def window(units: list[str], gold: set[int], budget: int, tag: str = "P") -> tuple[str, list[str], list[int]]:
    """Number the units "[P1] ...", keeping the whole text if it fits in `budget` characters, else every gold unit plus
    its nearest neighbours (in document order) up to the budget. Returns (text, option keys, gold positions)."""
    units = [u if len(u) <= UNIT_CHARS else u[:UNIT_CHARS].rsplit(" ", 1)[0] + " …" for u in units]
    cost = [len(u) + 8 for u in units]
    if sum(cost) <= budget:
        keep = list(range(len(units)))
    else:
        anchors = sorted(gold) or [0]
        order = sorted(range(len(units)), key=lambda i: (min(abs(i - a) for a in anchors), i))
        keep, used = [], 0
        for i in order:
            if used + cost[i] > budget and keep:
                if i in gold:
                    return "", [], []  # the gold units alone do not fit
                continue
            keep.append(i)
            used += cost[i]
        keep.sort()
    keys = [f"{tag}{n + 1}" for n in range(len(keep))]
    text = "\n".join(f"[{k}] {units[i]}" for k, i in zip(keys, keep))
    return text, keys, [n for n, i in enumerate(keep) if i in gold]
