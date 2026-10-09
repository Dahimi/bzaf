"""The E02b training mixture: many task families, and an answer count that no longer follows from the family.

E02 trained on four kinds of multi-answer data whose answer counts were mostly 1-3 (8.7 % empty); the count head
learned that prior and did not transfer (experiments/E02-count-head). Here every source is a pool of base items with
all their candidate options (gold plus judged or in-document negatives), and each training row offers a subset:

  answer count   drawn per row from COUNT_BUCKETS (25 % empty, a third with 5+), capped by what the item has
  option count   log-uniform within the source's range, at least the answer count, at most what the item has
  length         rows estimated above the token budget lose negatives first, or are skipped

so the count of a row is set by which options its own evidence supports, not by its source. Held-out families are
excluded by source choice (D21); rows whose text repeats a benchmark v0 state, or shares a 13-word sequence with one,
are dropped.
"""
from __future__ import annotations

import bisect
import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..schema import Item, read_items
from .data import TrainRow, merged, multi_question, native_question

COUNT_BUCKETS = ((0, 0, 0.25), (1, 1, 0.17), (2, 4, 0.25), (5, 9, 0.15), (10, 19, 0.11), (20, 32, 0.07))
MAX_GOLD = 32          # the count head covers 0..32
MAX_VARIANTS = 3       # rows drawn from one base item, at most
TOKEN_BUDGET = 7000    # estimated tokens per row (context + question + options)
NGRAM = 13


@dataclass
class Source:
    rows: int
    options: tuple[int, int]   # option-count range per row
    load: Callable[[], object]  # a list of Items, or a pool with limits() / draw()
    external: bool = True       # text from outside: checked for 13-word overlap with the benchmark


def _sources(seed: int, token_budget: int = TOKEN_BUDGET) -> dict[str, Source]:
    from ..data import load_goemotions, load_synthetic, load_wide
    from ..data.dbpedia import load_dbpedia
    from ..data.dbpedia_entity import load_dbpedia_entity
    from ..data.esci import load_esci
    from ..data.mams import load_mams
    from ..data.qampari import QampariPool, load_qampari_questions
    from ..data.qasper import load_qasper
    from ..data.redocred import load_redocred
    from ..data.squad2 import load_squad2
    from ..data.wands import load_wands
    from ..data.wice import load_wice

    rng = random.Random(seed)
    doc_chars = int((token_budget - 1500) * 3.5)  # long documents leave ~1.5k tokens for the question and options
    return {
        # new families (docs/data.md licence register)
        "qampari": Source(7000, (4, 80), lambda: QampariPool(load_qampari_questions("train"))),
        "qasper": Source(2500, (8, 120), lambda: load_qasper(budget=doc_chars)),
        "wice": Source(1500, (8, 160), lambda: load_wice(budget=doc_chars)),
        "squad2": Source(5000, (3, 30), load_squad2),
        "esci": Source(6000, (4, 80), load_esci),
        "wands": Source(2500, (6, 200), load_wands),
        "dbpedia_entity": Source(1500, (6, 160), load_dbpedia_entity),
        "redocred": Source(6000, (4, 96), load_redocred),
        "mams": Source(3000, (2, 8), load_mams),
        # E02's sources, now sampled the same way
        "goemotions": Source(3000, (3, 28), lambda: load_goemotions("train")),
        "goemotions_merged": Source(1000, (3, 28), lambda: merged(load_goemotions("train"), 3000, rng, "goemotions_merged",
                                                                  "Which emotions do the authors of these comments express?",
                                                                  "Comment", (2, 3))),
        "dbpedia_merged": Source(2000, (3, 14), lambda: merged(load_dbpedia("train", limit=40000, seed=seed), 6000, rng,
                                                               "dbpedia_merged", "Which categories do these entries belong to?",
                                                               "Entry", (1, 4))),
        "synthetic": Source(3000, (3, 40), lambda: load_synthetic(n=6000, seed=1000 + seed), external=False),
        "wide": Source(1000, (6, 200), lambda: load_wide(n_per_size=500, seed=1000 + seed), external=False),
    }


DISTILL = {"boolq": 4000, "hellaswag": 4000, "sst5": 3500, "dbpedia": 3500}


# --- sampling ---------------------------------------------------------------------------------------------------------

def draw_count(rng: random.Random, available: int) -> int:
    """An answer count from COUNT_BUCKETS, restricted to 0..min(available, MAX_GOLD) (each bucket weighted by the share
    of its range that is still possible)."""
    cap = min(available, MAX_GOLD)
    buckets = [(lo, min(hi, cap), w * (min(hi, cap) - lo + 1) / (hi - lo + 1)) for lo, hi, w in COUNT_BUCKETS if lo <= cap]
    lo, hi, _ = rng.choices(buckets, weights=[w for *_, w in buckets])[0]
    return rng.randint(lo, hi)


