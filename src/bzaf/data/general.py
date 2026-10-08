"""General (single-answer) decision track of benchmark v0: the no-regression check for every model we train.

Seven public test sets, read with the model's own question types (Choice, Noul, Score), ~300 items each. Items use the
multi-answer item format with exactly one gold option; `meta.qtype` says how to ask (choice, noul or score). Noul
items have the options ["no", "yes"]; Score items list their levels in order. Evaluation only.

| track | type | options | source, licence |
|---|---|---|---|
| mmlu_pro | choice | 3-10 | TIGER-Lab/MMLU-Pro test, MIT |
| bbh | choice | 2-18 | BIG-Bench Hard @9ee07bd (23 fixed-option tasks), MIT; carries the BIG-bench canary, never train on it |
| anli | choice | 3 | facebook/anli test r1-r3, CC BY-NC 4.0 (evaluation only) |
| hellaswag | choice | 4 | Rowan/hellaswag validation, MIT |
| clinc150 | choice | 151 | clinc/oos-eval @828f809 test + out-of-scope test, CC BY 3.0 |
| boolq | noul | yes/no | google/boolq validation, CC BY-SA 3.0 |
| sst5 | score | 5 levels | SetFit/sst5 test (Stanford Sentiment Treebank), research use |
"""
from __future__ import annotations

import json
import re

from ..schema import Item
from ._util import fetch, sample

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BBH_REV = "9ee07bd481feebf959a6b59d61ea57bdcf30964d"
BBH_URL = f"https://raw.githubusercontent.com/suzgunmirac/BIG-Bench-Hard/{BBH_REV}/bbh/{{task}}.json"
BBH_TASKS = (  # the 23 tasks with a fixed answer set (the four free-form tasks are left out, as the Decision Index does)
    "boolean_expressions", "causal_judgement", "date_understanding", "disambiguation_qa", "formal_fallacies",
    "geometric_shapes", "hyperbaton", "logical_deduction_five_objects", "logical_deduction_seven_objects",
    "logical_deduction_three_objects", "movie_recommendation", "navigate", "penguins_in_a_table",
    "reasoning_about_colored_objects", "ruin_names", "salient_translation_error_detection", "snarks",
    "sports_understanding", "temporal_sequences", "tracking_shuffled_objects_five_objects",
    "tracking_shuffled_objects_seven_objects", "tracking_shuffled_objects_three_objects", "web_of_lies",
)
BINARY = {"Yes": ("Yes", "No"), "No": ("Yes", "No"), "yes": ("yes", "no"), "no": ("yes", "no"), "True": ("True", "False"),
          "False": ("True", "False"), "valid": ("valid", "invalid"), "invalid": ("valid", "invalid")}
CLINC_REV = "828f8093932c8fe6ca7936c3d2e52903b1c523de"
CLINC_URL = f"https://raw.githubusercontent.com/clinc/oos-eval/{CLINC_REV}/data/data_full.json"
SST5_LEVELS = ["very negative", "negative", "neutral", "positive", "very positive"]
NLI = {"entailment": "the premise shows the hypothesis is true", "neutral": "the premise neither confirms nor rules it out",
       "contradiction": "the premise shows the hypothesis is false"}


def _lettered(options: list[str]) -> list[str]:
    return [f"{LETTERS[j]}. {o}" for j, o in enumerate(options)]


def _item(id_, dataset, state, question, options, gold, qtype="choice", **meta) -> Item:
    return Item(id=id_, dataset=dataset, state=state, question=question, options=options, gold=[gold],
                meta={"qtype": qtype, **meta})


