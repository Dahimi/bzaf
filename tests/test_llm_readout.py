"""The LLM letter readout (bzaf.llm) on a tiny random Qwen3.5 (linear-attention and attention layers) with a byte-level
stand-in tokenizer: shared-prefix and batched passes must give the same answers as one full pass per question."""
import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from bzaf.llm import LETTERS, SYSTEM_WIDE, WRITE, LLMClient, max_answer_diff, messages, parse_written  # noqa: E402
from bzaf.readout import build_questions, parse_answers  # noqa: E402
from bzaf.schema import Item  # noqa: E402


class ByteTokenizer:
    """One token per UTF-8 byte; a plain chat template ending where the answer letter goes."""
    pad_token_id = eos_token_id = None

    def encode(self, text, add_special_tokens=False):
        return list(text.encode("utf-8"))

    def decode(self, ids, skip_special_tokens=True):
        return bytes(i for i in ids if i < 256).decode("utf-8", errors="replace")

    def apply_chat_template(self, msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False):
        assert not tokenize and add_generation_prompt and not enable_thinking
        return "".join(f"<{m['role']}>{m['content']}</{m['role']}>" for m in msgs) + "<assistant>"


def tiny_lm():
    torch.manual_seed(0)
    cfg = transformers.Qwen3_5TextConfig(
        vocab_size=260, hidden_size=64, intermediate_size=128, num_hidden_layers=4, num_attention_heads=4,
        num_key_value_heads=2, head_dim=16, linear_key_head_dim=16, linear_value_head_dim=16, linear_num_key_heads=2,
        linear_num_value_heads=4, layer_types=["linear_attention", "linear_attention", "linear_attention", "full_attention"])
    return transformers.Qwen3_5ForCausalLM(cfg).eval()


LM = None


def client(**kw):
    global LM
    if LM is None:
        LM = tiny_lm()
    return LLMClient(LM, ByteTokenizer(), "tiny", **kw)


def item(k=5):
    opts = [f"option number {j}" for j in range(k)]
    return Item("t:0", "t", "A short story about a cat who visits the market and buys fish.", "Which of these apply?",
                opts, [1, 3], {})


def test_shared_prefix_and_batching_match_full_passes():
    it = item()
    qs = build_questions(it, ["noul_ctx", "pick", "count"])
    full = client(share=False, max_rows=1).decide(it.state, qs)["answers"]
    shared = client(share=True).decide(it.state, qs)["answers"]
    small = client(share=True, max_rows=2, max_tokens=900).decide(it.state, qs)["answers"]
    assert max_answer_diff(full, shared) < 1e-5
    assert max_answer_diff(full, small) < 1e-5


def test_answers_parse_like_a_server():
    it = item()
    c = client()
    rec = parse_answers(it, c.decide(it.state, build_questions(it, ["noul_ctx", "pick", "count"]))["answers"])
    assert len(rec["noul_ctx"]) == 5 and len(rec["pick"]) == 5 and len(rec["count"]) == 6
    assert abs(sum(rec["pick"]) - 1) < 1e-5 and abs(sum(rec["count"]) - 1) < 1e-5
    assert all(0 <= p <= 1 for p in rec["noul_ctx"])
    assert set(c.mass_summary()) == {"noulctx", "pick", "count"}


def test_wide_questions_use_lowercase_letters():
    q = build_questions(item(30), ["pick"])["pick"]
    msgs = messages("state", q)
    assert msgs[0]["content"] == SYSTEM_WIDE and '"letter": "d"' in msgs[1]["content"]
    with pytest.raises(ValueError):
        messages("state", build_questions(item(len(LETTERS) + 1), ["pick"])["pick"])


def test_written_answers_parse():
    assert parse_written(" B, D\n", 5) == [1, 3] and parse_written("a,c.", 5) == [0, 2] and parse_written("NONE", 5) == []
    assert parse_written("None.", 5) == [] and parse_written("D, B, D", 5) == [1, 3]
    assert parse_written("F", 5) is None and parse_written("B and D", 5) is None and parse_written("", 5) is None
    assert parse_written("A, a", 30) == [0, 26] and parse_written("d", 30) == [29] and parse_written("e", 30) is None


def test_write_question_runs_and_parses_into_the_record():
    it = item()
    qs = build_questions(it, ["pick", "write"])
    assert messages(it.state, qs["write"])[0]["content"] == WRITE
    c = client()
    answers = c.decide(it.state, qs)["answers"]
    rec = parse_answers(it, answers)
    assert isinstance(rec["write_raw"], str) and len(rec["pick"]) == 5
    assert ("write" in rec) == (answers["write"]["indices"] is not None)   # a random model writes junk: usually missing
    assert c.mass_summary()["write"]["n"] == 1