def draw_options(rng: random.Random, n_gold: int, n_neg: int, lo: int, hi: int) -> int | None:
    """An option count, log-uniform in [max(lo, n_gold, 2), min(hi, n_gold + n_neg)]; None if impossible."""
    kmin, kmax = max(lo, n_gold, 2), min(hi, n_gold + n_neg)
    if kmax < kmin:
        return None
    return min(kmax, int(math.exp(rng.uniform(math.log(kmin), math.log(kmax + 1)))))


class ItemPool:
    """Base items with every candidate option; a row offers the drawn number of gold and negative options."""

    def __init__(self, items: list[Item]):
        self.items = items

    def __len__(self) -> int:
        return len(self.items)

    def limits(self, i: int) -> tuple[int, int]:
        it = self.items[i]
        return len(it.gold), len(it.options) - len(it.gold)

    def draw(self, i: int, rng: random.Random, n_gold: int, n_options: int) -> Item | None:
        it = self.items[i]
        gold = set(it.gold)
        neg = [j for j in range(len(it.options)) if j not in gold]
        idx = rng.sample(it.gold, n_gold) + rng.sample(neg, n_options - n_gold)
        if it.meta.get("ordered"):
            idx.sort()  # numbered units stay in document order
        else:
            rng.shuffle(idx)
        meta = {}
        if it.meta.get("descriptions"):
            meta["descriptions"] = [it.meta["descriptions"][j] for j in idx]
        return Item(it.id, it.dataset, it.state, it.question, [it.options[j] for j in idx],
                    [n for n, j in enumerate(idx) if j in gold], meta)


def est_tokens(it: Item) -> int:
    """A conservative token estimate (3.5 characters per token, ~22 tokens of markup per option)."""
    desc = it.meta.get("descriptions") or []
    chars = len(str(it.state)) + len(it.question) + sum(len(o) for o in it.options) + sum(len(d or "") for d in desc)
    return int(chars / 3.5) + 22 * len(it.options) + 40


# --- contamination ----------------------------------------------------------------------------------------------------

_WORD = re.compile(r"\w+")


def _ngrams(text: str, n: int = NGRAM) -> set[tuple[str, ...]]:
    w = _WORD.findall(text.lower())
    return {tuple(w[i: i + n]) for i in range(len(w) - n + 1)}


class Benchmark:
    """Every state of benchmark v0: exact matches and 13-word sequences."""

    def __init__(self, bench_dir: str | Path | None):
        self.states: set[str] = set()
        self.grams: set[tuple[str, ...]] = set()
        if bench_dir and Path(bench_dir).exists():
            for f in sorted(Path(bench_dir).glob("*.jsonl")):
                for it in read_items(f):
                    s = it.state if isinstance(it.state, str) else json.dumps(it.state, sort_keys=True)
                    self.states.add(s)
                    self.grams |= _ngrams(s)

    def exact(self, state) -> bool:
        return (state if isinstance(state, str) else json.dumps(state, sort_keys=True)) in self.states

    def overlaps(self, text: str) -> bool:
        return bool(self.grams) and not self.grams.isdisjoint(_ngrams(text))


# --- the mixture ------------------------------------------------------------------------------------------------------

def default_sizes() -> dict[str, int]:
    return {**{k: v.rows for k, v in _sources(0).items()}, **{f"{k}_distill": v for k, v in DISTILL.items()}}


def bucket(n: int, edges: tuple[int, ...]) -> str:
    for lo, hi in zip(edges, edges[1:]):
        if lo <= n < hi:
            return f"{lo}-{hi - 1}" if hi - lo > 1 else str(lo)
    return f"{edges[-1]}+"


