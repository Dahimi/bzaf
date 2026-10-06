import json

import numpy as np

from bzaf.metrics import evaluate, set_f1
from bzaf.predictors import AlwaysNone, ChoiceOracleCount, Independent, OracleCount, ScoresPlusCount, ScoresPlusDevPrior, fit_platt
from bzaf.score import format_report, score_files, score_records


def test_set_f1_and_evaluate():
    assert set_f1(set(), set()) == 1.0
    assert set_f1({0, 1}, {1}) == 2 / 3
    m = evaluate([{0, 1}, {2}, None], [{0, 1}, {1}, {0}])
    assert m["exact"] == 1 / 3
    assert m["count_acc"] == 2 / 3
    # tp=2 (item 1), fp=1 + fn=1 (item 2), fn=1 (failed item 3)
    assert np.isclose(m["micro_f1"], 4 / 7)


def test_platt_recovers_scale():
    rng = np.random.default_rng(0)
    x = rng.normal(size=20000) * 3
    y = (rng.random(20000) < 1 / (1 + np.exp(-(0.5 * x - 1)))).astype(float)
    a, b = fit_platt(x, y)
    assert abs(a - 0.5) < 0.05 and abs(b + 1) < 0.1


def rec(**kw):
    base = {"id": "x", "dataset": "d", "k": 4, "gold": [0, 2]}
    base.update(kw)
    return base


def test_predictors_on_one_record():
    r = rec(noul=[0.9, 0.6, 0.8, 0.1], pick=[0.5, 0.1, 0.35, 0.05], count=[0.0, 0.1, 0.8, 0.1, 0.0])
    assert Independent("noul").predict(r).subset == {0, 1, 2}
    assert ChoiceOracleCount().predict(r).subset == {0, 2}
    assert ScoresPlusCount("pick").predict(r).subset == {0, 2}
    assert ScoresPlusCount("noul").predict(r).subset == {0, 2}
    assert OracleCount("noul").predict(r).subset == {0, 2}
    assert AlwaysNone().predict(r).subset == set()
    prior = ScoresPlusDevPrior("pick").fit([rec(), rec(gold=[1, 3]), rec(gold=[0])])   # sizes 2, 2, 1 -> 2 most likely
    assert prior.predict(r).subset == {0, 2}


def test_score_records_end_to_end():
    rng = np.random.default_rng(1)
    recs = []
    for i in range(200):
        k = 5
        gold = sorted(rng.choice(k, size=rng.integers(1, 4), replace=False).tolist())
        noisy = np.clip(np.isin(np.arange(k), gold) * 0.6 + rng.uniform(0, 0.4, k), 0.01, 0.99)
        pick = noisy / noisy.sum()
        count = np.full(k + 1, 0.05); count[len(gold)] += 0.7; count /= count.sum()
        recs.append({"id": f"d:{i}", "dataset": "d", "model": "fake", "k": k, "gold": gold,
                     "noul": noisy.tolist(), "noul_ctx": noisy.tolist(), "pick": pick.tolist(), "count": count.tolist()})
    recs.append({"id": "d:err", "dataset": "d", "model": "fake", "k": 5, "gold": [1], "error": "boom"})
    report = score_records(recs)
    rows = report["d"]["predictors"]
    assert rows["pick+true_count"]["exact"] >= rows["pick@top1"]["exact"]
    assert "set_nll" in rows["noul@0.5"] and "set_nll" not in rows["pick+true_count"]
    text = format_report(report, "fake")
    assert "G1 ranking+true count vs best yes/no" in text
    assert report["d"]["n_failed"] == 1 and "1 items failed" in text


def test_score_files_keeps_dotted_model_names(tmp_path):
    rec = {"id": "d:0", "dataset": "d", "model": "kev-0.8b", "k": 2, "gold": [0], "noul": [0.9, 0.1], "pick": [0.8, 0.2], "count": [0.1, 0.8, 0.1]}
    src = tmp_path / "r.jsonl"
    src.write_text(json.dumps(rec) + "\n")
    score_files([str(src)], out=str(tmp_path / "kev-0.8b"))
    assert (tmp_path / "kev-0.8b.md").exists() and (tmp_path / "kev-0.8b.json").exists()
