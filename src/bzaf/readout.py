"""Experiment E01 readouts: ask an existing decision model about each multi-answer item using only the question
types it already supports, and save the raw probabilities. Scoring happens offline (bzaf.score), so one readout
serves every predictor.

Per item, four variants (all in the same request where possible; the questions are isolated from each other):
  noul      one yes/no per option; the question does not list the other options (today's workaround)
  noul_ctx  one yes/no per option, with every option listed in the question (a zero-training stand-in for
            "options see each other", direction 2)
  pick      one Choice over all options (its ranking feeds the count approach)
  count     one Choice: "how many of these options apply?", answers 0..K
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Iterable

from .client import DecisionClient
from .schema import Item

VARIANTS = ("noul", "noul_ctx", "pick", "count")


def _listing(options: list[str]) -> str:
    return "\n".join(f"- {o}" for o in options)


def count_label(n: int, k: int) -> str:
    if n == 0:
        return "none of the options apply"
    if n == k and k > 1:
        return f"all {k} options apply"
    return "exactly one option applies" if n == 1 else f"exactly {n} options apply"


def build_questions(item: Item, variants: Iterable[str] = VARIANTS) -> dict[str, dict]:
    q, opts, k = item.question, item.options, len(item.options)
    out: dict[str, dict] = {}
    variants = set(variants)
    if "noul" in variants:
        for j, o in enumerate(opts):
            out[f"noul_{j}"] = {"type": "noul", "instructions": f"{q}\nDoes this option apply?\nOption: {o}"}
    if "noul_ctx" in variants:
        for j, o in enumerate(opts):
            out[f"noulctx_{j}"] = {"type": "noul", "instructions": f"{q}\nAll options:\n{_listing(opts)}\n\nDoes this option apply?\nOption: {o}"}
    if "pick" in variants:
        out["pick"] = {"type": "choice", "instructions": f"{q}\nPick the option that applies best.", "criteria": {o: None for o in opts}}
    if "count" in variants:
        out["count"] = {"type": "choice", "instructions": f"{q}\nOptions:\n{_listing(opts)}\n\nHow many of these options apply?",
                        "criteria": {str(n): count_label(n, k) for n in range(k + 1)}}
    return out


def parse_answers(item: Item, answers: dict) -> dict[str, list[float]]:
    k = len(item.options)
    rec: dict[str, list[float]] = {}
    if "noul_0" in answers:
        rec["noul"] = [float(answers[f"noul_{j}"]["noul"]) for j in range(k)]
    if "noulctx_0" in answers:
        rec["noul_ctx"] = [float(answers[f"noulctx_{j}"]["noul"]) for j in range(k)]
    if "pick" in answers:
        p = answers["pick"]["probabilities"]
        rec["pick"] = [float(p[o]) for o in item.options]
    if "count" in answers:
        p = answers["count"]["probabilities"]
        rec["count"] = [float(p[str(n)]) for n in range(k + 1)]
    return rec


def read_item(client: DecisionClient, item: Item, variants: Iterable[str] = VARIANTS, max_questions: int = 64) -> dict:
    questions = build_questions(item, variants)
    keys = list(questions)
    answers: dict = {}
    t0 = time.perf_counter()
    for i in range(0, len(keys), max_questions):  # isolation makes chunking exact: same state, independent questions
        chunk = {key: questions[key] for key in keys[i : i + max_questions]}
        answers.update(client.decide(item.state, chunk)["answers"])
    rec = {"id": item.id, "dataset": item.dataset, "model": client.model, "k": len(item.options), "gold": item.gold}
    rec.update(parse_answers(item, answers))
    rec["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return rec


def run_readout(client: DecisionClient, items: list[Item], out: str | Path, variants: Iterable[str] = VARIANTS,
                max_questions: int = 64, log: Callable[[str], None] = print) -> int:
    """Append one record per item to `out`, skipping items already there (safe to stop and resume)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        done = {json.loads(line)["id"] for line in out.read_text(encoding="utf-8").splitlines() if line.strip()}
    todo = [it for it in items if it.id not in done]
    log(f"{len(done)} done, {len(todo)} to go -> {out}")
    n = 0
    with out.open("a", encoding="utf-8") as f:
        for i, item in enumerate(todo, 1):
            try:
                rec = read_item(client, item, variants, max_questions)
            except Exception as e:  # keep going; failures are recorded and count as unanswered when scoring
                rec = {"id": item.id, "dataset": item.dataset, "model": client.model, "k": len(item.options), "gold": item.gold,
                       "error": str(e)[:500]}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            n += 1
            if i % 25 == 0 or i == len(todo):
                log(f"  {i}/{len(todo)}")
    return n
