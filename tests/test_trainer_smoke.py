"""End to end on the runtime's tiny random Decision 2.0 package: mixture rows -> a few training steps -> in-process
benchmark evaluation -> scoring with our set predictor. Skipped without torch, transformers, peft and vllm-srun."""
import json
import random

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("peft")
pytest.importorskip("vllm_srun")


def test_train_then_evaluate_offline(tmp_path):
    from vllm_srun.testing.fixtures import write_package

    from bzaf import bench
    from bzaf.data import load_synthetic
    from bzaf.schema import Item, write_items
    from bzaf.train.data import TrainRow, multi_question, native_question, shuffled
    from bzaf.train.trainer import TrainConfig, train

    pkg = write_package(tmp_path / "pkg", backbone="qwen3_5", seed=1)
    bench_dir = tmp_path / "bench"
    write_items(load_synthetic(n=12, seed=0), bench_dir / "synthetic.jsonl")
    general = [Item(f"g{i}", "boolq", f"passage {i}", "Is it true?", ["no", "yes"], [i % 2], {"qtype": "noul"}) for i in range(8)]
    write_items(general, bench_dir / "boolq.jsonl")

    rng = random.Random(0)
    rows = [TrainRow(it.id, "synthetic", "set", it.state, multi_question(it), it.gold)
            for it in (shuffled(x, rng) for x in load_synthetic(n=16, seed=5))]
    rows += [TrainRow(it.id, "boolq", "distill", it.state, native_question(it), it.gold) for it in general]
    cfg = TrainConfig(base=str(pkg), out=str(tmp_path / "run"), bench=str(bench_dir), max_steps=6, warmup_steps=2,
                      max_tokens=4096, eval_base=True, log_every=2, lr_count=1e-2)
    res = train(cfg, device="cpu", rows=rows, log=lambda *_: None)
    assert res["steps"] == 6
    log = [json.loads(line) for line in (tmp_path / "run" / "train_log.jsonl").read_text().splitlines()]
    assert all("tokens_per_s" in r for r in log)
    assert (tmp_path / "run" / "adapter" / "adapter_config.json").exists() and (tmp_path / "run" / "heads.pt").exists()

    ours = bench.score(tmp_path / "run" / "eval" / "ours")
    base = bench.score(tmp_path / "run" / "eval" / "base")
    assert "ours@mode" in ours["main"]["synthetic"]["predictors"]
    assert "native@top1" in ours["main"]["boolq"]["predictors"]
    assert "pick+dev_prior" in base["main"]["synthetic"]["predictors"]     # the base was asked its own question types


def test_e02_mixture_offline(tmp_path):
    """The mixture builder with small offline sources: set rows are shuffled multi questions with valid gold sets,
    merged rows combine several texts, distill rows keep their native type, and benchmark states are dropped."""
    from bzaf.data import load_synthetic
    from bzaf.schema import Item, write_items
    from bzaf.train.data import build_e02

    emo = [Item(f"e{i}", "goemotions", f"comment {i}", "Which emotions?", ["joy", "anger", "fear", "neutral"], [i % 4]) for i in range(40)]
    db = [Item(f"d{i}", "dbpedia", f"entry {i}", "Which category?", ["film", "album", "plant", "village"], [i % 4], {"qtype": "choice"})
          for i in range(40)]
    yn = [Item(f"b{i}", "boolq", f"passage {i}", "Is it?", ["no", "yes"], [i % 2], {"qtype": "noul"}) for i in range(10)]
    bench = tmp_path / "bench"
    write_items([emo[0]], bench / "goemotions.jsonl")                       # this state must not be trained on
    loaders = {"goemotions": lambda: emo, "dbpedia": lambda: db, "boolq": lambda: yn, "hellaswag": lambda: [],
               "sst5": lambda: [], "synthetic": lambda: load_synthetic(n=10, seed=3), "wide": lambda: []}
    sizes = {"goemotions": 40, "goemotions_merged": 10, "dbpedia_merged": 10, "synthetic": 10, "wide": 0,
             "boolq_distill": 10, "hellaswag_distill": 0, "sst5_distill": 0, "dbpedia_distill": 5}
    rows = build_e02(0, sizes, bench, loaders=loaders, log=lambda *_: None)
    assert not any(r.state == "comment 0" for r in rows)
    sets = [r for r in rows if r.loss == "set"]
    assert all(r.question["type"] == "multi" and all(0 <= g < len(r.question["criteria"]) for g in r.gold) for r in sets)
    merged = [r for r in sets if r.source == "goemotions_merged"]
    assert merged and all("Comment 2:" in r.state for r in merged)
    assert {r.question["type"] for r in rows if r.loss == "distill"} == {"noul", "choice"}


def test_option_subset_keeps_gold_consistent():
    import random

    from bzaf.schema import Item
    from bzaf.train.data import option_subset

    it = Item("x", "d", "s", "q", [f"o{i}" for i in range(28)], [3, 7], {"descriptions": [f"d{i}" for i in range(28)]})
    rng = random.Random(0)
    sizes, empty = [], 0
    for _ in range(300):
        sub = option_subset(it, rng, (4, 20), 0.5)
        assert 2 <= len(sub.options) <= 20 and set(sub.options) <= set(it.options)
        assert {sub.options[g] for g in sub.gold} == {"o3", "o7"} & set(sub.options)
        assert all(sub.meta["descriptions"][j] == "d" + sub.options[j][1:] for j in range(len(sub.options)))
        sizes.append(len(sub.options)); empty += not sub.gold
    assert 0.15 < empty / 300 < 0.4 and len(set(sizes)) > 5


def test_interrupted_run_resumes_to_the_same_weights(tmp_path):
    """Training stopped right after the step-3 checkpoint and resumed ends with the same weights as an uninterrupted
    run (same data order, restored optimizer); a resume after training finished skips straight to evaluation."""
    import random

    from vllm_srun.testing.fixtures import write_package

    from bzaf.data import load_synthetic
    from bzaf.train.data import TrainRow, multi_question, shuffled
    from bzaf.train.trainer import TrainConfig, train

    pkg = write_package(tmp_path / "pkg", backbone="qwen3_5", seed=1)
    rng = random.Random(0)
    rows = [TrainRow(it.id, "synthetic", "set", it.state, multi_question(it), it.gold)
            for it in (shuffled(x, rng) for x in load_synthetic(n=24, seed=5))]

    def cfg(out, **kw):
        return TrainConfig(base=str(pkg), out=str(tmp_path / out), bench=str(tmp_path / "nobench"), max_steps=6,
                           warmup_steps=2, max_tokens=2048, log_every=1, save_every=3, lr_count=1e-2, **kw)

    def weights(out):
        return torch.load(tmp_path / out / "checkpoint.pt")["trainable"]

    train(cfg("full"), device="cpu", rows=rows, log=lambda *_: None)

    class Stop(Exception):
        pass

    def stop():
        raise Stop

    with pytest.raises(Stop):
        train(cfg("cut"), device="cpu", rows=rows, log=lambda *_: None, on_checkpoint=stop)
    assert torch.load(tmp_path / "cut" / "checkpoint.pt")["step"] == 3
    res = train(cfg("cut", resume=True), device="cpu", rows=rows, log=lambda *_: None)
    assert res["resumed_from"] == 3 and res["steps"] == 6
    a, b = weights("full"), weights("cut")
    assert all(torch.allclose(a[n], b[n], atol=1e-6) for n in a)
    again = train(cfg("cut", resume=True), device="cpu", rows=rows, log=lambda *_: None)
    assert again["resumed_from"] == 6
