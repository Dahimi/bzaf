"""Benchmark v0: fixed multi-answer evaluation tracks, readout plan and report. See docs/benchmark.md.

    bzaf bench prepare                                   # -> data/bench-v0/*.jsonl + manifest.json (deterministic)
    bzaf bench readout --base-url URL --model M          # -> runs/bench-v0/M/*.jsonl, resumable
    bzaf bench score runs/bench-v0/M --out experiments/.../results/M
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

import numpy as np

from .data import load_ecthr, load_goemotions, load_nlupp, load_sata, load_synthetic, load_unfair_tos, load_wide
from .schema import Item, read_items, read_jsonl, write_items
from .score import format_report, score_records

VERSION = "v0"
ONE_PASS = ("pick", "count")


@dataclass(frozen=True)
class Track:
    name: str
    loader: Callable[..., list[Item]]
    kwargs: dict = field(default_factory=dict)
    size: int | None = None            # fixed random subset; None = all items
    fanout: str = "noul_ctx"           # the per-option yes/no baseline: noul_ctx lists every option in each question
    separate_timing: bool = False      # read the fan-out and the one-pass questions in separate requests, to time them
    role: str = "headline"             # headline tracks are averaged in the summary; probes are reported apart
    about: str = ""


TRACKS = (
    Track("sata", load_sata, {"lettered": True}, None, about="exam-style knowledge questions, 3-16 options, 2-11 answers (SATA-Bench, all 1,650)"),
    Track("goemotions", load_goemotions, {"split": "test"}, 600, about="emotions in Reddit comments, 28 options, mostly 1 answer"),
    Track("unfair_tos", load_unfair_tos, {"split": "test"}, 800, about="unfair clause types in terms of service, 8 options, mostly none"),
    Track("nlupp", load_nlupp, {}, 600, about="intents in customer messages, 40-48 options with descriptions, 0-6 answers"),
    Track("ecthr", load_ecthr, {"split": "test"}, 300, about="violated articles from court case facts, 10 options, long inputs (up to ~6k tokens)"),
    Track("synthetic", load_synthetic, {"n": 300}, None, about="statements about a JSON order, exact gold, 4-10 options, 0-10 answers"),
    Track("wide", load_wide, {"n_per_size": 75}, None, fanout="noul", separate_timing=True, role="probe",
          about="products in an order, 10/50/100/200 options, 0-6 answers: cost and quality against the number of options"),
)
ORDER_SOURCES = {"sata": 100, "goemotions": 100, "nlupp": 100}  # items re-asked with shuffled options
ORDER_SEED = 1


def permuted(item: Item, rng: random.Random) -> Item:
    """The same item with its options shuffled; meta.perm[j] = original index of the option now at position j."""
    perm = list(range(len(item.options)))
    rng.shuffle(perm)
    meta = dict(item.meta, perm=perm)
    if "descriptions" in item.meta:
        meta["descriptions"] = [item.meta["descriptions"][i] for i in perm]
    gold = set(item.gold)
    return replace(item, options=[item.options[i] for i in perm], gold=[j for j, i in enumerate(perm) if i in gold], meta=meta)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(out: str | Path = f"data/bench-{VERSION}", tracks: list[str] | None = None, log=print) -> dict:
    out = Path(out)
    manifest = {"version": VERSION, "tracks": {}}
    chosen: dict[str, list[Item]] = {}
    for t in TRACKS:
        if tracks and t.name not in tracks:
            continue
        items = t.loader(limit=t.size, seed=0, **t.kwargs)
        chosen[t.name] = items
        path = out / f"{t.name}.jsonl"
        write_items(items, path)
        manifest["tracks"][t.name] = {
            "file": path.name, "items": len(items), "sha256": _sha(path), "role": t.role, "about": t.about,
            "options_mean": round(float(np.mean([len(i.options) for i in items])), 1),
            "options_max": max(len(i.options) for i in items),
            "answers": dict(sorted(Counter(len(i.gold) for i in items).items())),
        }
        log(f"{t.name}: {len(items)} items -> {path}")
    if all(name in chosen for name in ORDER_SOURCES):
        rng = random.Random(ORDER_SEED)
        order = [permuted(it, rng) for name, n in ORDER_SOURCES.items()
                 for it in random.Random(ORDER_SEED).sample(chosen[name], n)]
        path = out / "order.jsonl"
        write_items(order, path)
        manifest["order"] = {"file": path.name, "items": len(order), "sha256": _sha(path), "sources": ORDER_SOURCES,
                             "about": "the same items with shuffled options; compared with the main tracks' answers"}
        log(f"order: {len(order)} items -> {path}")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def readout_plan(bench: Path, with_set: bool = False, tracks: list[str] | None = None) -> list[tuple[Path, str, list[str]]]:
    """(items file, output stem, variants) for every part of the benchmark."""
    extra = ["set"] if with_set else []
    plan = []
    for t in TRACKS:
        if tracks and t.name not in tracks:
            continue
        f = bench / f"{t.name}.jsonl"
        if t.separate_timing:
            plan.append((f, f"{t.name}__fanout", [t.fanout]))
            plan.append((f, f"{t.name}__onepass", list(ONE_PASS) + extra))
        else:
            plan.append((f, t.name, [t.fanout, *ONE_PASS, *extra]))
    if (bench / "order.jsonl").exists() and (not tracks or "order" in tracks):
        plan.append((bench / "order.jsonl", "order", ["noul_ctx", *ONE_PASS, *extra]))
    return plan


def readout(client, bench: str | Path, out: str | Path, with_set: bool = False, tracks: list[str] | None = None,
            max_questions: int = 64, concurrency: int = 1, limit: int | None = None, log=print) -> None:
    from .readout import run_readout

    bench, out = Path(bench), Path(out)
    for items_file, stem, variants in readout_plan(bench, with_set, tracks):
        if not items_file.exists():
            log(f"skip {stem}: {items_file} missing (run `bzaf bench prepare`)")
            continue
        items = list(read_items(items_file))[:limit]
        log(f"== {stem} ({len(items)} items, {','.join(variants)})")
        run_readout(client, items, out / f"{stem}.jsonl", variants, max_questions, concurrency, log)


# --- report -------------------------------------------------------------------------------------------------------

SUMMARY = (  # column label, predictors in order of preference
    ("yes/no per option, tuned", ("noul_ctx+platt", "noul+platt")),
    ("Choice + dataset count", ("pick+dev_prior",)),
    ("native set, as shipped", ("set@shipped",)),
    ("ceiling: ranking + true count", ("pick+true_count",)),
)


STABILITY_PREDICTORS = ("noul_ctx@0.5", "noul_ctx+platt", "pick@top1", "pick+count", "pick+dev_prior", "set@shipped")


def _first(rows: dict, names: tuple[str, ...]) -> str | None:
    return next((n for n in names if n in rows), None)


def stability(main: dict, order: dict) -> dict:
    """Per dataset and predictor: share of items whose answer set is unchanged when the options are shuffled, and the
    mean Jaccard overlap of the two answers (after mapping shuffled positions back)."""
    out: dict = {}
    for ds, r in order.items():
        if ds not in main:
            continue
        pos = {i: n for n, i in enumerate(main[ds]["test_ids"])}
        res = {}
        for name, m in r["predictors"].items():
            if name not in main[ds]["predictors"] or name not in STABILITY_PREDICTORS:
                continue
            base = main[ds]["predictors"][name]["per_item_pred"]
            same, jac = [], []
            for i, iid in enumerate(r["test_ids"]):
                a, perm = m["per_item_pred"][i], r["test_perm"][i]
                b = base[pos[iid]] if iid in pos else None
                if a is None or b is None or perm is None:
                    continue
                a, b = {perm[j] for j in a}, set(b)
                same.append(float(a == b)); jac.append(len(a & b) / len(a | b) if a | b else 1.0)
            if same:
                res[name] = {"n": len(same), "unchanged": float(np.mean(same)), "jaccard": float(np.mean(jac))}
        out[ds] = res
    return out


def _median_s(latencies: list[dict], prefix: str) -> float:
    v = [x for d in latencies for key, x in d.items() if key.startswith(f"latency_ms:{prefix}")]
    return float(np.median(v)) / 1000 if v else float("nan")


def cost_by_k(report: dict) -> list[dict]:
    """Wide probe: median seconds per item for the per-option fan-out and the one-pass questions, and example F1 of the
    main predictors, for each number of options."""
    r = report.get("wide")
    if not r:
        return []
    rows = []
    ks = r["test_k"]
    for k in sorted(set(ks)):
        idx = [i for i, x in enumerate(ks) if x == k]
        lat = [r["test_latency"][i] for i in idx]
        row = {"k": k, "n": len(idx), "fanout_s": _median_s(lat, "noul"), "onepass_s": _median_s(lat, "count")}
        for label, names in SUMMARY:
            n = _first(r["predictors"], names)
            if n:
                row[label] = float(np.mean([r["predictors"][n]["per_item_f1"][i] for i in idx]))
        rows.append(row)
    return rows


def score(run_dir: str | Path, dev_frac: float = 0.3) -> dict:
    run_dir = Path(run_dir)
    files = sorted(p for p in run_dir.glob("*.jsonl") if p.stem != "order")
    records = [r for p in files for r in read_jsonl(p)]
    main = score_records(records, dev_frac)
    order_file = run_dir / "order.jsonl"
    order = score_records(read_jsonl(order_file), dev_frac, fit_on=records) if order_file.exists() else {}
    return {"main": main, "order": order, "stability": stability(main, order), "cost": cost_by_k(main),
            "models": sorted({r.get("model", "") for r in records})}


def format_bench(res: dict) -> str:
    main = res["main"]
    lines = [f"# Benchmark {VERSION} — {', '.join(res['models'])}", "",
             "Summary: exact-set % / example F1 on each track's test split (dev split used only for fitting).", "",
             "| track | items (test) | " + " | ".join(label for label, _ in SUMMARY) + " |",
             "|---|---|" + "---|" * len(SUMMARY)]
    roles = {t.name: t.role for t in TRACKS}
    for ds, r in main.items():
        cells = []
        for _, names in SUMMARY:
            n = _first(r["predictors"], names)
            m = r["predictors"].get(n) if n else None
            cells.append(f"{100*m['exact']:.1f} / {m['example_f1']:.3f}" if m else "—")
        tag = " (probe)" if roles.get(ds) == "probe" else ""
        lines.append(f"| {ds}{tag} | {r['n_test']} | " + " | ".join(cells) + " |")
    if res["stability"]:
        lines += ["", "## Option-order stability", "",
                  "Same items, options shuffled: share of answers unchanged, and mean Jaccard overlap of the two answers.", "",
                  "| track | predictor | items | unchanged | Jaccard |", "|---|---|---|---|---|"]
        for ds, preds in res["stability"].items():
            for name, s in preds.items():
                lines.append(f"| {ds} | {name} | {s['n']} | {100*s['unchanged']:.1f} % | {s['jaccard']:.3f} |")
    if res["cost"]:
        labels = [label for label, _ in SUMMARY if any(label in row for row in res["cost"])]
        lines += ["", "## Cost and quality against the number of options (wide probe)", "",
                  "Median seconds per item for one yes/no question per option vs the one-pass questions; example F1.", "",
                  "| options | items | fan-out s | one-pass s | " + " | ".join(labels) + " |",
                  "|---|---|---|---|" + "---|" * len(labels)]
        for row in res["cost"]:
            lines.append(f"| {row['k']} | {row['n']} | {row['fanout_s']:.2f} | {row['onepass_s']:.2f} | "
                         + " | ".join(f"{row[label]:.3f}" if label in row else "—" for label in labels) + " |")
    lines += ["", format_report(main, ", ".join(res["models"])).replace("# E01 readout scores", "# Per-track details", 1)]
    return "\n".join(lines)


def score_dir(run_dir: str, dev_frac: float = 0.3, out: str | None = None) -> str:
    res = score(run_dir, dev_frac)
    text = format_bench(res)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        slim = {ds: {**{k: v for k, v in r.items() if not k.startswith("test_")},
                     "predictors": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("per_item")} for k, v in r["predictors"].items()}}
                for ds, r in res["main"].items()}
        Path(f"{out}.json").write_text(json.dumps({"models": res["models"], "tracks": slim, "stability": res["stability"],
                                                   "cost": res["cost"]}, indent=2))
        Path(f"{out}.md").write_text(text)
    return text


def compare(run_a: str | Path, run_b: str | Path, predictor: str = "pick+true_count", metric: str = "per_item_exact",
            n_boot: int = 2000, seed: int = 0, dev_frac: float = 0.3) -> dict:
    """Paired comparison of two models' benchmark runs (A − B) for one predictor, on the test items both answered:
    per track, and the macro average over headline tracks (each track weighs the same; bootstrap resamples items
    within each track)."""
    a, b = score(run_a, dev_frac)["main"], score(run_b, dev_frac)["main"]
    roles = {t.name: t.role for t in TRACKS}
    rng = np.random.default_rng(seed)
    per_track, diffs = {}, {}
    for ds in sorted(set(a) & set(b)):
        if predictor not in a[ds]["predictors"] or predictor not in b[ds]["predictors"]:
            continue
        va = dict(zip(a[ds]["test_ids"], a[ds]["predictors"][predictor][metric]))
        vb = dict(zip(b[ds]["test_ids"], b[ds]["predictors"][predictor][metric]))
        d = np.array([va[i] - vb[i] for i in va if i in vb and va[i] is not None and vb[i] is not None], dtype=float)
        if not len(d):
            continue
        boots = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1)
        per_track[ds] = {"n": len(d), "mean": float(d.mean()), "ci": (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))}
        if roles.get(ds) == "headline":
            diffs[ds] = d
    out = {"predictor": predictor, "metric": metric, "tracks": per_track}
    if diffs:
        boots = np.mean([d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1) for d in diffs.values()], axis=0)
        out["macro"] = {"tracks": sorted(diffs), "mean": float(np.mean([d.mean() for d in diffs.values()])),
                        "ci": (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))}
    return out


def format_compare(res: dict, a: str, b: str) -> str:
    scale = 100.0 if res["metric"] in ("per_item_exact", "per_item_f1") else 1.0
    lines = [f"# {a} − {b}: {res['predictor']}, {res['metric'].removeprefix('per_item_')}", "",
             "| track | items | mean [95% CI] |", "|---|---|---|"]
    for ds, r in res["tracks"].items():
        lines.append(f"| {ds} | {r['n']} | {scale*r['mean']:+.2f} [{scale*r['ci'][0]:+.2f}, {scale*r['ci'][1]:+.2f}] |")
    if "macro" in res:
        m = res["macro"]
        lines.append(f"| **macro (headline tracks)** | {len(m['tracks'])} tracks | **{scale*m['mean']:+.2f}** "
                     f"[{scale*m['ci'][0]:+.2f}, {scale*m['ci'][1]:+.2f}] |")
    return "\n".join(lines)
