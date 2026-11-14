"""Exploratory, after E04a (not pre-registered): how much of what a task's labels add is ONE number, the bar on the
per-option yes/no score, and can that number be had without labelled examples? Test split; yes/no per option with
all options listed (noul_ctx). Rows:

  @0.5                     the default bar
  platt (dev labels)       two numbers fitted on the dev split's labels (the B baseline's yes/no half)
  1 number, ...            one bar, chosen for exact-set on all / 5 / 10 / 20 labelled dev items (mean of 30 draws)
  oracle 1 number (test)   the best single bar, chosen on test: the most any task-level calibration can give
  no labels: ...           the bar from the unlabelled scores alone (two clusters; Otsu; largest gap per item)
  stated mean count        no labelled items: the bar that makes the average number of answers over the unlabelled
                           items equal to one stated number (here the dev split's mean; also 30 % too low / high)
  true count               per-item oracle (top-n by yes/no score): beyond any task-level number

    uv run python experiments/E04a-llm-count/one_number.py runs/e04a-qwen3.6-27b/bench
"""
import json
import sys
from pathlib import Path

import numpy as np

from bzaf.predictors import fit_platt
from bzaf.score import is_dev

TRACKS = ("sata", "nlupp", "ecthr", "unfair_tos", "synthetic")


def logit(p) -> np.ndarray:
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    return np.log(p) - np.log1p(-p)


def exact(recs: list[dict], xs: list[np.ndarray], bar) -> float:
    """Exact-set % when each item keeps the options above bar(x) (a constant, or a function of the item's scores)."""
    fn = bar if callable(bar) else (lambda x: bar)
    return 100 * float(np.mean([set(np.flatnonzero(x > fn(x)).tolist()) == set(r["gold"]) for r, x in zip(recs, xs)]))


def two_clusters(v: np.ndarray, iters: int = 200) -> tuple[float, np.ndarray]:
    """1-D mixture of two Gaussians by EM; returns the point between the means where they are equally likely."""
    mu = np.percentile(v, [25, 90])
    sd = np.full(2, v.std() + 1e-3)
    w = np.array([0.8, 0.2])
    for _ in range(iters):
        d = w * np.exp(-0.5 * ((v[:, None] - mu) / sd) ** 2) / sd
        r = d / d.sum(1, keepdims=True)
        n = r.sum(0)
        w, mu = n / n.sum(), (r * v[:, None]).sum(0) / n
        sd = np.sqrt((r * (v[:, None] - mu) ** 2).sum(0) / n) + 1e-3
    o = np.argsort(mu)
    mu, sd, w = mu[o], sd[o], w[o]
    g = np.linspace(mu[0], mu[1], 2001)
    d = w * np.exp(-0.5 * ((g[:, None] - mu) / sd) ** 2) / sd
    return float(g[np.argmin(np.abs(d[:, 0] - d[:, 1]))]), mu


def otsu(v: np.ndarray) -> float:
    best, bar = -1.0, 0.0
    for t in np.quantile(v, np.linspace(0.02, 0.98, 193)):
        a, b = v[v <= t], v[v > t]
        if len(a) and len(b) and len(a) * len(b) * (a.mean() - b.mean()) ** 2 > best:
            best, bar = len(a) * len(b) * (a.mean() - b.mean()) ** 2, float(t)
    return bar


def track_rows(recs: list[dict]) -> dict[str, float]:
    dev = [r for r in recs if is_dev(r["id"], 0.3)]
    test = [r for r in recs if not is_dev(r["id"], 0.3)]
    x, xd = [logit(r["noul_ctx"]) for r in test], [logit(r["noul_ctx"]) for r in dev]
    pooled = np.concatenate([logit(r["noul_ctx"]) for r in recs])   # every item's scores, no labels
    grid = np.quantile(pooled, np.linspace(0.01, 0.995, 400))

    def best_bar(rs, xs) -> float:
        return float(grid[int(np.argmax([exact(rs, xs, g) for g in grid]))])

    yd = np.concatenate([[j in set(r["gold"]) for j in range(r["k"])] for r in dev]).astype(float)
    a, b = fit_platt(np.concatenate(xd), yd)
    out = {"@0.5": exact(test, x, 0.0), "platt (dev labels)": exact(test, x, -b / a),
           "1 number, all dev labels": exact(test, x, best_bar(dev, xd))}
    rng = np.random.default_rng(0)
    for n in (5, 10, 20):
        draws = [rng.choice(len(dev), n, replace=False) for _ in range(30)]
        out[f"1 number, {n} labelled items"] = float(np.mean(
            [exact(test, x, best_bar([dev[i] for i in d], [xd[i] for i in d])) for d in draws]))
    out["oracle 1 number (test)"] = max(exact(test, x, g) for g in grid)
    bar, mu = two_clusters(pooled)
    out["no labels: two clusters"] = exact(test, x, bar)
    out["no labels: Otsu"] = exact(test, x, otsu(pooled))

    def largest_gap(v: np.ndarray) -> float:   # cut each item at its widest gap, between the two cluster means
        s = np.sort(np.concatenate([v, mu]))
        i = int(np.argmax(np.diff(s)))
        return float((s[i] + s[i + 1]) / 2)

    out["no labels: largest gap per item"] = exact(test, x, largest_gap)
    share = np.mean([len(r["gold"]) for r in dev]) / np.mean([r["k"] for r in recs])   # stated answers per option
    for name, f in (("stated mean count", 1.0), ("stated mean count, 30 % too low", 0.7), ("stated mean count, 30 % too high", 1.3)):
        out[name] = exact(test, x, float(np.quantile(pooled, 1 - min(share * f, 1.0))))
    out["true count"] = 100 * float(np.mean(
        [set(np.argsort(-v)[: len(r["gold"])].tolist()) == set(r["gold"]) for r, v in zip(test, x)]))
    out["always none"] = 100 * float(np.mean([not r["gold"] for r in test]))
    return out


def main(run_dir: str) -> None:
    rows = {}
    for t in TRACKS:
        path = Path(run_dir) / f"{t}.jsonl"
        if path.exists():
            rows[t] = track_rows([r for r in map(json.loads, path.open()) if "error" not in r and "noul_ctx" in r])
    held_out = [t for t in rows if t != "synthetic"]
    print("| method | " + " | ".join(rows) + " | macro (held-out) |")
    print("|---|" + "---|" * (len(rows) + 1))
    for k in next(iter(rows.values())):
        print(f"| {k} | " + " | ".join(f"{rows[t][k]:.1f}" for t in rows) + f" | {np.mean([rows[t][k] for t in held_out]):.1f} |")


if __name__ == "__main__":
    main(sys.argv[1])
