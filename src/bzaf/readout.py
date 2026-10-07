"""Experiment E01 readouts: ask an existing decision model about each multi-answer item using only the question
types it already supports, and save the raw probabilities. Scoring happens offline (bzaf.score), so one readout
serves every predictor.

Per item, four variants (all in the same request where possible; the questions are isolated from each other):
  noul      one yes/no per option; the question does not list the other options (today's workaround)
  noul_ctx  one yes/no per option, with every option listed in the question (a zero-training stand-in for
            "options see each other", direction 2)
  pick      one Choice over all options (its ranking feeds the count approach)
  count     one Choice: "how many of these options apply?", answers 0..K
  set       one native multi-answer question (type "set", e.g. Vela 2.0): one probability per option plus the server's
            own threshold. Opt-in (not in VARIANTS): only servers that declare the type accept it.
  native    single-answer items (general track): the question asked in its own type, meta.qtype = choice, noul or
            score; the answer's probabilities are recorded per option.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterable

from .client import DecisionClient
from .schema import Item

VARIANTS = ("noul", "noul_ctx", "pick", "count")
ALL_VARIANTS = VARIANTS + ("set", "native")


def _listing(options: list[str], descriptions: list[str] | None = None) -> str:
    if descriptions:
        return "\n".join(f"- {o}: {d}" for o, d in zip(options, descriptions))
    return "\n".join(f"- {o}" for o in options)


def _named(o: str, d: str | None) -> str:
    return f"{o} ({d})" if d else o


def count_label(n: int, k: int) -> str:
    if n == 0:
        return "none of the options apply"
    if n == k and k > 1:
        return f"all {k} options apply"
    return "exactly one option applies" if n == 1 else f"exactly {n} options apply"


def build_questions(item: Item, variants: Iterable[str] = VARIANTS) -> dict[str, dict]:
    q, opts, k = item.question, item.options, len(item.options)
    desc = item.meta.get("descriptions")  # optional, one per option (e.g. NLU++ intent descriptions)
    ds = desc or [None] * k
    out: dict[str, dict] = {}
    variants = set(variants)
    if "noul" in variants:
        for j, o in enumerate(opts):
            out[f"noul_{j}"] = {"type": "noul", "instructions": f"{q}\nDoes this option apply?\nOption: {_named(o, ds[j])}"}
    if "noul_ctx" in variants:
        listing = _listing(opts, desc)
        for j, o in enumerate(opts):
            out[f"noulctx_{j}"] = {"type": "noul",
                                   "instructions": f"{q}\nAll options:\n{listing}\n\nDoes this option apply?\nOption: {_named(o, ds[j])}"}
    if "pick" in variants:
        out["pick"] = {"type": "choice", "instructions": f"{q}\nPick the option that applies best.", "criteria": dict(zip(opts, ds))}
    if "count" in variants:
        out["count"] = {"type": "choice", "instructions": f"{q}\nOptions:\n{_listing(opts, desc)}\n\nHow many of these options apply?",
                        "criteria": {str(n): count_label(n, k) for n in range(k + 1)}}
    if "set" in variants:
        out["set"] = {"type": "set", "instructions": f"{q}\nSelect every option that applies.", "criteria": dict(zip(opts, ds))}
    if "native" in variants:
        qtype = item.meta.get("qtype", "choice")
        if qtype == "noul":
            out["native"] = {"type": "noul", "instructions": q}
        elif qtype == "score":
            out["native"] = {"type": "score", "instructions": q, "criteria": list(opts)}
        else:
            out["native"] = {"type": "choice", "instructions": q, "criteria": dict(zip(opts, ds))}
    return out


def parse_answers(item: Item, answers: dict, sets: dict | None = None, thresholds: dict | None = None) -> dict:
    k = len(item.options)
    rec: dict = {}
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
    if "native" in answers:
        a, qtype = answers["native"], item.meta.get("qtype", "choice")
        if qtype == "noul":
            rec["native"] = [1.0 - float(a["noul"]), float(a["noul"])]  # options are ["no", "yes"]
        else:
            p = a["probabilities"]
            keys = [str(j) for j in range(k)] if qtype == "score" and str(0) in p else item.options
            rec["native"] = [float(p[key]) for key in keys]
    if sets and "set" in sets:
        p = sets["set"]["probabilities"]
        rec["set"] = [float(p[o]) for o in item.options]
        if thresholds and "set" in thresholds:
            rec["set_threshold"] = float(thresholds["set"])
    return rec


def read_item(client: DecisionClient, item: Item, variants: Iterable[str] = VARIANTS, max_questions: int = 64) -> dict:
    questions = build_questions(item, variants)
    keys = list(questions)
    answers: dict = {}
    sets: dict = {}
    thresholds: dict = {}
    t0 = time.perf_counter()
    for i in range(0, len(keys), max_questions):  # isolation makes chunking exact: same state, independent questions
        chunk = {key: questions[key] for key in keys[i : i + max_questions]}
        resp = client.decide(item.state, chunk)
        answers.update(resp["answers"])
        sets.update(resp.get("sets") or {})
        thresholds.update(resp.get("thresholds") or {})
    rec = {"id": item.id, "dataset": item.dataset, "model": client.model, "k": len(item.options), "gold": item.gold,
           "variants": sorted(set(variants))}
    if "perm" in item.meta:  # options were shuffled (order-stability track): perm[j] = original index of option j
        rec["perm"] = item.meta["perm"]
    rec.update(parse_answers(item, answers, sets, thresholds))
    rec["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return rec


def run_readout(client: DecisionClient, items: list[Item], out: str | Path, variants: Iterable[str] = VARIANTS,
                max_questions: int = 64, concurrency: int = 1, log: Callable[[str], None] = print) -> int:
    """Append one record per item to `out`, skipping items already answered (safe to stop and resume).

    Items that failed on an earlier run are retried: their error records are dropped from `out` first. concurrency > 1
    sends that many items at once; worth it against a GPU server that batches requests (Kev on CUDA batches up to 64),
    not against Kev on a Mac, which runs one request at a time.
    """
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if out.exists():
        recs = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
        ok = [r for r in recs if "error" not in r]
        if len(ok) < len(recs):  # rewrite without the failures, so a retry does not leave duplicates
            out.write_text("".join(json.dumps(r) + "\n" for r in ok), encoding="utf-8")
            log(f"retrying {len(recs) - len(ok)} items that failed before")
        done = {r["id"] for r in ok}
    todo = [it for it in items if it.id not in done]
    log(f"{len(done)} done, {len(todo)} to go -> {out}")

    def one(item: Item) -> dict:
        try:
            return read_item(client, item, variants, max_questions)
        except Exception as e:  # keep going; failures are recorded and count as unanswered when scoring
            return {"id": item.id, "dataset": item.dataset, "model": client.model, "k": len(item.options), "gold": item.gold,
                    "error": str(e)[:500]}

    n, errors, latencies = 0, [], []
    t0 = time.perf_counter()
    pool = ThreadPoolExecutor(max_workers=max(1, concurrency))
    try:
        with out.open("a", encoding="utf-8") as f:
            for fut in as_completed([pool.submit(one, it) for it in todo]):  # written as they finish; order does not matter
                rec = fut.result()
                if "error" in rec:
                    errors.append(rec["error"])
                else:
                    latencies.append(rec["latency_ms"])
                f.write(json.dumps(rec) + "\n")
                f.flush()
                n += 1
                if n % 25 == 0 or n == len(todo):
                    log(f"  {n}/{len(todo)}")
    except KeyboardInterrupt:  # stop at once: everything finished so far is on disk, the rest is retried next time
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    pool.shutdown()
    if todo:
        wall = time.perf_counter() - t0
        log(f"done: {len(latencies)} ok, {len(errors)} failed, {wall / len(todo):.2f} s per item wall clock "
            f"(concurrency {concurrency})")
        if errors:
            log(f"first error: {errors[0]}")
    return n
