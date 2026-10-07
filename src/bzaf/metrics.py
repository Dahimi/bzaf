"""Set-level metrics. A prediction of None means the model failed on that item; it scores as wrong (exact 0, F1 0)
and is left out of the log-loss, which is reported with its coverage."""
from __future__ import annotations

from typing import Sequence

import numpy as np


def set_f1(pred: set, gold: set) -> float:
    if not pred and not gold:
        return 1.0
    return 2 * len(pred & gold) / (len(pred) + len(gold))


def set_jaccard(pred: set, gold: set) -> float:
    if not pred and not gold:
        return 1.0
    return len(pred & gold) / len(pred | gold)


def evaluate(preds: Sequence[set | None], golds: Sequence[set], logps: Sequence[float | None] | None = None,
             confs: Sequence[float | None] | None = None) -> dict:
    """`logps`: log-probability of the gold set (set log-loss). `confs`: probability the predictor gives its own
    predicted set (set calibration and selective automation). Both only for predictors that define a distribution."""
    n = len(golds)
    exact, f1, jac, count_ok, count_err, sizes = [], [], [], [], [], []
    tp = fp = fn = 0
    for p, g in zip(preds, golds):
        if p is None:
            exact.append(0.0); f1.append(0.0); jac.append(0.0); count_ok.append(0.0); count_err.append(float(len(g)))
            fn += len(g)
            continue
        exact.append(float(p == g)); f1.append(set_f1(p, g)); jac.append(set_jaccard(p, g))
        count_ok.append(float(len(p) == len(g))); count_err.append(float(abs(len(p) - len(g))))
        sizes.append(len(p))
        tp += len(p & g); fp += len(p - g); fn += len(g - p)
    out = {
        "n": n,
        "exact": float(np.mean(exact)) if n else float("nan"),
        "example_f1": float(np.mean(f1)) if n else float("nan"),
        "jaccard": float(np.mean(jac)) if n else float("nan"),
        "micro_f1": 2 * tp / (2 * tp + fp + fn) if (tp + fp + fn) else 1.0,
        "count_acc": float(np.mean(count_ok)) if n else float("nan"),
        "count_abs_err": float(np.mean(count_err)) if n else float("nan"),
        "mean_pred_size": float(np.mean(sizes)) if sizes else float("nan"),
        "mean_gold_size": float(np.mean([len(g) for g in golds])) if n else float("nan"),
        "per_item_exact": exact,
        "per_item_f1": f1,
    }
    if logps is not None:
        vals = [-lp for lp in logps if lp is not None]
        out["set_nll"] = float(np.mean(vals)) if vals else float("nan")
        out["nll_coverage"] = len(vals) / n if n else 0.0
        out["per_item_nll"] = [None if lp is None else -lp for lp in logps]
    if confs is not None:
        pairs = [(c, e) for c, e in zip(confs, exact) if c is not None]
        if pairs:
            c, e = np.array(pairs, dtype=float).T
            out["ece"] = ece(c, e)
            out.update(selective(c, e))
    return out


def ece(conf: np.ndarray, correct: np.ndarray, bins: int = 10) -> float:
    """Expected calibration error of the predicted set's probability against exact-set correctness: items sorted by
    confidence into `bins` equal-size groups; mean |stated probability - observed accuracy|, weighted by group size."""
    order = np.argsort(conf, kind="stable")
    groups = [g for g in np.array_split(order, min(bins, len(order))) if len(g)]
    return float(sum(len(g) * abs(conf[g].mean() - correct[g].mean()) for g in groups) / len(conf))


def selective(conf: np.ndarray, correct: np.ndarray, targets: tuple[float, ...] = (0.9, 0.95)) -> dict:
    """Selective automation: answer the most confident items, hand the rest to a person. Returns the largest share of
    items that can be answered at each target exact-set accuracy (0 if none), and the area under the risk-coverage
    curve (mean error over all coverage levels; lower is better)."""
    order = np.argsort(-conf, kind="stable")
    acc = np.cumsum(correct[order]) / np.arange(1, len(order) + 1)
    out = {"aurc": float(np.mean(1 - acc))}
    for t in targets:
        ok = np.nonzero(acc >= t)[0]
        out[f"cov@{int(t * 100)}"] = float((ok.max() + 1) / len(order)) if len(ok) else 0.0
    return out


def satabench_metrics(preds: Sequence[set | None], golds: Sequence[set], ks: Sequence[int]) -> dict:
    """SATA-Bench's own definitions (sata-bench/sata-bench, src/satabench/evaluation/metrics/metrics.py), so our SATA
    numbers can sit next to the paper's. Two differences from ours: EM leaves out items where the model selected
    nothing (it divides by the number of non-empty predictions), and RStd is the spread of per-position recall
    (option A, B, ...), a position-bias measure. Failed items are treated as empty predictions."""
    P = [p if p is not None else set() for p in preds]
    nonempty = [i for i, p in enumerate(P) if p]
    em = sum(P[i] == golds[i] for i in nonempty) / len(nonempty) if nonempty else 0.0
    ji = float(np.mean([len(p & g) / len(p | g) if p | g else 1.0 for p, g in zip(P, golds)]))
    recalls = []
    for pos in range(max(ks)):
        hits = [pos in p for p, g in zip(P, golds) if pos in g]
        if hits:
            recalls.append(100 * float(np.mean(hits)))
    return {"EM": float(em), "JI": ji, "CtDifAbs": float(np.mean([abs(len(p) - len(g)) for p, g in zip(P, golds)])),
            "CtDif": float(np.mean([len(p) - len(g) for p, g in zip(P, golds)])), "RStd": float(np.std(recalls)) if recalls else float("nan"),
            "abstained": len(P) - len(nonempty)}


def bootstrap_ci(values: Sequence[float], n_boot: int = 2000, seed: int = 0, alpha: float = 0.05) -> tuple[float, float]:
    v = np.asarray([x for x in values if x is not None], dtype=float)
    if len(v) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), size=(n_boot, len(v)))].mean(axis=1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def paired_diff_ci(a: Sequence[float], b: Sequence[float], **kw) -> tuple[float, float, float]:
    """Mean of a - b over items both have, with a bootstrap CI."""
    d = [x - y for x, y in zip(a, b) if x is not None and y is not None]
    lo, hi = bootstrap_ci(d, **kw)
    return float(np.mean(d)) if d else float("nan"), lo, hi
