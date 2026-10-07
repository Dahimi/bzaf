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
            elif q["type"] == "set":
                names = list(q["criteria"])
                sets = {key: {"selected": [n for n in names if n in gold_opts],
                              "probabilities": {n: 0.8 if n in gold_opts else 0.2 for n in names}}}
                return {"answers": answers, "sets": sets, "thresholds": {key: 0.5}}
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
    recs = {r["id"]: r for r in map(json.loads, out.read_text().splitlines())}
    assert len(recs) == 12 and max(seen) <= 7
    for it in items:
        r = recs[it.id]
        assert r["gold"] == it.gold
        assert len(r["noul"]) == len(r["noul_ctx"]) == len(r["pick"]) == r["k"]
        assert len(r["count"]) == r["k"] + 1
        assert {j for j, p in enumerate(r["noul"]) if p > 0.5} == set(it.gold)


class FlakyClient(FakeClient):
    """Fails every item once, then answers normally."""

    def __init__(self, *a):
        super().__init__(*a)
        self.failed = set()

    def decide(self, state, questions):
        key = json.dumps(state, sort_keys=True)
        if key not in self.failed:
            self.failed.add(key)
            raise RuntimeError("cold start")
        return super().decide(state, questions)


def test_failed_items_are_retried_without_duplicates(tmp_path):
    items = load_synthetic(n=10, seed=7)
    gold_by_state = {json.dumps(it.state, sort_keys=True): {it.options[g] for g in it.gold} for it in items}
    client, out = FlakyClient(gold_by_state, []), tmp_path / "r.jsonl"
    run_readout(client, items, out, concurrency=4, log=lambda _: None)
    assert all("error" in json.loads(line) for line in out.read_text().splitlines())
    run_readout(client, items, out, concurrency=4, log=lambda _: None)
    recs = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(recs) == 10 and not any("error" in r for r in recs)
    assert {r["id"] for r in recs} == {it.id for it in items}


def test_native_set_variant_reads_probabilities_and_threshold(tmp_path):
    from bzaf.predictors import ShippedThreshold
    from bzaf.score import score_records

    items = load_synthetic(n=40, seed=5)
    gold_by_state = {json.dumps(it.state, sort_keys=True): {it.options[j] for j in it.gold} for it in items}
    out = tmp_path / "set.jsonl"
    run_readout(FakeClient(gold_by_state, []), items, out, variants=["set"], log=lambda *_: None)
    recs = [json.loads(line) for line in out.read_text().splitlines()]
    assert all("set" in r and r["set_threshold"] == 0.5 for r in recs)
    for r in recs:
        assert ShippedThreshold().predict(r).subset == set(r["gold"])
    rows = score_records(recs)["synthetic"]["predictors"]
    assert rows["set@shipped"]["exact"] == 1.0 and "set+true_count" in rows
