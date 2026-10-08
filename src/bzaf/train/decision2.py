"""Decision 2.0 adapter: load a vllm-sr Decision 2.0 package as a trainable PyTorch model, render questions exactly as
the released runtime does, and add the count head.

Reference: vllm-project/semantic-router, src/model-runtime (Apache-2.0) at the commit pinned in cloud/vllmsr_serve.py:
`text/segments.py` (prompt), `heads/candidate.py` (head), `families/decision2/answers.py` (answers). Re-implemented
here, not imported, so training does not depend on the runtime; `tests/test_decision2_parity.py` checks that this
module and the runtime give the same answers on the runtime's own random-weight test package.

One question is one row: context, question, one `<option>` segment per option, a fixed suffix. The hidden state at
the last token of each option segment (its endpoint) and at the last token of the row (the query) feed the candidate
head; the count head reads the query state. Nothing is truncated: a row longer than the package limit is rejected.
"""
from __future__ import annotations

import contextlib
import copy
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from torch import nn

PROMPT_VERSION = "decision2-segmented-options-global-query-v1"
SUFFIX = "\n\nSelect the single option best supported by the context and instructions.\nDecision:"
# Our multi-answer question: the same layout with its own type name and suffix (the base model has never seen it;
# training teaches it). Vela 2.0 words its set questions the same way.
MULTI_SUFFIX = "\n\nSelect every option supported by the context and instructions.\nDecision:"
NOUL_OPTIONS = (("false", "No"), ("true", "Yes"))
MAX_COUNT = 32  # count head classes 0..MAX_COUNT; larger gold sets are clipped (none in benchmark v0 or the training mix)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _payload(value: Any) -> str:
    return value if isinstance(value, str) else canonical(value)


# --- package ----------------------------------------------------------------------------------------------------

@dataclass
class Package:
    root: Path
    manifest: dict
    decision_config: dict
    max_input_tokens: int
    temperatures: dict[str, float]
    score_bias: dict[int, list[float]] | None

    @classmethod
    def open(cls, name_or_path: str, revision: str | None = None, cache_dir: str | None = None) -> "Package":
        root = Path(name_or_path)
        if not root.is_dir():
            from huggingface_hub import snapshot_download

            root = Path(snapshot_download(name_or_path, revision=revision, cache_dir=cache_dir))
        pointer = json.loads((root / "config.json").read_text())
        if pointer.get("decision_format") != "vllm-sr-decision" or pointer.get("format_version") != 2:
            raise ValueError(f"{root} is not a Decision 2.0 package")
        manifest = json.loads((root / pointer.get("manifest", "MODEL_MANIFEST.json")).read_text())
        if manifest.get("profile") != "qwen-full":
            raise NotImplementedError(f"package profile {manifest.get('profile')!r}: only qwen-full is supported so far")
        dc = json.loads((root / "decision_config.json").read_text())
        if dc.get("prompt_version") != PROMPT_VERSION or dc.get("head_variant", "shared") != "shared":
            raise ValueError(f"unsupported Decision 2.0 checkpoint: {dc.get('prompt_version')}, {dc.get('head_variant')}")
        temps = {"choice": 1.0, "noul": 1.0, "score": 1.0}
        if manifest.get("calibration"):
            report = json.loads((root / manifest["calibration"]["file"]).read_text())
            temps = {k: float(v) for k, v in report["temperature_by_type"].items()}
        bias = None
        if manifest.get("score_bias"):
            report = json.loads((root / manifest["score_bias"]["file"]).read_text())
            bias = {int(k): [float(x) for x in v] for k, v in report["offsets"].items()}
        return cls(root, manifest, dc, int(manifest["max_input_tokens"]), temps, bias)

    def tokenizer(self) -> "Tokenizer":
        return Tokenizer.from_package(self.root)


