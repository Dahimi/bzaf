"""Letter readout from an instruction-tuned LLM (E04a): answer our Choice / Noul / Score questions with no training.

Each question becomes one chat prompt, as in SemIf and Geuter et al. 2026 ("Releasing the Inner Jev", Appendix A): a
fixed system message, a JSON user message {"evidence", "criterion", "options": [{"letter", "description"}]}, and the
model's own chat template with thinking off, so the next token is the answer letter. The probability of each listed
option is the softmax of the next-token logits over the option letters (A-Z, then a-z above 26 options; at most 52).
No temperature: these readouts are scored as they come out of the model.

The client answers like a decision server (`DecisionClient.decide`), so `bzaf readout`, `bzaf bench` and all the
predictors run unchanged. One extra question type, `write`, is not a readout: the model writes the letters of every
option that applies (greedy, thinking off), a reference for what the model knows when it may answer in a few tokens.

Speed: questions about one item share most of their prompt (the per-option yes/no questions all repeat the evidence and
the option listing), so each group of questions runs as one pass over the shared prefix plus short continuations from
copies of its cache, right-padded. Both are exact for causal models, attention and linear-attention layers alike;
`tests/test_llm_readout.py` checks them against one full pass per question on a tiny random Qwen3.5.
"""
from __future__ import annotations

import copy
import json
import re
import string
from collections import defaultdict
from typing import Any

import torch

LETTERS = string.ascii_uppercase + string.ascii_lowercase
SYSTEM = ("Apply the supplied criterion to the supplied evidence. Choose exactly one listed option. "
          "Respond with only its uppercase letter, with no explanation or reasoning.")
SYSTEM_WIDE = ("Apply the supplied criterion to the supplied evidence. Choose exactly one listed option. "
               "Respond with only its letter, exactly as listed (upper or lower case), with no explanation or reasoning.")
WRITE = ("Apply the supplied criterion to the supplied evidence. Choose every listed option that applies; there may be "
         "none, one or several. Respond with only their uppercase letters separated by commas, or NONE if no option "
         "applies, with no explanation or reasoning.")
WRITE_WIDE = ("Apply the supplied criterion to the supplied evidence. Choose every listed option that applies; there may "
              "be none, one or several. Respond with only their letters exactly as listed (upper or lower case), "
              "separated by commas, or NONE if no option applies, with no explanation or reasoning.")
MIN_SHARED = 16   # tokens: a shorter common prefix is not worth a separate pass


def options_of(q: dict) -> tuple[list[str], list[str]]:
    """(answer keys, option texts) of one question in the decision-server format."""
    crit = q.get("criteria")
    if q["type"] == "noul":
        crit = crit or {}
        keys = ["true", "false"]
        return keys, [f"{k}: {crit[k]}" if crit.get(k) else k for k in keys]
    if q["type"] == "score":
        return [str(j) for j in range(len(crit))], [f"{j}: {t}" for j, t in enumerate(crit)]
    if q["type"] in ("choice", "write"):
        return list(crit), [f"{k}: {d}" if d else k for k, d in crit.items()]
    raise ValueError(f"question type {q['type']!r} is not answered by the letter readout")


def messages(state: Any, q: dict) -> list[dict]:
    _, texts = options_of(q)
    if len(texts) > len(LETTERS):
        raise ValueError(f"{len(texts)} options; the letter readout supports at most {len(LETTERS)}")
    user = {"evidence": state, "criterion": q["instructions"],
            "options": [{"letter": L, "description": t} for L, t in zip(LETTERS, texts)]}
    narrow, wide = (WRITE, WRITE_WIDE) if q["type"] == "write" else (SYSTEM, SYSTEM_WIDE)
    return [{"role": "system", "content": narrow if len(texts) <= 26 else wide},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]


