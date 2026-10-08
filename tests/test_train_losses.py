import numpy as np
import pytest

torch = pytest.importorskip("torch")

from bzaf.setdist import SetDistribution  # noqa: E402
from bzaf.train.losses import choice_ce, distill, set_nll  # noqa: E402


def test_set_nll_matches_numpy_set_distribution():
    rng = np.random.default_rng(0)
    rows, width, cmax = 6, 7, 5
    z = torch.tensor(rng.normal(size=(rows, width)) * 2, dtype=torch.float32)
    mask = torch.ones(rows, width, dtype=torch.bool)
    mask[3, 5:] = False                         # a row with 5 options
    c = torch.tensor(rng.normal(size=(rows, cmax + 1)), dtype=torch.float32)
    gold = torch.zeros(rows, width, dtype=torch.bool)
    for r, idx in enumerate([[0], [1, 2], [], [0, 3, 4], [6], [1, 2, 3, 4, 5]]):
        gold[r, idx] = True
    out = set_nll(z, c, gold, mask)
    for r in range(rows):
        k = int(mask[r].sum())
        counts = torch.softmax(c[r, : min(k, cmax) + 1], 0).numpy()
        counts = np.concatenate([counts, np.zeros(k + 1 - len(counts))])
        d = SetDistribution(z[r, :k].numpy().astype(float), np.log(np.clip(counts, 1e-300, None)))
        ref = -d.log_prob([int(i) for i in torch.nonzero(gold[r]).flatten()])
        assert out["nll"][r].item() == pytest.approx(ref, rel=1e-4, abs=1e-4), r


def test_single_answer_and_distill():
    z = torch.tensor([[2.0, 0.0, -1.0]])
    mask = torch.ones(1, 3, dtype=torch.bool)
    assert choice_ce(z, torch.tensor([0]), mask).item() == pytest.approx(-torch.log_softmax(z, -1)[0, 0].item())
    # count fixed at 1: the set likelihood of {i} is the Choice probability of i
    c = torch.tensor([[-1e4, 0.0, -1e4, -1e4]])
    gold = torch.tensor([[False, True, False]])
    assert set_nll(z, c, gold, mask)["nll"].item() == pytest.approx(choice_ce(z, torch.tensor([1]), mask).item(), abs=1e-4)
    assert distill(z, z, mask).item() == pytest.approx(0.0, abs=1e-6)
    assert distill(z, torch.zeros(1, 3), mask).item() > 0
    z.requires_grad_(True)
    set_nll(z, c, gold, mask)["nll"].sum().backward()
    assert torch.isfinite(z.grad).all()
