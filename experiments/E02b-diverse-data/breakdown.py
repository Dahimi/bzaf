"""E02b read-outs that the pre-registration reports (no decision attached): exact-set % on the held-out tracks per
SATA source subset and per gold-count bucket, for each trained run's `ours@mode` and the baseline B (per track the
better of `noul_ctx+platt` and `pick+dev_prior` on test, as in G2).

    uv run python experiments/E02b-diverse-data/breakdown.py runs/e02/eval/base e02=runs/e02/eval/ours \
        e02b=runs/e02b/eval/ours > experiments/E02b-diverse-data/results/breakdown.md
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from bzaf import bench
from bzaf.schema import read_jsonl

HELD_OUT = ("sata", "nlupp", "ecthr", "unfair_tos")
B = ("noul_ctx+platt", "pick+dev_prior")
SUBSETS = {"d1": "story reading comprehension", "d2": "toxicity", "d3": "Reuters topics", "d4": "MeSH",
           "d5": "EUR-Lex", "d6": "business events"}
BUCKETS = ((0, 0), (1, 1), (2, 4), (5, 9), (10, 99))


def exact_by_id(main: dict, track: str, predictor: str) -> dict[str, bool]:
    r = main[track]
    preds = r["predictors"][predictor]["per_item_pred"]
    return {i: p is not None and set(p) == gold[i] for i, p in zip(r["test_ids"], preds)}


def main(base_dir: str, runs: list[str], bench_dir: str = "data/bench-v0") -> None:
    global gold
    gold = {r["id"]: set(r["gold"]) for p in Path(base_dir).glob("*.jsonl") for r in read_jsonl(p)}
    subset = {json.loads(line)["id"]: json.loads(line)["meta"].get("source_subset")
              for line in (Path(bench_dir) / "sata.jsonl").open()}
    base = bench.score(base_dir)["main"]
    columns = {}
    for track in HELD_OUT:
        name = max(B, key=lambda n: sum(exact_by_id(base, track, n).values()) if n in base[track]["predictors"] else -1)
        columns.setdefault("B", {}).update(exact_by_id(base, track, name))
    for spec in runs:
        label, path = spec.split("=", 1)
        res = bench.score(path)["main"]
        for track in HELD_OUT:
            columns.setdefault(label, {}).update(exact_by_id(res, track, "ours@mode"))
    labels = list(columns)

    def row(name, ids):
        ids = [i for i in ids if all(i in columns[c] for c in labels)]
        cells = [f"{100 * sum(columns[c][i] for i in ids) / max(1, len(ids)):.1f}" for c in labels]
        return f"| {name} | {len(ids)} | " + " | ".join(cells) + " |"

    print("Exact-set % on test items (B = per track the better of " + " / ".join(B) + ").\n")
    print("| SATA subset | items | " + " | ".join(labels) + " |\n|---|---|" + "---|" * len(labels))
    by_sub = defaultdict(list)
    for i in columns["B"]:
        if i.startswith("sata:"):
            by_sub[subset.get(i)].append(i)
    for s in sorted(by_sub):
        print(row(f"{s} {SUBSETS.get(s, '')}", by_sub[s]))
    print("\n| track, gold count | items | " + " | ".join(labels) + " |\n|---|---|" + "---|" * len(labels))
    for track in HELD_OUT:
        ids = [i for i in columns["B"] if i.split(":")[0] == track]
        for lo, hi in BUCKETS:
            sel = [i for i in ids if lo <= len(gold[i]) <= hi]
            if sel:
                print(row(f"{track}, {lo}" + (f"–{hi}" if hi != lo else ""), sel))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