class Tokenizer:
    """The package tokenizer through the `tokenizers` library, no special tokens (as the runtime)."""

    def __init__(self, backend, pad_id: int):
        self.backend, self.pad_id = backend, pad_id

    @classmethod
    def from_package(cls, root: Path) -> "Tokenizer":
        from tokenizers import Tokenizer as Backend

        backend = Backend.from_file(str(root / "tokenizer.json"))
        config = json.loads((root / "tokenizer_config.json").read_text()) if (root / "tokenizer_config.json").is_file() else {}
        for name in ("pad_token", "eos_token"):
            token = config.get(name)
            token = token.get("content") if isinstance(token, dict) else token
            if isinstance(token, str) and backend.token_to_id(token) is not None:
                return cls(backend, backend.token_to_id(token))
        raise ValueError("the tokenizer needs a pad or EOS token")

    def encode(self, text: str) -> list[int]:
        return list(self.backend.encode(text, add_special_tokens=False).ids)


# --- rendering ----------------------------------------------------------------------------------------------------

@dataclass
class Row:
    """One rendered question."""
    ids: list[int]
    endpoints: list[int]
    query: int
    kind: str
    keys: list[str]
    meta: dict = field(default_factory=dict)


def options_for(kind: str, criteria: Any) -> list[tuple[str, Any]]:
    """(key, description) per option, as the runtime builds them: Choice {name: description}, Noul false/true,
    Score levels keyed by index, multi {name: description}."""
    if kind == "noul":
        given = criteria or {}
        return [(k, given.get(k) if given.get(k) is not None else d) for k, d in NOUL_OPTIONS]
    if kind == "score":
        return [(str(i), level) for i, level in enumerate(criteria)]
    return list(criteria.items())


def render(tok: Tokenizer, state: Any, kind: str, instructions: Any, options: list[tuple[str, Any]],
           max_length: int) -> Row:
    prefix = f"Context:\n{_payload(state)}\n\nTask type: {kind}\nQuestion:\n{_payload(instructions)}\nOptions:"
    ids = tok.encode(prefix)
    endpoints = []
    for key, description in options:
        part = tok.encode("\n<option>\n" + canonical({"key": key, "description": description}) + "\n</option>")
        if not part:
            raise ValueError(f"empty tokenized option {key!r}")
        ids.extend(part)
        endpoints.append(len(ids) - 1)
    ids.extend(tok.encode(MULTI_SUFFIX if kind == "multi" else SUFFIX))
    if len(ids) > max_length:
        raise ValueError(f"{len(ids)} tokens exceeds max_length={max_length}")
    return Row(ids, endpoints, len(ids) - 1, kind, [k for k, _ in options])


def render_question(tok: Tokenizer, state: Any, question: dict, max_length: int) -> Row:
    """A System One question dict ({type, instructions, criteria}), plus our "multi" type."""
    kind = question["type"]
    return render(tok, state, kind, question["instructions"], options_for(kind, question.get("criteria")), max_length)


def collate(rows: list[Row], pad_id: int, multiple: int = 8) -> dict[str, torch.Tensor]:
    length = math.ceil(max(len(r.ids) for r in rows) / multiple) * multiple
    width = max(len(r.keys) for r in rows)
    ids = torch.full((len(rows), length), pad_id, dtype=torch.long)
    mask = torch.zeros_like(ids)
    endpoints = torch.zeros((len(rows), width), dtype=torch.long)
    cand = torch.zeros((len(rows), width), dtype=torch.bool)
    for i, r in enumerate(rows):
        ids[i, : len(r.ids)] = torch.tensor(r.ids)
        mask[i, : len(r.ids)] = 1
        endpoints[i, : len(r.keys)] = torch.tensor(r.endpoints)
        cand[i, : len(r.keys)] = True
    return {"input_ids": ids, "attention_mask": mask, "endpoints": endpoints, "candidate_mask": cand,
            "query": torch.tensor([r.query for r in rows], dtype=torch.long)}


# --- heads and model ------------------------------------------------------------------------------------------------

