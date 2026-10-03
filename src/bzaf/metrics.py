"""Set-level metrics. A prediction of None means the model failed on that item; it scores as wrong (exact 0, F1 0)
and is left out of the log-loss, which is reported with its coverage."""
from __future__ import annotations

from typing import Sequence

import numpy as np


def set_f1(pred: set, gold: set) -> float:
    if not pred and not gold:
        return 1.0
    return 2 * len(pred & gold) / (len(pred) + len(gold))


def evaluate(preds: Sequence[set | None], golds: Sequence[set], logps: Sequence[float | None] | None = None) -> dict:
    n = len(golds)
    exact, f1, count_ok, sizes = [], [], [], []
    tp = fp = fn = 0
    for p, g in zip(preds, golds):
        if p is None:
            exact.append(0.0); f1.append(0.0); count_ok.append(0.0)
            fn += len(g)
            continue
        exact.append(float(p == g)); f1.append(set_f1(p, g)); count_ok.append(float(len(p) == len(g)))
        sizes.append(len(p))
        tp += len(p & g); fp += len(p - g); fn += len(g - p)
    out = {
        "n": n,
        "exact": float(np.mean(exact)) if n else float("nan"),
        "example_f1": float(np.mean(f1)) if n else float("nan"),
        "micro_f1": 2 * tp / (2 * tp + fp + fn) if (tp + fp + fn) else 1.0,
        "count_acc": float(np.mean(count_ok)) if n else float("nan"),
        "mean_pred_size": float(np.mean(sizes)) if sizes else float("nan"),
        "mean_gold_size": float(np.mean([len(g) for g in golds])) if n else float("nan"),
        "per_item_exact": exact,
    }
    if logps is not None:
        vals = [-lp for lp in logps if lp is not None]
        out["set_nll"] = float(np.mean(vals)) if vals else float("nan")
        out["nll_coverage"] = len(vals) / n if n else 0.0
        out["per_item_nll"] = [None if lp is None else -lp for lp in logps]
    return out


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