def load_bbh(limit: int | None = 300, seed: int = 0) -> list[Item]:
    items = []
    for task in BBH_TASKS:
        rows = json.loads(fetch(BBH_URL.format(task=task), f"bbh_{task}.json").read_text(encoding="utf-8"))["examples"]
        for i, row in enumerate(rows):
            text, target = row["input"], row["target"].strip()
            m = re.search(r"\nOptions:\n(\(A\).*)$", text, re.S)
            if m:  # lettered options: (A) ... (B) ...
                opts = re.findall(r"^\(([A-Z])\)\s*(.*)$", m.group(1), re.M)
                letters = [x for x, _ in opts]
                gold = target.strip("()")
                if gold not in letters or len(set(t for _, t in opts)) != len(opts):
                    continue  # a handful of source items give the answer text instead of a letter
                items.append(_item(f"bbh:{task}:{i}", "bbh", text[: m.start()].strip(), "Which option is correct?",
                                   _lettered([t.strip() for _, t in opts]), letters.index(gold), task=task))
            elif target in BINARY:
                opts = list(BINARY[target])
                state = re.sub(r"\nOptions:\n(- .*\n?)+$", "", text).strip()
                items.append(_item(f"bbh:{task}:{i}", "bbh", state, "Which answer is correct?", opts, opts.index(target), task=task))
    return sample(items, limit, seed)


def load_clinc150(limit: int | None = 300, seed: int = 0) -> list[Item]:
    data = json.loads(fetch(CLINC_URL, "clinc150_data_full.json").read_text(encoding="utf-8"))
    intents = sorted({intent for _, intent in data["test"]})
    options = [x.replace("_", " ") for x in intents] + ["out of scope"]
    rows = [(t, intents.index(i)) for t, i in data["test"]] + [(t, len(intents)) for t, _ in data["oos_test"]]
    items = [_item(f"clinc150:{n}", "clinc150", text, "What does the user want?", options, gold) for n, (text, gold) in enumerate(rows)]
    return sample(items, limit, seed)


def load_mmlu_pro(limit: int | None = 300, seed: int = 0) -> list[Item]:
    from datasets import load_dataset  # optional dependency

    ds = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
    items = []
    for i, row in enumerate(ds):
        opts = [str(o).strip() for o in row["options"]]
        items.append(_item(f"mmlu_pro:{i}", "mmlu_pro", row["question"], "Which option answers the question correctly?",
                           _lettered(opts), int(row["answer_index"]), category=row.get("category")))
    return sample(items, limit, seed)


def load_anli(limit: int | None = 300, seed: int = 0) -> list[Item]:
    from datasets import load_dataset

    items = []
    for r in ("test_r1", "test_r2", "test_r3"):
        for i, row in enumerate(load_dataset("facebook/anli", split=r)):
            if row["label"] not in (0, 1, 2):
                continue
            state = f"Premise: {row['premise']}\nHypothesis: {row['hypothesis']}"
            items.append(_item(f"anli:{r}:{i}", "anli", state, "How does the premise relate to the hypothesis?", list(NLI),
                               int(row["label"]), descriptions=list(NLI.values())))
    return sample(items, limit, seed)


def load_hellaswag(limit: int | None = 300, seed: int = 0, split: str = "validation") -> list[Item]:
    from datasets import load_dataset

    items = []
    for i, row in enumerate(load_dataset("Rowan/hellaswag", split=split)):
        endings = [e.strip() for e in row["endings"]]
        if len(set(endings)) != len(endings) or str(row["label"]) == "":
            continue
        state = f"{row['activity_label']}: {row['ctx']}"
        id_ = f"hellaswag:{i}" if split == "validation" else f"hellaswag:{split}:{i}"
        items.append(_item(id_, "hellaswag", state, "Which ending continues the text most plausibly?",
                           _lettered(endings), int(row["label"])))
    return sample(items, limit, seed)


def load_boolq(limit: int | None = 300, seed: int = 0, split: str = "validation") -> list[Item]:
    from datasets import load_dataset

    items = [_item(f"boolq:{i}" if split == "validation" else f"boolq:{split}:{i}", "boolq", row["passage"],
                   row["question"].strip().capitalize() + "?", ["no", "yes"],
                   int(bool(row["answer"])), qtype="noul")
             for i, row in enumerate(load_dataset("google/boolq", split=split))]
    return sample(items, limit, seed)


def load_sst5(limit: int | None = 300, seed: int = 0, split: str = "test") -> list[Item]:
    from datasets import load_dataset

    items = [_item(f"sst5:{i}" if split == "test" else f"sst5:{split}:{i}", "sst5", row["text"],
                   "How positive is the sentiment of this text?", SST5_LEVELS,
                   int(row["label"]), qtype="score")
             for i, row in enumerate(load_dataset("SetFit/sst5", split=split))]
    return sample(items, limit, seed)
