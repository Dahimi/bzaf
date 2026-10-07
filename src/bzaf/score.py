"""Score E01 readouts: split each dataset into dev (for fitting) and test (for reporting) by a stable hash of the
item id, fit predictors on dev, report test metrics with bootstrap CIs, plus the comparisons the E01 gates use."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from .metrics import bootstrap_ci, evaluate, paired_diff_ci
from .predictors import default_predictors
from .schema import read_jsonl


def is_dev(item_id: str, dev_frac: float) -> bool:
    h = int(hashlib.sha256(item_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return h < dev_frac


def score_records(records: list[dict], dev_frac: float = 0.3) -> dict:
    by_ds: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_ds[r["dataset"]].append(r)
    report = {}
    for ds, recs in sorted(by_ds.items()):
        dev = [r for r in recs if is_dev(r["id"], dev_frac)]
        test = [r for r in recs if not is_dev(r["id"], dev_frac)]
        golds = [set(r["gold"]) for r in test]
        rows = {}
        for pred in default_predictors():
            if not any(pred.available(r) for r in test):
                continue
            pred.fit(dev)
            sets, logps = [], []
            for r in test:
                if not pred.available(r):
                    sets.append(None); logps.append(None); continue
                p = pred.predict(r)
                sets.append(p.subset)
                logps.append(p.dist.log_prob(r["gold"]) if p.dist is not None else None)
            has_dist = any(lp is not None for lp in logps)
            m = evaluate(sets, golds, logps if has_dist else None)
            m["exact_ci"] = bootstrap_ci(m["per_item_exact"])
            if has_dist:
                m["nll_ci"] = bootstrap_ci(m["per_item_nll"])
            rows[pred.name] = m
        errors = [r["error"] for r in recs if "error" in r]
        report[ds] = {"n_dev": len(dev), "n_test": len(test), "n_failed": len(errors), "first_error": errors[0] if errors else None,
                      "predictors": rows, "comparisons": comparisons(rows)}
    return report


def comparisons(rows: dict) -> dict:
    """The E01 signals: (name, a, b) -> mean of a - b on test items, with CI. Exact-set accuracy in points."""
    out = {}

    def diff(key, a, b, metric="per_item_exact", scale=100.0):
        if a in rows and b in rows and metric in rows[a] and metric in rows[b]:
            mean, lo, hi = paired_diff_ci(rows[a][metric], rows[b][metric])
            out[key] = {"a": a, "b": b, "metric": metric, "mean": mean * scale, "ci": (lo * scale, hi * scale)}

    # native multi-answer type (E01c): is its count the bottleneck, and does its ranking match Choice's?
    diff("V1 native set as shipped vs its ranking + true count", "set@shipped", "set+true_count")
    diff("V2 Choice ranking vs native-set ranking (both told the count)", "pick+true_count", "set+true_count")
    diff("V3 dataset count prior on native-set scores vs shipped threshold", "set+dev_prior", "set@shipped")
    nouls = [n for n in ("noul@0.5", "noul+platt", "noul_ctx@0.5", "noul_ctx+platt") if n in rows]
    if not nouls:
        return out
    best_noul = max(nouls, key=lambda n: rows[n]["exact"])
    diff("G1 ranking+true count vs best yes/no", "pick+true_count", best_noul)
    diff("R1 Choice ranking vs yes/no ranking (both told the count)", "pick+true_count", "noul_ctx+true_count")
    diff("C1 value of the right count over top-1", "pick+true_count", "pick@top1")
    diff("S2 asked count vs true count (headroom)", "pick+count", "pick+true_count")
    diff("S5 dataset count prior vs true count (item-level counting headroom)", "pick+dev_prior", "pick+true_count")
    diff("S3 count dial on yes/no (ctx)", "noul_ctx+count", "noul_ctx@0.5")
    diff("S4 options in context (yes/no)", "noul_ctx@0.5", "noul@0.5")
    diff("S3 count dial on yes/no (ctx), log-loss", "noul_ctx+count", "noul_ctx@0.5", metric="per_item_nll", scale=1.0)
    return out


def format_report(report: dict, model: str = "") -> str:
    lines = [f"# E01 readout scores{f' — {model}' if model else ''}", ""]
    for ds, r in report.items():
        failed = r.get("n_failed", 0)
        lines += [f"## {ds} (dev {r['n_dev']}, test {r['n_test']}, failed {failed})", ""]
        if failed:
            share = failed / max(1, r["n_dev"] + r["n_test"])
            lines += [f"> **{'WARNING: ' if share > 0.02 else ''}{failed} items failed ({100 * share:.0f} %)** and count as wrong. "
                      f"First error: `{(r.get('first_error') or '')[:300]}`. Re-run the readout to retry them.", ""]
        lines += [
                  "| predictor | exact-set % [95% CI] | example F1 | micro F1 | count acc | mean size (gold) | set log-loss |",
                  "|---|---|---|---|---|---|---|"]
        for name, m in r["predictors"].items():
            lo, hi = m["exact_ci"]
            nll = f"{m['set_nll']:.3f}" if "set_nll" in m else "—"
            lines.append(f"| {name} | {100*m['exact']:.1f} [{100*lo:.1f}, {100*hi:.1f}] | {m['example_f1']:.3f} | {m['micro_f1']:.3f} | "
                         f"{m['count_acc']:.3f} | {m['mean_pred_size']:.2f} ({m['mean_gold_size']:.2f}) | {nll} |")
        if r["comparisons"]:
            lines += ["", "| signal | a − b | mean [95% CI] |", "|---|---|---|"]
            for key, c in r["comparisons"].items():
                unit = " nats" if c["metric"] == "per_item_nll" else " pts"
                lines.append(f"| {key} | {c['a']} − {c['b']} | {c['mean']:+.2f}{unit} [{c['ci'][0]:+.2f}, {c['ci'][1]:+.2f}] |")
        lines.append("")
    return "\n".join(lines)


def score_files(paths: list[str], dev_frac: float = 0.3, out: str | None = None) -> str:
    records = [r for p in paths for r in read_jsonl(p)]
    models = sorted({r.get("model", "") for r in records})
    report = score_records(records, dev_frac)
    text = format_report(report, ", ".join(models))
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        slim = {ds: {**r, "predictors": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("per_item")} for k, v in r["predictors"].items()}}
                for ds, r in report.items()}
        Path(f"{out}.json").write_text(json.dumps(slim, indent=2))  # not with_suffix: "kev-0.8b" would become "kev-0.md"
        Path(f"{out}.md").write_text(text)
    return text
