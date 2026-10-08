"""Our Decision 2.0 adapter against the released runtime (vllm-srun), on the runtime's own random-weight test package.
Skipped unless torch, transformers and vllm-srun are installed (`uv pip install <semantic-router>/src/model-runtime`)."""
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("vllm_srun")

STATE = {"ticket": "I was charged twice and the app crashes on the billing page.", "plan": "pro"}
QUESTIONS = {
    "team": {"type": "choice", "instructions": "Which team handles this?",
             "criteria": {"billing": "payments and refunds", "technical": "bugs", "sales": None, "other": "anything else"}},
    "refund": {"type": "noul", "instructions": "Does the customer ask for a refund?"},
    "urgency": {"type": "score", "instructions": "How urgent is this?", "criteria": ["low", "medium", "high"]},
    "many": {"type": "choice", "instructions": "Which tag fits best?", "criteria": {f"tag {i}": None for i in range(12)}},
}


@pytest.fixture(scope="module")
def package(tmp_path_factory):
    from vllm_srun.testing.fixtures import write_package

    return write_package(tmp_path_factory.mktemp("d2") / "pkg", backbone="qwen3_5", seed=1)


def test_adapter_reproduces_runtime_answers(package):
    from vllm_srun.config import ModelConfig, ServeConfig
    from vllm_srun.runtime import Runtime

    from bzaf.train.decision2 import Decision2Model, Package, answer, collate, render_question

    runtime = Runtime(ServeConfig(models=(ModelConfig(model=str(package), device="cpu"),)))
    runtime.start(background=False)
    try:
        import asyncio

        status, body = asyncio.run(runtime.call("decisions", {"state": STATE, "questions": QUESTIONS}))
        assert status == 200, body
        reference = body["answers"]
    finally:
        runtime.stop()

    pkg = Package.open(str(package))
    tok = pkg.tokenizer()
    model = Decision2Model.from_package(pkg).eval()
    rows = [render_question(tok, STATE, q, pkg.max_input_tokens) for q in QUESTIONS.values()]
    with torch.no_grad():
        scores, counts = model(collate(rows, tok.pad_id))
    for (qid, ref), row, z in zip(reference.items(), rows, scores):
        ours = answer(pkg, row, z[: len(row.keys)].tolist())
        if ref["type"] == "noul":
            assert ours["noul"] == pytest.approx(ref["noul"], abs=1e-5), qid
        else:
            for key, p in ref["probabilities"].items():
                assert ours["probabilities"][key] == pytest.approx(p, abs=1e-5), (qid, key)
    # the new count head starts uniform over the counts each row allows
    p = torch.softmax(counts[0], -1)
    assert torch.allclose(p[:5], torch.full((5,), 0.2)) and p[5:].sum() == 0
