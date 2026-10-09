"""Untrained multi-answer predictors built from E01 readouts (see experiments/E01-readout-baselines).

Each predictor turns one readout record into a predicted set and, where it defines one, a full distribution over
sets (for the log-loss). Predictors that need tuning fit on a dev split of the same dataset only.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .setdist import SetDistribution, logit


@dataclass
class Prediction:
    subset: set
    dist: SetDistribution | None = None


class Predictor:
    name = "base"
    needs: tuple[str, ...] = ()

    def available(self, rec: dict) -> bool:
        return "error" not in rec and all(f in rec for f in self.needs)

    def fit(self, dev: list[dict]) -> "Predictor":
        return self

    def predict(self, rec: dict) -> Prediction:
        raise NotImplementedError


def fit_platt(x: np.ndarray, y: np.ndarray, iters: int = 50, ridge: float = 1e-3) -> tuple[float, float]:
    """Fit P(y=1) = sigmoid(a*x + b) by damped Newton. Returns (a, b); (1, 0) leaves probabilities unchanged."""
    X = np.stack([x, np.ones_like(x)], axis=1)
    theta = np.array([1.0, 0.0])
    prior = theta.copy()

    def loss(t):
        z = X @ t
        return float(np.sum(np.logaddexp(0.0, z) - y * z) + 0.5 * ridge * np.sum((t - prior) ** 2))

    cur = loss(theta)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ theta, -500, 500)))
        g = X.T @ (p - y) + ridge * (theta - prior)
        H = (X * (p * (1 - p))[:, None]).T @ X + ridge * np.eye(2)
        step = np.linalg.solve(H, g)
        t = 1.0
        while t > 1e-6 and loss(theta - t * step) > cur:  # backtrack: plain Newton overshoots from a far start
            t /= 2
        theta = theta - t * step
        new = loss(theta)
        if abs(cur - new) < 1e-10 * max(1.0, abs(cur)):
            break
        cur = new
    return float(theta[0]), float(theta[1])


class Independent(Predictor):
    """One yes/no per option, each kept if its probability is above 0.5 (the mode of the independent product).
    calibrate=True first refits the probabilities on the dev split (Platt scaling: two numbers per dataset)."""

    def __init__(self, field: str = "noul", calibrate: bool = False):
        self.field, self.calibrate, self.needs = field, calibrate, (field,)
        self.name = f"{field}+platt" if calibrate else f"{field}@0.5"
        self.ab = (1.0, 0.0)

    def fit(self, dev):
        if self.calibrate:
            xs, ys = [], []
            for r in dev:
                if self.available(r):
                    xs.extend(logit(r[self.field])); ys.extend(j in set(r["gold"]) for j in range(r["k"]))
            if xs:
                self.ab = fit_platt(np.asarray(xs), np.asarray(ys, dtype=float))
        return self

    def predict(self, rec):
        a, b = self.ab
        dist = SetDistribution(a * logit(rec[self.field]) + b)
        return Prediction(set(dist.mode()), dist)


class ShippedThreshold(Predictor):
    """A native multi-answer type as its server ships it: keep options whose probability is above the server's own
    threshold (recorded with the readout). The set distribution is the independent product shifted so its mode is that
    thresholded set."""

    def __init__(self, field: str = "set"):
        self.field, self.needs, self.name = field, (field, f"{field}_threshold"), f"{field}@shipped"

    def predict(self, rec):
        dist = SetDistribution(logit(rec[self.field]) - logit([rec[f"{self.field}_threshold"]])[0])
        return Prediction(set(dist.mode()), dist)


class NativeTop1(Predictor):
    """Single-answer items (general track): the model's own answer, i.e. the most likely option of the question asked
    in its own type. Its distribution puts the count at exactly 1, so set log-loss is the usual log-loss, exact-set
    accuracy is accuracy, and the predicted set's probability is the answer's confidence."""
    name, needs = "native@top1", ("native",)

    def predict(self, rec):
        p = np.asarray(rec["native"], dtype=float)
        count = np.zeros(len(p) + 1)
        count[1] = 1.0
        dist = SetDistribution.from_scores(p / p.sum(), count)
        return Prediction({int(np.argmax(p))}, dist)


class OursSet(Predictor):
    """Our trained model's multi-answer question: its option logits and its count head define the set distribution;
    the answer is the most likely set."""
    name, needs = "ours@mode", ("multi_z", "multi_count")

    def predict(self, rec):
        k = rec["k"]
        c = np.zeros(k + 1)
        n = min(k + 1, len(rec["multi_count"]))
        c[:n] = rec["multi_count"][:n]
        dist = SetDistribution.from_logits_and_count(np.asarray(rec["multi_z"], dtype=float), c / c.sum())
        return Prediction(set(dist.mode()), dist)


class OursCalibrated(Predictor):
    """Our model's set distribution adapted to a task with k labelled dev items (default: the whole dev split, the same
    labels `pick+dev_prior` and `noul_ctx+platt` fit on), using the same add-one count histogram as `pick+dev_prior`.

    prior  the histogram replaces the model's count distribution (the item's own count evidence is dropped)
    match  the model's count distribution is reweighted, P'(s | item) ∝ P(s | item) · hist(s) / mean_dev P(s), so its
           average over the dev items matches the task's histogram while each item keeps its own count evidence
    """
    needs = ("multi_z", "multi_count")

    def __init__(self, mode: str = "match", k: int | None = None):
        self.mode, self.k = mode, k
        self.name = f"ours+dev_{mode}" + (f"@{k}" if k else "")
        self.hist: np.ndarray | None = None
        self.ratio: np.ndarray | None = None

    @staticmethod
    def _count(rec: dict, width: int) -> np.ndarray:
        c = np.zeros(width)
        n = min(width, len(rec["multi_count"]), rec["k"] + 1)
        c[:n] = rec["multi_count"][:n]
        return c / max(c.sum(), 1e-12)

    def fit(self, dev):
        import hashlib

        dev = [r for r in dev if self.available(r)]
        if self.k:  # a fixed pseudo-random subset of the dev split
            dev = sorted(dev, key=lambda r: hashlib.md5(r["id"].encode()).hexdigest())[: self.k]
        width = max([r["k"] for r in dev] + [1]) + 1
        h = np.ones(width)
        for r in dev:
            h[len(r["gold"])] += 1
        self.hist = h / h.sum()
        if self.mode == "match" and dev:
            mean = np.mean([self._count(r, width) for r in dev], axis=0)
            self.ratio = np.clip(self.hist / np.maximum(mean, 1e-6), 1e-3, 1e3)
        return self

    def predict(self, rec):
        width = rec["k"] + 1
        if self.mode == "prior" and self.hist is not None:
            c = np.full(width, 1e-6)
            n = min(len(self.hist), width)
            c[:n] = self.hist[:n]
        else:
            c = self._count(rec, width)
            if self.ratio is not None:
                r = np.ones(width)
                n = min(len(self.ratio), width)
                r[:n] = self.ratio[:n]
                c = c * r
        c = c / c.sum()
        dist = SetDistribution.from_logits_and_count(np.asarray(rec["multi_z"], dtype=float), c)
        return Prediction(set(dist.mode()), dist)


class ChoiceTop1(Predictor):
    """Today's single-answer Choice: always exactly one option."""
    name, needs = "pick@top1", ("pick",)

    def predict(self, rec):
        return Prediction({int(np.argmax(rec["pick"]))})


