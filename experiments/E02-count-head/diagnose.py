"""E02 diagnosis: on each multi-answer track's test split, is the trained model's failure in the count or in the
selection, and does its count carry signal? Reads the in-process evaluation records (results/eval-records.tgz).

    tar xzf experiments/E02-count-head/results/eval-records.tgz -C runs/e02 && find runs/e02 -name '._*' -delete
    uv run python experiments/E02-count-head/diagnose.py runs/e02/eval > experiments/E02-count-head/results/diagnosis.md
"""
import json
import sys
from pathlib import Path

import numpy as np

from bzaf.score import is_dev
from bzaf.setdist import SetDistribution


def load(p: Path) -> dict:
    return {r["id"]: r for r in map(json.loads, p.open()) if "error" not in r}


def auc(score, label) -> float:
    score, label = np.asarray(score, float), np.asarray(label, bool)
    pos, neg = score[label], score[~label]
    if not len(pos) or not len(neg):
        return float("nan")
    return float(np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos]))


def spearman(a, b) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main(root: Path, tracks=("ecthr", "nlupp", "sata", "unfair_tos", "goemotions", "synthetic")) -> None:
    print("| track | test | gold size (share empty) | ours E[size] / mode size / mean P(0) | ours ranking + true count "
          "| base Choice + true count | ours ranking + dev count prior: exact / log-loss | count ↔ gold rank corr: ours / "
          "base 'how many' / base Σ yes-no | 'none' AUC: ours P(0) / base 1 − max yes-no |")
    print("|---|---|---|---|---|---|---|---|---|")
    for t in tracks:
        ours, base = load(root / "ours" / f"{t}.jsonl"), load(root / "base" / f"{t}.jsonl")
        ids = [i for i in ours if i in base]
        dev, test = [i for i in ids if is_dev(i, 0.3)], [i for i in ids if not is_dev(i, 0.3)]
        prior = np.full(max(ours[i]["k"] for i in ids) + 1, 0.5)   # dev count histogram, add-0.5 smoothing
        for i in dev:
            prior[len(ours[i]["gold"])] += 1
        m = {k: [] for k in ("gold", "E", "mode", "p0", "ztrue", "btrue", "zdev", "zdev_nll", "bhow", "bsum", "bmax")}
        for i in test:
            r, b, k = ours[i], base[i], ours[i]["k"]
            gold = set(r["gold"])
            z = np.asarray(r["multi_z"])
            c = np.zeros(k + 1)
            n = min(k + 1, len(r["multi_count"]))
            c[:n] = r["multi_count"][:n]
            c /= c.sum()
            d = SetDistribution.from_logits_and_count(z, c)
            dd = SetDistribution.from_logits_and_count(z, prior[: k + 1] / prior[: k + 1].sum())
            m["gold"].append(len(gold))
            m["E"].append(float(np.arange(k + 1) @ c))
            m["mode"].append(len(d.mode()))
            m["p0"].append(c[0])
            m["ztrue"].append(set(np.argsort(-z, kind="stable")[: len(gold)].tolist()) == gold)
            m["btrue"].append(set(np.argsort(-np.asarray(b["pick"]), kind="stable")[: len(gold)].tolist()) == gold)
            m["zdev"].append(set(dd.mode()) == gold)
            m["zdev_nll"].append(-dd.log_prob(gold))
            m["bhow"].append(float(np.arange(len(b["count"])) @ np.asarray(b["count"])))
            m["bsum"].append(sum(b["noul_ctx"]))
            m["bmax"].append(-max(b["noul_ctx"]))
        a = {k: float(np.mean(v)) for k, v in m.items()}
        none = [g == 0 for g in m["gold"]]
        print(f"| {t} | {len(test)} | {a['gold']:.2f} ({np.mean(none):.2f}) | {a['E']:.2f} / {a['mode']:.2f} / {a['p0']:.2f} "
              f"| {100 * a['ztrue']:.1f} | {100 * a['btrue']:.1f} | {100 * a['zdev']:.1f} / {a['zdev_nll']:.2f} "
              f"| {spearman(m['E'], m['gold']):+.2f} / {spearman(m['bhow'], m['gold']):+.2f} / {spearman(m['bsum'], m['gold']):+.2f} "
              f"| {auc(m['p0'], none):.2f} / {auc(m['bmax'], none):.2f} |")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
