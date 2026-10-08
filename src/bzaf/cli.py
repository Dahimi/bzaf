"""Command line: `bzaf prepare | readout | score | bench`. See README.md and docs/benchmark.md."""
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
    r.add_argument("--variants", default="noul,noul_ctx,pick,count", help="comma list of noul,noul_ctx,pick,count,set")
    r.add_argument("--max-questions", type=int, default=64, help="questions per request (chunked above this)")
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--concurrency", type=int, default=1, help="items in flight at once (use 8-32 against a GPU server, 1 on a Mac)")
    r.add_argument("--timeout", type=float, default=300.0, help="seconds per request")

    s = sub.add_parser("score", help="score readout files and print the E01 tables")
    s.add_argument("readouts", nargs="+")
    s.add_argument("--dev-frac", type=float, default=0.3)
    s.add_argument("--out", default=None, help="write <out>.md and <out>.json")

    b = sub.add_parser("bench", help="benchmark v0: prepare the tracks, read a model out on all of them, score")
    bsub = b.add_subparsers(dest="bench_cmd", required=True)
    bp = bsub.add_parser("prepare", help="write every track to data/bench-v0 with a manifest (deterministic)")
    bp.add_argument("--out", default="data/bench-v0")
    bp.add_argument("--tracks", default=None, help="comma list (default: all)")
    br = bsub.add_parser("readout", help="read one model out on every track (resumable)")
    br.add_argument("--base-url", required=True)
    br.add_argument("--model", required=True)
    br.add_argument("--bench", default="data/bench-v0")
    br.add_argument("--out", default=None, help="default runs/bench-v0/<model>")
    br.add_argument("--with-set", action="store_true", help="also ask the native `set` question type (Vela 2.0)")
    br.add_argument("--tracks", default=None, help="comma list of tracks (and/or `order`); default all")
    br.add_argument("--max-questions", type=int, default=64)
    br.add_argument("--concurrency", type=int, default=8)
    br.add_argument("--limit", type=int, default=None, help="first N items of each track (pilot)")
    br.add_argument("--timeout", type=float, default=300.0)
    bs = bsub.add_parser("score", help="score one model's benchmark run directory")
    bs.add_argument("run_dir")
    bs.add_argument("--dev-frac", type=float, default=0.3)
    bs.add_argument("--out", default=None, help="write <out>.md and <out>.json")
    bc = bsub.add_parser("compare", help="paired comparison of two models' runs (A - B), per track and macro-averaged")
    bc.add_argument("run_a")
    bc.add_argument("run_b")
    bc.add_argument("--predictor", default="pick+true_count")
    bc.add_argument("--metric", default="per_item_exact", choices=["per_item_exact", "per_item_f1", "per_item_nll"])
    bc.add_argument("--predictor-b", default=None, help="B's predictor(s), comma list: per track the best one (default: as A)")
    bc.add_argument("--only", default=None, help="comma list of tracks to compare (default: all)")

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
        run_readout(DecisionClient(a.base_url, a.model, timeout=a.timeout), items, a.out, a.variants.split(","), a.max_questions, a.concurrency)
    elif a.cmd == "bench":
        from . import bench

        tracks = a.tracks.split(",") if getattr(a, "tracks", None) else None
        if a.bench_cmd == "prepare":
            bench.prepare(a.out, tracks)
        elif a.bench_cmd == "readout":
            from .client import DecisionClient

            bench.readout(DecisionClient(a.base_url, a.model, timeout=a.timeout), a.bench, a.out or f"runs/bench-v0/{a.model}",
                          a.with_set, tracks, a.max_questions, a.concurrency, a.limit)
        elif a.bench_cmd == "compare":
            res = bench.compare(a.run_a, a.run_b, a.predictor, a.metric, predictor_b=a.predictor_b,
                                tracks=a.only.split(",") if a.only else None)
            print(bench.format_compare(res, a.run_a, a.run_b))
        else:
            print(bench.score_dir(a.run_dir, a.dev_frac, a.out))
    elif a.cmd == "score":
        from .score import score_files

        print(score_files(a.readouts, a.dev_frac, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