class CandidateHead(nn.Module):
    """logit = <K c, Q q> / sqrt(d) + w · GELU(Mc c + Mq q), LayerNorm-ed inputs, FP32 (same parameter names as the
    runtime, so decision_head.safetensors loads as is)."""

    def __init__(self, hidden_size: int, head_dim: int = 256):
        super().__init__()
        self.head_dim = head_dim
        self.candidate_norm = nn.LayerNorm(hidden_size)
        self.query_norm = nn.LayerNorm(hidden_size)
        self.key = nn.Linear(hidden_size, head_dim, bias=False)
        self.query = nn.Linear(hidden_size, head_dim, bias=False)
        self.candidate_mlp = nn.Linear(hidden_size, head_dim)
        self.query_mlp = nn.Linear(hidden_size, head_dim, bias=False)
        self.scalar = nn.Linear(head_dim, 1, bias=False)

    def forward(self, candidates: torch.Tensor, query: torch.Tensor) -> torch.Tensor:
        with torch.autocast(device_type=candidates.device.type, enabled=False):
            c = self.candidate_norm(candidates.float())
            q = self.query_norm(query.float())
            bilinear = (self.key(c) * self.query(q)[:, None, :]).sum(-1) / math.sqrt(self.head_dim)
            nonlinear = self.scalar(F.gelu(self.candidate_mlp(c) + self.query_mlp(q)[:, None, :])).squeeze(-1)
            return bilinear + nonlinear


class CountHead(nn.Module):
    """P(number of correct options = s), s = 0..MAX_COUNT, from the query state; counts above the row's number of
    options are masked. The last layer starts at zero (a uniform count), so it cannot disturb the base at step 0."""

    def __init__(self, hidden_size: int, width: int = 256, max_count: int = MAX_COUNT):
        super().__init__()
        self.max_count = max_count
        self.norm = nn.LayerNorm(hidden_size)
        self.mlp = nn.Sequential(nn.Linear(hidden_size, width), nn.GELU(), nn.Linear(width, max_count + 1))
        nn.init.zeros_(self.mlp[-1].weight)
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, query: torch.Tensor, n_options: torch.Tensor) -> torch.Tensor:
        with torch.autocast(device_type=query.device.type, enabled=False):
            logits = self.mlp(self.norm(query.float()))
        allowed = torch.arange(self.max_count + 1, device=query.device)[None, :] <= n_options[:, None]
        return logits.masked_fill(~allowed, -float("inf"))