def build_e02b(seed: int = 0, sizes: dict | None = None, bench_dir: str | Path | None = "data/bench-v0",
               sources: dict[str, Source] | None = None, distill_loaders: dict | None = None,
               stats_path: str | Path | None = None, token_budget: int = TOKEN_BUDGET,
               measure: Callable[[Item], int] | None = None, log=print) -> list[TrainRow]:
    """The E02b mixture. `sources` and `distill_loaders` override the defaults (tests use small offline ones); a size of
    0 leaves a source out. Rows longer than `token_budget` lose negatives or are skipped; `measure` counts a row's
    tokens (the trainer passes the model's tokenizer; default: an estimate)."""
    from ..data.dbpedia import load_dbpedia
    from ..data.general import load_boolq, load_hellaswag, load_sst5

    srcs = sources or _sources(seed, token_budget)
    length = measure or est_tokens
    sizes = {**{k: v.rows for k, v in srcs.items()}, **{f"{k}_distill": v for k, v in DISTILL.items()}, **(sizes or {})}
    rng = random.Random(seed)
    bench = Benchmark(bench_dir)
    rows: list[TrainRow] = []
    stats: dict[str, Counter] = {k: Counter() for k in ("answers", "options", "tokens", "share_correct")}
    per_source: dict[str, dict] = {}

    for name, src in srcs.items():
        n_rows = sizes.get(name, 0)
        if not n_rows:
            continue
        loaded = src.load()
        pool = loaded if hasattr(loaded, "draw") else ItemPool(loaded)
        lo, hi = src.options
        # the count is drawn first (capped by the most this source can offer), then an item that has that many
        n_gold_of = [pool.limits(i)[0] for i in range(len(pool))]
        order = sorted(range(len(pool)), key=n_gold_of.__getitem__)
        sorted_gold = [n_gold_of[i] for i in order]
        source_max = sorted_gold[-1]
        used: Counter = Counter()
        clean: dict[int, bool] = {}
        made, tries, dropped = [], 0, Counter()
        while len(made) < n_rows and tries < 20 * n_rows:
            tries += 1
            g = draw_count(rng, source_max)
            i = order[rng.randrange(bisect.bisect_left(sorted_gold, g), len(order))]
            if used[i] >= MAX_VARIANTS:
                continue
            n_gold, n_neg = pool.limits(i)
            k = draw_options(rng, g, n_neg, lo, hi)
            if k is None:
                dropped["no options"] += 1
                continue
            it = pool.draw(i, rng, g, k)
            while it is not None and length(it) > token_budget and len(it.options) > max(lo, len(it.gold), 2):
                k = max(lo, len(it.gold), 2, int(len(it.options) * 0.7))  # too long: fewer negatives
                it = pool.draw(i, rng, len(it.gold), k)
            if it is None or length(it) > token_budget:
                dropped["too long"] += 1
                continue
            fixed = isinstance(pool, ItemPool)  # same context for every row of an item: check it once
            if not fixed or i not in clean:
                clean[i] = not bench.exact(it.state) and not (src.external and bench.overlaps(f"{it.state}\n{it.question}"))
            if not clean[i]:
                dropped["benchmark overlap"] += 1
                used[i] = MAX_VARIANTS
                continue
            used[i] += 1
            made.append(TrainRow(f"{it.id}#{used[i]}", name, "set", it.state, multi_question(it), list(it.gold)))
            t = length(it)
            stats["answers"][bucket(len(it.gold), (0, 1, 2, 5, 10, 20, 33))] += 1
            stats["options"][bucket(len(it.options), (2, 5, 11, 31, 101, 256))] += 1
            stats["tokens"][bucket(t, (0, 512, 2048, 4096, 8192))] += 1
            stats["share_correct"][bucket(int(100 * len(it.gold) / len(it.options)), (0, 6, 21, 51, 101))] += 1
            per_source.setdefault(name, Counter()).update(
                rows=1, tokens=t, empty=int(not it.gold), answers=len(it.gold), options=len(it.options))
        rows += made
        log(f"  {name}: {len(made)} rows from {len(pool)} items" + (f" (dropped: {dict(dropped)})" if dropped else ""))

    distill = {"boolq": lambda: load_boolq(limit=None, split="train"), "hellaswag": lambda: load_hellaswag(limit=None, split="train"),
               "sst5": lambda: load_sst5(limit=None, split="train"), "dbpedia": lambda: load_dbpedia("train", limit=40000, seed=seed),
               **(distill_loaders or {})}
    for name, load in distill.items():
        n_rows = sizes.get(f"{name}_distill", 0)
        if not n_rows:
            continue
        items = load()
        kept = 0
        for it in rng.sample(items, min(n_rows, len(items))):
            if bench.exact(it.state) or bench.overlaps(str(it.state)):
                continue
            rows.append(TrainRow(it.id, f"{name}_distill", "distill", it.state, native_question(it), list(it.gold)))
            kept += 1
        per_source[f"{name}_distill"] = Counter(rows=kept)
        log(f"  {name}_distill: {kept} rows")

    rng.shuffle(rows)
    n_set = sum(c["rows"] for k, c in per_source.items() if not k.endswith("_distill"))
    summary = {
        "set_rows": n_set,
        "distill_rows": sum(c["rows"] for k, c in per_source.items() if k.endswith("_distill")),
        "set_tokens": sum(c["tokens"] for c in per_source.values()),
        **{k: {b: round(v / max(1, n_set), 3) for b, v in sorted(c.items())} for k, c in stats.items()},
        "per_source": {k: {"rows": c["rows"], "empty": round(c["empty"] / max(1, c["rows"]), 3),
                           "mean_answers": round(c["answers"] / max(1, c["rows"]), 2),
                           "mean_options": round(c["options"] / max(1, c["rows"]), 1),
                           "mean_tokens": round(c["tokens"] / max(1, c["rows"]))} for k, c in per_source.items()},
    }
    summary["token_budget"] = token_budget
    log("mixture: " + json.dumps({k: v for k, v in summary.items() if k != "per_source"}))
    if stats_path:
        Path(stats_path).write_text(json.dumps(summary, indent=2))
    return rows
