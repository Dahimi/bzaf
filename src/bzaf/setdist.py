"""Distributions over answer sets for a multi-answer question with K options.

One family covers every predictor in this project:

    P(S) = P(|S| = s) * prod_{i in S} w_i / e_s(w),      w_i = exp(z_i)

where e_s is the elementary symmetric polynomial of degree s (the sum of the weight products over all sets of
size s). Read it as: first decide how many options apply, then decide which, in proportion to the options' weights.

- Count approach: z = the option scores (Choice logits), P(|S|) = the count head.
- Independent per-option probabilities p_i (one Noul or sigmoid per option): z = logit(p_i) and P(|S|) is the
  Poisson-binomial count those probabilities imply. Then P(S) = prod p_i^y_i (1 - p_i)^(1 - y_i) exactly. So the
  count approach is "per-option scores plus a learned count" and switching the count off recovers independence.

Everything is computed exactly in log space: e_s by an O(K^2) recursion, marginals by leave-one-out recursions,
the most likely sets by best-first search per size. No sum over 2^K subsets anywhere.
"""
from __future__ import annotations

import heapq
from typing import Iterable, Sequence

import numpy as np

EPS = 1e-6


def _logsumexp(x: np.ndarray) -> float:
    m = np.max(x)
    if not np.isfinite(m):
        return float(m)
    return float(m + np.log(np.sum(np.exp(x - m))))


def log_esp(z: np.ndarray) -> np.ndarray:
    """log e_0..e_K of w = exp(z). e_0 = 1."""
    k = len(z)
    out = np.full(k + 1, -np.inf)
    out[0] = 0.0
    for i, zi in enumerate(z):
        out[1 : i + 2] = np.logaddexp(out[1 : i + 2], out[0 : i + 1] + zi)
    return out


def log_esp_leave_one_out(z: np.ndarray) -> np.ndarray:
    """Row j holds log e_0..e_{K-1} of w with option j removed."""
    k = len(z)
    out = np.full((k, k), -np.inf)
    out[:, 0] = 0.0
    for i, zi in enumerate(z):
        rows = np.arange(k) != i
        out[rows, 1:] = np.logaddexp(out[rows, 1:], out[rows, :-1] + zi)
    return out


def logit(p: Sequence[float]) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p) - np.log1p(-p)


class SetDistribution:
    """A distribution over subsets of range(K)."""

    def __init__(self, logits: Sequence[float], count_logprobs: Sequence[float] | None = None):
        z = np.asarray(logits, dtype=float)
        if z.ndim != 1 or len(z) == 0 or not np.all(np.isfinite(z)):
            raise ValueError("logits must be a non-empty 1-D array of finite values")
        self.logits = z
        self.k = len(z)
        self.log_e = log_esp(z)
        if count_logprobs is None:
            # Independent Bernoulli(sigmoid(z)): P(s) = e_s(odds) * prod(1 - p_i).
            c = self.log_e - np.sum(np.logaddexp(0.0, z))
        else:
            given = np.asarray(count_logprobs, dtype=float)
            c = np.full(self.k + 1, -np.inf)
            n = min(len(given), self.k + 1)
            c[:n] = given[:n]
            total = _logsumexp(c)
            if not np.isfinite(total):
                raise ValueError("count distribution has no mass on sizes 0..K")
            c = c - total
        self.count_logprobs = c

    # constructors -----------------------------------------------------------------------------------------------
    @classmethod
    def independent(cls, probs: Sequence[float]) -> "SetDistribution":
        """Independent per-option probabilities (one Noul per option)."""
        return cls(logit(probs))

    @classmethod
    def from_scores(cls, probs: Sequence[float], count_probs: Sequence[float]) -> "SetDistribution":
        """Option probabilities from a Choice (or any positive scores) plus a distribution over counts 0..K."""
        p = np.clip(np.asarray(probs, dtype=float), EPS, None)
        c = np.clip(np.asarray(count_probs, dtype=float), EPS, None)  # model outputs are rounded; keep log-loss finite
        return cls(np.log(p), np.log(c))

    @classmethod
    def from_logits_and_count(cls, logits: Sequence[float], count_probs: Sequence[float]) -> "SetDistribution":
        c = np.clip(np.asarray(count_probs, dtype=float), EPS, None)
        return cls(logits, np.log(c))

    # queries ----------------------------------------------------------------------------------------------------
    @property
    def count_probs(self) -> np.ndarray:
        return np.exp(self.count_logprobs)

    def log_prob(self, subset: Iterable[int]) -> float:
        s = sorted(set(subset))
        if any(i < 0 or i >= self.k for i in s):
            raise IndexError("option index out of range")
        n = len(s)
        return float(self.count_logprobs[n] + np.sum(self.logits[s]) - self.log_e[n])

    def marginals(self) -> np.ndarray:
        """P(option i is in the set)."""
        loo = log_esp_leave_one_out(self.logits)  # [K, K]: log e_{s-1}(w_{-i}) at column s-1
        sizes = np.arange(1, self.k + 1)
        terms = self.count_logprobs[sizes][None, :] + self.logits[:, None] + loo[:, sizes - 1] - self.log_e[sizes][None, :]
        return np.exp(np.logaddexp.reduce(terms, axis=1))

    def restrict_count(self, lo: int = 0, hi: int | None = None) -> "SetDistribution":
        """Condition on lo <= |S| <= hi, e.g. exactly one (1, 1), at most three (0, 3), at least one (1, None)."""
        hi = self.k if hi is None else min(hi, self.k)
        c = np.full(self.k + 1, -np.inf)
        c[lo : hi + 1] = self.count_logprobs[lo : hi + 1]
        out = object.__new__(SetDistribution)
        out.logits, out.k, out.log_e = self.logits, self.k, self.log_e
        total = _logsumexp(c)
        if not np.isfinite(total):
            raise ValueError("no probability mass in the requested count range")
        out.count_logprobs = c - total
        return out

    def _top_of_size(self, s: int, n: int) -> list[tuple[float, tuple[int, ...]]]:
        """The n most likely sets of size s, by sum of logits (best-first search over sorted positions)."""
        order = np.argsort(-self.logits, kind="stable")
        zs = self.logits[order]
        if s == 0:
            return [(0.0, ())]
        start = tuple(range(s))
        heap = [(-float(np.sum(zs[list(start)])), start)]
        seen = {start}
        out = []
        while heap and len(out) < n:
            neg, pos = heapq.heappop(heap)
            out.append((-neg, tuple(sorted(int(order[p]) for p in pos))))
            chosen = set(pos)
            for t, p in enumerate(pos):
                q = p + 1
                if q < self.k and q not in chosen:
                    nxt = pos[:t] + (q,) + pos[t + 1 :]
                    if nxt not in seen:
                        seen.add(nxt)
                        heapq.heappush(heap, (neg + float(zs[p] - zs[q]), nxt))
        return out

    def top_sets(self, n: int = 5) -> list[tuple[tuple[int, ...], float]]:
        """The n most likely answer sets with their probabilities, most likely first."""
        cands = []
        for s in range(self.k + 1):
            if not np.isfinite(self.count_logprobs[s]):
                continue
            for zsum, subset in self._top_of_size(s, n):
                cands.append((float(self.count_logprobs[s] + zsum - self.log_e[s]), subset))
        cands.sort(key=lambda x: -x[0])
        return [(subset, float(np.exp(lp))) for lp, subset in cands[:n]]

    def mode(self) -> tuple[int, ...]:
        return self.top_sets(1)[0][0]