class Decision2Model(nn.Module):
    def __init__(self, backbone: nn.Module, head: CandidateHead, count_head: CountHead):
        super().__init__()
        self.backbone, self.head, self.count_head = backbone, head, count_head

    @classmethod
    def from_package(cls, pkg: Package, dtype: torch.dtype = torch.float32, device: str = "cpu",
                     attn_implementation: str | None = None) -> "Decision2Model":
        from safetensors.torch import load_file
        from transformers import AutoModel

        kw = {"attn_implementation": attn_implementation} if attn_implementation else {}
        backbone = AutoModel.from_pretrained(pkg.root / "backbone", dtype=dtype, **kw)
        hidden = backbone.config.hidden_size
        head = CandidateHead(hidden, pkg.decision_config["head_dim"])
        head.load_state_dict({k: v.float() for k, v in load_file(str(pkg.root / "decision_head.safetensors")).items()}, strict=True)
        model = cls(backbone, head.float(), CountHead(hidden))
        return model.to(device)

    def hidden(self, batch: dict[str, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
        out = self.backbone(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], use_cache=False)
        h = out.last_hidden_state
        rows = torch.arange(h.shape[0], device=h.device)
        return h[rows[:, None], batch["endpoints"]], h[rows, batch["query"]]

    def keep_base(self) -> None:
        """Keep a frozen copy of the released candidate head, for base answers (distillation targets, baselines)."""
        self.base_head = copy.deepcopy(self.head).requires_grad_(False)

    def base_forward(self, batch: dict[str, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
        """The released model's answers: LoRA adapters off, the original candidate head."""
        off = self.backbone.disable_adapter() if hasattr(self.backbone, "disable_adapter") else contextlib.nullcontext()
        with off:
            gathered, query = self.hidden(batch)
        head = getattr(self, "base_head", self.head)
        scores = head(gathered, query).masked_fill(~batch["candidate_mask"], -float("inf"))
        return scores, self.count_head(query, batch["candidate_mask"].sum(-1))

    def forward(self, batch: dict[str, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
        """Option logits [B, W] (-inf on padded slots) and count logits [B, MAX_COUNT + 1]."""
        gathered, query = self.hidden(batch)
        scores = self.head(gathered, query).masked_fill(~batch["candidate_mask"], -float("inf"))
        counts = self.count_head(query, batch["candidate_mask"].sum(-1))
        return scores, counts


# --- answers (as the runtime) -------------------------------------------------------------------------------------

def answer(pkg: Package, row: Row, logits: list[float]) -> dict:
    """System One answer from one row's option logits: score offsets, then the package's per-type temperature."""
    kind = row.kind
    values = list(logits)
    if kind == "score" and pkg.score_bias and len(values) in pkg.score_bias:
        values = [v + b for v, b in zip(values, pkg.score_bias[len(values)])]
    t = pkg.temperatures.get(kind, 1.0)
    z = torch.tensor(values, dtype=torch.float64) / t
    p = torch.softmax(z, 0).tolist()
    probs = dict(zip(row.keys, p))
    if kind == "noul":
        return {"type": "noul", "noul": probs["true"]}
    if kind == "score":
        return {"type": "score", "score": sum(int(k) * v for k, v in probs.items()), "probabilities": probs}
    return {"type": "choice", "choice": row.keys[int(max(range(len(p)), key=p.__getitem__))], "probabilities": probs}


def compare_to_reference(pkg: Package, state: Any, questions: dict, expected: dict, device: str = "cpu",
                         autocast: bool = False) -> dict:
    """Our adapter's answers to `questions` about `state` against reference answers keyed by question id."""
    tok = pkg.tokenizer()
    model = Decision2Model.from_package(pkg, device=device).eval()
    qids = list(questions)
    rows = [render_question(tok, state, questions[q], pkg.max_input_tokens) for q in qids]
    batch = {k: v.to(device) for k, v in collate(rows, tok.pad_id).items()}
    with torch.no_grad(), torch.autocast(device_type=torch.device(device).type, dtype=torch.bfloat16, enabled=autocast):
        scores, _ = model(batch)
    worst, report = 0.0, {}
    for qid, row, z in zip(qids, rows, scores):  # matched by question id: reference files may be in another order
        ours = answer(pkg, row, z[: len(row.keys)].float().tolist())
        exp_p = expected[qid].get("probabilities") or {"true": expected[qid]["noul"]}
        our_p = ours.get("probabilities") or {"true": ours["noul"]}
        diff = max(abs(exp_p[k] - our_p[k]) for k in exp_p)
        report[qid] = {"expected": exp_p, "ours": our_p, "max_abs_diff": diff}
        worst = max(worst, diff)
    return {"device": device, "autocast": autocast, "max_abs_diff": worst, "questions": report}


def golden_check(repo_id: str, device: str = "cpu", autocast: bool = False, cache_dir: str | None = None) -> dict:
    """Our adapter on the runtime's readiness request against its recorded FP32 answers for this model (the
    `decision2_golden.py` copy of the runtime registry). Returns the largest probability difference; expect ~1e-5
    in FP32 and ~1e-2 under bf16 autocast."""
    from .decision2_golden import GOLDEN as golden

    ref = golden["models"][repo_id]
    pkg = Package.open(repo_id, revision=ref["revision"], cache_dir=cache_dir)
    result = compare_to_reference(pkg, golden["state"], golden["questions"], ref["cpu"], device, autocast)
    return {"model": repo_id, "revision": ref["revision"], **result}
