import json

import numpy as np

from bzaf.client import DecisionClient
from bzaf.data import load_synthetic
from bzaf.readout import build_questions, run_readout
from bzaf.schema import Item, read_items, write_items


class FakeClient(DecisionClient):
    """Answers like a TypeSafe-compatible server, from the item's gold set, and records request sizes."""

    def __init__(self, gold_by_state, max_seen):
        super().__init__("http://fake", model="fake")
        self.gold_by_state, self.max_seen = gold_by_state, max_seen

    def decide(self, state, questions):
        self.max_seen.append(len(questions))
        gold_opts = self.gold_by_state[json.dumps(state, sort_keys=True)]
        answers = {}
        for key, q in questions.items():
            if q["type"] == "noul":
                opt = q["instructions"].rsplit("Option: ", 1)[1]
                answers[key] = {"type": "noul", "noul": 0.9 if opt in gold_opts else 0.1}
            elif key == "pick":
                names = list(q["criteria"])
                w = np.array([3.0 if n in gold_opts else 1.0 for n in names]); w /= w.sum()
                answers[key] = {"type": "choice", "probabilities": dict(zip(names, w.tolist()))}
            else:
                names = list(q["criteria"])
                answers[key] = {"type": "choice", "probabilities": {n: float(int(n) == len(gold_opts)) for n in names}}
        return {"answers": answers}


def test_synthetic_items_are_valid_and_varied(tmp_path):
    items = load_synthetic(n=200, seed=3)
    sizes = {len(it.gold) for it in items}
    assert 0 in sizes and max(sizes) >= 4
    write_items(items, tmp_path / "s.jsonl")
    assert [it.id for it in read_items(tmp_path / "s.jsonl")] == [it.id for it in items]


def test_build_questions_shapes():
    it = Item("a", "d", "state", "Q?", ["x", "y", "z"], [1])
    qs = build_questions(it)
    assert len(qs) == 3 + 3 + 2
    assert list(qs["count"]["criteria"]) == ["0", "1", "2", "3"]
    assert "All options:" in qs["noulctx_0"]["instructions"]


def test_run_readout_chunks_and_resumes(tmp_path):
    items = load_synthetic(n=12, seed=5)
    gold_by_state = {json.dumps(it.state, sort_keys=True): {it.options[g] for g in it.gold} for it in items}
    seen = []
    out = tmp_path / "r.jsonl"
    run_readout(FakeClient(gold_by_state, seen), items[:6], out, max_questions=7, log=lambda _: None)
    run_readout(FakeClient(gold_by_state, seen), items, out, max_questions=7, log=lambda _: None)
    recs = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(recs) == 12 and max(seen) <= 7
    for r, it in zip(recs, items):
        assert r["gold"] == it.gold
        assert len(r["noul"]) == len(r["noul_ctx"]) == len(r["pick"]) == r["k"]
        assert len(r["count"]) == r["k"] + 1
        assert {j for j, p in enumerate(r["noul"]) if p > 0.5} == set(it.gold)
