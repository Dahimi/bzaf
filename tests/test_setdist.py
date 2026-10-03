import itertools

import numpy as np
import pytest

from bzaf.setdist import SetDistribution, log_esp


def all_subsets(k):
    return [s for n in range(k + 1) for s in itertools.combinations(range(k), n)]


def brute(dist):
    return {s: np.exp(dist.log_prob(s)) for s in all_subsets(dist.k)}


@pytest.fixture
def rng():
    return np.random.default_rng(0)


def test_log_esp_matches_enumeration(rng):
    z = rng.normal(size=6)
    w = np.exp(z)
    for s in range(7):
        want = sum(np.prod(w[list(c)]) for c in itertools.combinations(range(6), s))
        assert np.isclose(np.exp(log_esp(z)[s]), want)


def test_sums_to_one_and_count_marginal(rng):
    z = rng.normal(size=6)
    c = rng.dirichlet(np.ones(7))
    d = SetDistribution(z, np.log(c))
    p = brute(d)
    assert np.isclose(sum(p.values()), 1.0)
    for s in range(7):
        assert np.isclose(sum(v for k, v in p.items() if len(k) == s), c[s])


def test_independent_equals_bernoulli_product(rng):
    probs = rng.uniform(0.05, 0.95, size=5)
    d = SetDistribution.independent(probs)
    for s in all_subsets(5):
        y = np.isin(np.arange(5), s)
        want = np.prod(np.where(y, probs, 1 - probs))
        assert np.isclose(np.exp(d.log_prob(s)), want)
    assert np.allclose(d.marginals(), probs)


def test_count_one_reduces_to_softmax(rng):
    z = rng.normal(size=5)
    d = SetDistribution(z, np.log([1e-300, 1, 1e-300, 1e-300, 1e-300, 1e-300]))
    soft = np.exp(z) / np.exp(z).sum()
    for i in range(5):
        assert np.isclose(np.exp(d.log_prob([i])), soft[i])


def test_marginals_match_enumeration(rng):
    z = rng.normal(size=6)
    d = SetDistribution(z, np.log(rng.dirichlet(np.ones(7))))
    p = brute(d)
    want = [sum(v for k, v in p.items() if i in k) for i in range(6)]
    assert np.allclose(d.marginals(), want)


def test_top_sets_match_enumeration(rng):
    for _ in range(20):
        z = rng.normal(size=7) * 2
        d = SetDistribution(z, np.log(rng.dirichlet(np.ones(8))))
        p = sorted(brute(d).items(), key=lambda kv: -kv[1])
        got = d.top_sets(10)
        assert [round(v, 12) for _, v in got] == [round(v, 12) for _, v in p[:10]]
        assert got[0][0] == d.mode()


def test_restrict_count(rng):
    d = SetDistribution(rng.normal(size=5), np.log(rng.dirichlet(np.ones(6))))
    r = d.restrict_count(1, 2)
    p = brute(r)
    assert np.isclose(sum(p.values()), 1.0)
    assert all(v == 0 or 1 <= len(k) <= 2 for k, v in p.items())
    assert all(1 <= len(s) <= 2 for s, _ in r.top_sets(5))


def test_large_k_is_stable():
    z = np.linspace(-8, 8, 255)
    d = SetDistribution(z, np.log(np.full(256, 1 / 256)))
    m = d.marginals()
    assert np.all(np.isfinite(m)) and np.all((m >= 0) & (m <= 1 + 1e-9))
    assert np.isclose(m.sum(), np.sum(np.arange(256) / 256))
    assert len(d.top_sets(5)) == 5


def test_from_scores_handles_zero_probabilities():
    d = SetDistribution.from_scores([0.7, 0.3, 0.0], [0.0, 0.2, 0.8, 0.0])
    assert np.isfinite(d.log_prob([2]))
    assert d.mode() == (0, 1)