def parse_written(text: str, k: int) -> list[int] | None:
    """Option indices from a written answer ("B, D", "NONE"); None if it is anything else."""
    t = text.strip().rstrip(".").strip()
    if t.upper() == "NONE":
        return []
    out: set[int] = set()
    for part in re.split(r"[,\s]+", t):
        if not part:
            continue
        j = LETTERS.find(part.upper() if k <= 26 else part) if len(part) == 1 else -1
        if not 0 <= j < k:
            return None
        out.add(j)
    return sorted(out) if out else None


def max_answer_diff(a: dict, b: dict) -> float:
    """Largest difference between two `decide` answer sets on the same questions (any option's probability)."""
    out = 0.0
    for key, x in a.items():
        px = {"_": x["noul"]} if "noul" in x else x["probabilities"]
        py = {"_": b[key]["noul"]} if "noul" in b[key] else b[key]["probabilities"]
        out = max(out, max(abs(px[n] - py[n]) for n in px))
    return out


def _group(key: str) -> str:
    """Questions that share a long prompt: the per-option fan-outs (noul_3, noulctx_3); the rest go together."""
    head, _, tail = key.rpartition("_")
    return head if head and tail.isdigit() else "rest"


class LLMClient:
    """`decide(state, questions)` like a decision server, answered by a local causal LM's next-token letters."""

    def __init__(self, model, tokenizer, name: str, max_tokens: int = 32768, max_rows: int = 32, share: bool = True):
        self.lm, self.tok, self.model = model, tokenizer, name   # `model` is the name recorded in readouts
        self.max_tokens, self.max_rows, self.share = max_tokens, max_rows, share
        self.device = next(model.parameters()).device
        ids = [tokenizer.encode(L, add_special_tokens=False) for L in LETTERS]
        if any(len(i) != 1 for i in ids):
            raise ValueError("every option letter must be one token for this readout")
        self.letter_ids = torch.tensor([i[0] for i in ids], device=self.device)
        self.mass: dict[str, list[float]] = defaultdict(list)   # probability on the listed letters, per question group
        self.written: list[bool] = []                            # whether each written answer parsed
        self.pad_id = getattr(tokenizer, "pad_token_id", None) or getattr(tokenizer, "eos_token_id", None) or 0

    @classmethod
    def load(cls, model_id: str, name: str | None = None, revision: str | None = None, device: str = "cuda",
             dtype: str = "bfloat16", **kw) -> "LLMClient":
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
        lm, info = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, dtype=getattr(torch, dtype),
                                                        device_map=device, output_loading_info=True)
        if info["missing_keys"]:  # a silently random layer would read as a bad model, not as a bug
            raise ValueError(f"{len(info['missing_keys'])} weights not in the checkpoint, e.g. {sorted(info['missing_keys'])[:5]}")
        return cls(lm.eval(), tok, name or model_id.split("/")[-1].lower(), **kw)

    def prompt_text(self, state: Any, q: dict) -> str:
        return self.tok.apply_chat_template(messages(state, q), add_generation_prompt=True, tokenize=False,
                                            enable_thinking=False)

    def prompt_ids(self, state: Any, q: dict) -> list[int]:
        return self.tok.encode(self.prompt_text(state, q), add_special_tokens=False)

    def decide(self, state: Any, questions: dict[str, dict]) -> dict:
        seqs = {key: self.prompt_ids(state, q) for key, q in questions.items()}
        answers = {}
        for key, q in questions.items():
            if q["type"] == "write":
                k = len(q["criteria"])
                text = self._generate(seqs[key], max_new_tokens=min(2 * k + 8, 128))
                answers[key] = {"text": text, "indices": parse_written(text, k)}
                self.written.append(answers[key]["indices"] is not None)
        groups: dict[str, list[str]] = defaultdict(list)
        for key, q in questions.items():
            if q["type"] != "write":
                groups[_group(key)].append(key)
        logits: dict[str, torch.Tensor] = {}
        for keys in groups.values():
            for key, row in zip(keys, self._last_logits([seqs[k] for k in keys])):
                logits[key] = row
        for key, q in questions.items():
            if q["type"] == "write":
                continue
            names, _ = options_of(q)
            row = logits[key].float()
            letters = row[self.letter_ids[: len(names)]]
            label = key if _group(key) == "rest" else _group(key)
            self.mass[label].append(float((torch.logsumexp(letters, 0) - torch.logsumexp(row, 0)).exp()))
            p = torch.softmax(letters, 0).tolist()
            answers[key] = {"noul": p[0]} if q["type"] == "noul" else {"probabilities": dict(zip(names, p))}
        return {"answers": answers}

    def mass_summary(self) -> dict[str, dict[str, float]]:
        """Mean and lowest probability the model put on the listed letters (the rest went to other tokens), and the
        share of written answers that parsed."""
        out = {g: {"n": len(v), "mean": sum(v) / len(v), "min": min(v)} for g, v in sorted(self.mass.items()) if v}
        if self.written:
            out["write"] = {"n": len(self.written), "parsed": sum(self.written) / len(self.written)}
        return out

    # --- forward passes -----------------------------------------------------------------------------------------

    @torch.no_grad()
    def _generate(self, ids: list[int], max_new_tokens: int) -> str:
        """Greedy continuation of one prompt, up to the model's end-of-turn token."""
        x = torch.tensor([ids], device=self.device)
        out = self.lm.generate(input_ids=x, attention_mask=torch.ones_like(x), max_new_tokens=max_new_tokens,
                               do_sample=False, temperature=None, top_p=None, top_k=None, pad_token_id=self.pad_id)
        return self.tok.decode(out[0, len(ids):].tolist(), skip_special_tokens=True)

    @torch.no_grad()
    def _last_logits(self, seqs: list[list[int]]) -> list[torch.Tensor]:
        """Next-token logits after each sequence (full vocabulary)."""
        n = 0
        if self.share and len(seqs) > 1:
            shortest = min(map(len, seqs))
            while n < shortest - 1 and all(s[n] == seqs[0][n] for s in seqs):  # every continuation keeps >= 1 token
                n += 1
        if n < MIN_SHARED:
            return self._batched(seqs, None, 0)
        out = self.lm(input_ids=torch.tensor([seqs[0][:n]], device=self.device), use_cache=True, logits_to_keep=1)
        return self._batched([s[n:] for s in seqs], out.past_key_values, n)

    def _batched(self, seqs: list[list[int]], cache, prefix: int) -> list[torch.Tensor]:
        order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
        out: list[torch.Tensor | None] = [None] * len(seqs)
        batch: list[int] = []
        for i in order + [None]:
            if batch and (i is None or len(batch) == self.max_rows or (len(batch) + 1) * len(seqs[i]) > self.max_tokens):
                for j, row in zip(batch, self._forward([seqs[j] for j in batch], cache, prefix)):
                    out[j] = row
                batch = []
            if i is not None:
                batch.append(i)
        return out

    def _forward(self, seqs: list[list[int]], cache, prefix: int) -> torch.Tensor:
        """One right-padded batch, continuing from `cache` (the shared prefix, batch size 1) if given."""
        n, width = len(seqs), max(map(len, seqs))
        ids = torch.zeros(n, width, dtype=torch.long)
        mask = torch.zeros(n, prefix + width, dtype=torch.long)
        mask[:, :prefix] = 1
        for r, s in enumerate(seqs):
            ids[r, : len(s)] = torch.tensor(s)
            mask[r, prefix : prefix + len(s)] = 1
        last = torch.tensor([len(s) - 1 for s in seqs])
        keep, pick = torch.unique(last, return_inverse=True)
        kw = {}
        if cache is not None:
            kw["past_key_values"] = copy.deepcopy(cache)
            kw["past_key_values"].reorder_cache(torch.zeros(n, dtype=torch.long, device=self.device))
        logits = self.lm(input_ids=ids.to(self.device), attention_mask=mask.to(self.device), use_cache=cache is not None,
                         logits_to_keep=keep.to(self.device), **kw).logits
        return logits[torch.arange(n, device=self.device), pick.to(self.device)]