class OracleCount(Predictor):
    """Rank options by `field` and keep as many as the true number of answers. With field="pick" this is the upper
    bound for the count approach; with a yes/no field it is the control that tells whether Choice ranks better than
    yes/no or whether the whole gap is counting."""

    def __init__(self, field: str = "pick"):
        self.field, self.needs, self.name = field, (field,), f"{field}+true_count"

    def predict(self, rec):
        s = len(rec["gold"])
        return Prediction(set(int(i) for i in np.argsort(-np.asarray(rec[self.field]), kind="stable")[:s]))


ChoiceOracleCount = OracleCount  # backwards-compatible name


class AlwaysNone(Predictor):
    """Reference: always answer "none of these". Shows how much exact-set accuracy an empty answer gets for free."""
    name, needs = "always_none", ()

    def predict(self, rec):
        return Prediction(set())


class ScoresPlusCount(Predictor):
    """The count approach without training: option scores from `field` plus the model's own answer to
    "how many apply?". field="pick" uses Choice probabilities; "noul"/"noul_ctx" use per-option yes/no logits
    (i.e. independent yes/no with its implied count replaced by the asked count)."""

    def __init__(self, field: str = "pick"):
        self.field, self.needs, self.name = field, (field, "count"), f"{field}+count"

    def predict(self, rec):
        if self.field == "pick":
            dist = SetDistribution.from_scores(rec["pick"], rec["count"])
        else:
            dist = SetDistribution.from_logits_and_count(logit(rec[self.field]), rec["count"])
        return Prediction(set(dist.mode()), dist)


class ScoresPlusDevPrior(Predictor):
    """Option scores plus the dataset's typical number of answers (count histogram of the dev split, add-one smoothed),
    the same for every item. Control for the count head: if this matches item-level counting, a learned count head
    only needs the dataset prior; if not, the count must be read from each item."""

    def __init__(self, field: str = "pick"):
        self.field, self.needs, self.name = field, (field,), f"{field}+dev_prior"
        self.hist: np.ndarray | None = None

    def fit(self, dev):
        sizes = [len(r["gold"]) for r in dev if "error" not in r]
        kmax = max([r["k"] for r in dev if "error" not in r] + [1])
        h = np.ones(kmax + 1)
        for n in sizes:
            h[n] += 1
        self.hist = h / h.sum()
        return self

    def predict(self, rec):
        h = self.hist if self.hist is not None else np.ones(rec["k"] + 1)
        c = np.full(rec["k"] + 1, 1e-6)
        n = min(len(h), rec["k"] + 1)
        c[:n] = h[:n]
        c = c / c.sum()
        if self.field == "pick":
            dist = SetDistribution.from_scores(rec["pick"], c)
        else:
            dist = SetDistribution.from_logits_and_count(logit(rec[self.field]), c)
        return Prediction(set(dist.mode()), dist)


def default_predictors() -> list[Predictor]:
    return [
        Independent("noul"),
        Independent("noul", calibrate=True),
        Independent("noul_ctx"),
        Independent("noul_ctx", calibrate=True),
        AlwaysNone(),
        ChoiceTop1(),
        OracleCount("pick"),
        OracleCount("noul"),
        OracleCount("noul_ctx"),
        ScoresPlusCount("pick"),
        ScoresPlusCount("noul"),
        ScoresPlusCount("noul_ctx"),
        ScoresPlusDevPrior("pick"),
        ScoresPlusDevPrior("noul_ctx"),
        NativeTop1(),
        OursSet(),
        OursCalibrated("prior"),
        OursCalibrated("prior", k=16),
        OursCalibrated("prior", k=64),
        OursCalibrated("match"),
        ShippedThreshold("set"),
        Independent("set", calibrate=True),
        OracleCount("set"),
        ScoresPlusDevPrior("set"),
    ]
