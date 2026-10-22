"""E04a tables beyond `bzaf bench score`: how well each model's count matches the gold count without labels, and
whether the count follows the bar wording. Test split only (the same split as every other report).

    uv run python experiments/E04a-llm-count/analyze.py qwen3.5-4b=runs/e04a-qwen3.5-4b qwen3.6-27b=runs/e04a-qwen3.6-27b \
        nox-4b=runs/nox > experiments/E04a-llm-count/results/counts.md

A run directory holds bench/<track>.jsonl and bar/bar_<source>.jsonl (a directory with the track files directly, like
the Nox-4B records of E01b, also works; it has no probe).
"""
import json
import sys
from pathlib import Path

import numpy as np

from bzaf.predictors import Independent, ScoresPlusCount
from bzaf.score import is_dev

TRACKS = ("sata", "nlupp", "ecthr", "unfair_tos", "synthetic")
SOURCES = ("wands", "esci")
ASKED, SUMMED = ScoresPlusCount("pick"), Independent("noul_ctx")


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [r for r in map(json.loads, path.open()) if "error" not in r and all(f in r for f in ("noul_ctx", "pick", "count"))]


def ranks(x) -> np.ndarray:
    """Average ranks (ties share their mean rank)."""
    x = np.asarray(x, float)
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    for v in np.unique(x):
        r[x == v] = r[x == v].mean()
    return r


def spearman(a, b) -> float:
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def counts(r: dict) -> tuple[float, int, float, int]:
    """Asked count (expected, most likely) and summed yes/no (expected, number above 0.5)."""
    c = np.asarray(r["count"], float)
    c /= c.sum()
    p = np.asarray(r["noul_ctx"], float)
    return float(np.arange(len(c)) @ c), int(c.argmax()), float(p.sum()), int((p > 0.5).sum())


def written(recs: list[dict], g: np.ndarray) -> str:
    """Written answer: mean count / rank corr / exactly right count (unparsed answers: count unknown, so wrong)."""
    if not any("write_raw" in r for r in recs):
        return "–"
    ok = np.array(["write" in r for r in recs])
    w = np.array([len(r["write"]) if "write" in r else -1 for r in recs])
    if not ok.any():
        return "none parsed"
    corr = spearman(w[ok], g[ok]) if ok.sum() > 2 else float("nan")
    return f"{w[ok].mean():.2f} / {corr:+.2f} / {100 * (w == g).mean():.1f} % ({100 * (1 - ok.mean()):.0f} % unparsed)"


def count_table(runs: dict[str, Path]) -> str:
    out = ["| track | model | test | gold mean | asked: mean / rank corr / exactly right | summed yes/no: mean / rank corr / exactly right "
           "| written: mean / rank corr / exactly right |",
           "|---|---|---|---|---|---|---|"]
    for t in TRACKS:
        for name, d in runs.items():
            recs = [r for r in load(d / f"{t}.jsonl") if not is_dev(r["id"], 0.3)]
            if not recs:
                continue
            g = np.array([len(r["gold"]) for r in recs])
            e, m, s, k = map(np.array, zip(*map(counts, recs)))
            out.append(f"| {t} | {name} | {len(recs)} | {g.mean():.2f} | {e.mean():.2f} / {spearman(e, g):+.2f} / {100 * (m == g).mean():.1f} % "
                       f"| {s.mean():.2f} / {spearman(s, g):+.2f} / {100 * (k == g).mean():.1f} % | {written(recs, g)} |")
    return "\n".join(out)


def bar_table(runs: dict[str, Path]) -> str:
    out = ["| source | model | pairs | gold count strict → loose | asked count strict → loose (moved ≥ 1 the right way) "
           "| summed yes/no strict → loose (moved ≥ 1 the right way) | written strict → loose (moved ≥ 1 the right way) "
           "| exact set, strict / loose: asked count | same: summed yes/no | same: written |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for src in SOURCES:
        for name, d in runs.items():
            recs = {r["id"]: r for r in load(d.parent / "bar" / f"bar_{src}.jsonl")} if d.name == "bench" else {}
            pairs = [(recs[i], recs[i[: -len("strict")] + "loose"]) for i in recs
                     if i.endswith(":strict") and i[: -len("strict")] + "loose" in recs]
            if not pairs:
                continue
            row = {}
            for side in (0, 1):
                rs = [p[side] for p in pairs]
                row[side] = dict(gold=np.mean([len(r["gold"]) for r in rs]),
                                 asked=np.array([counts(r)[0] for r in rs]), summed=np.array([counts(r)[2] for r in rs]),
                                 ex_asked=100 * np.mean([ASKED.predict(r).subset == set(r["gold"]) for r in rs]),
                                 ex_summed=100 * np.mean([SUMMED.predict(r).subset == set(r["gold"]) for r in rs]),
                                 written=np.array([len(r["write"]) if "write" in r else np.nan for r in rs]),
                                 ex_written=100 * np.mean([set(r.get("write", [-1])) == set(r["gold"]) for r in rs]))
            s, lo = row[0], row[1]
            moved = {k: 100 * np.mean(lo[k] - s[k] >= 1) for k in ("asked", "summed", "written")}   # unparsed: not moved
            wr = (f"{np.nanmean(s['written']):.2f} → {np.nanmean(lo['written']):.2f} ({moved['written']:.0f} %)"
                  if not np.isnan(s["written"]).all() else "–")
            out.append(f"| {src} | {name} | {len(pairs)} | {s['gold']:.2f} → {lo['gold']:.2f} "
                       f"| {s['asked'].mean():.2f} → {lo['asked'].mean():.2f} ({moved['asked']:.0f} %) "
                       f"| {s['summed'].mean():.2f} → {lo['summed'].mean():.2f} ({moved['summed']:.0f} %) | {wr} "
                       f"| {s['ex_asked']:.1f} / {lo['ex_asked']:.1f} | {s['ex_summed']:.1f} / {lo['ex_summed']:.1f} "
                       f"| {s['ex_written']:.1f} / {lo['ex_written']:.1f} |")
    return "\n".join(out)


def main(args: list[str]) -> None:
    runs = {}
    for a in args:
        name, _, path = a.partition("=")
        d = Path(path)
        runs[name] = d / "bench" if (d / "bench").is_dir() else d
    print("## Counts without labels (test split)\n")
    print("Asked: the model's answer to \"how many of these options apply?\" (expected value; exactly right = its most "
          "likely count is the gold count). Summed yes/no: the sum of its per-option yes probabilities (exactly right = "
          "the number of options above 0.5 is the gold count). Written: the number of letters it wrote (a few generated "
          "tokens, not one pass; unparsed answers count as wrong). Rank corr: Spearman with the gold count.\n")
    print(count_table(runs))
    print("\n## Bar wording: the same options asked strictly and loosely (all pairs: the loose answer has more options)\n")
    print(bar_table(runs))


if __name__ == "__main__":
    main(sys.argv[1:])
