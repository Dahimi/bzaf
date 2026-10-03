"""Command line: `bzaf prepare | readout | score`. See README.md for the end-to-end E01 recipe."""
from __future__ import annotations

import argparse
import sys

from .data import LOADERS
from .schema import read_items, write_items


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="bzaf")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="convert a dataset to the item format (data/items/<name>.jsonl)")
    p.add_argument("dataset", choices=sorted(LOADERS))
    p.add_argument("--limit", type=int, default=None, help="fixed random subset of this many items")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default=None)

    r = sub.add_parser("readout", help="ask a decision server about every item and save raw probabilities")
    r.add_argument("--items", required=True)
    r.add_argument("--base-url", required=True, help="e.g. http://localhost:8000 (a TypeSafe-compatible server)")
    r.add_argument("--model", required=True, help="name recorded in the output, and sent as the request's model")
    r.add_argument("--out", required=True)
    r.add_argument("--variants", default="noul,noul_ctx,pick,count")
    r.add_argument("--max-questions", type=int, default=64, help="questions per request (chunked above this)")
    r.add_argument("--limit", type=int, default=None)

    s = sub.add_parser("score", help="score readout files and print the E01 tables")
    s.add_argument("readouts", nargs="+")
    s.add_argument("--dev-frac", type=float, default=0.3)
    s.add_argument("--out", default=None, help="write <out>.md and <out>.json")

    a = ap.parse_args(argv)
    if a.cmd == "prepare":
        kw = {"limit": a.limit, "seed": a.seed}
        items = LOADERS[a.dataset](**kw)
        out = a.out or f"data/items/{a.dataset}.jsonl"
        n = write_items(items, out)
        print(f"{n} items -> {out}")
    elif a.cmd == "readout":
        from .client import DecisionClient
        from .readout import run_readout

        items = list(read_items(a.items))[: a.limit]
        run_readout(DecisionClient(a.base_url, a.model), items, a.out, a.variants.split(","), a.max_questions)
    elif a.cmd == "score":
        from .score import score_files

        print(score_files(a.readouts, a.dev_frac, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
