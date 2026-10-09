"""E02b sources and mixture, offline: each loader on a tiny file in the real format, the count-regime sampler, and the
mixture builder (counts decoupled from sources, benchmark overlap dropped)."""
import io
import json
import random
import tarfile
import zipfile
from collections import Counter

import pytest

from bzaf.schema import Item, write_items


@pytest.fixture
def raw(tmp_path, monkeypatch):
    monkeypatch.setattr("bzaf.data._util.CACHE", tmp_path)
    return tmp_path


def test_qasper_evidence_paragraphs_and_unanswerable(raw):
    from bzaf.data.qasper import load_qasper

    paper = {"title": "T", "abstract": "A", "figures_and_tables": [{"file": "f.png", "caption": "Table 1: Results."}],
             "full_text": [{"section_name": "Intro", "paragraphs": ["First para.", "Second para."]},
                           {"section_name": "Method", "paragraphs": ["Third para."]}],
             "qas": [{"question": "What?", "question_id": "q1", "answers": [
                         {"answer": {"unanswerable": False, "evidence": ["Second para.", "FLOAT SELECTED: Table 1: Results."]}},
                         {"answer": {"unanswerable": False, "evidence": ["Third para."]}}]},
                     {"question": "Why?", "question_id": "q2", "answers": [{"answer": {"unanswerable": True, "evidence": []}}]},
                     {"question": "How?", "question_id": "q3", "answers": [{"answer": {"unanswerable": False, "evidence": ["Not in paper."]}}]}]}
    buf = io.BytesIO(json.dumps({"p1": paper}).encode())
    with tarfile.open(raw / "qasper-train-dev-v0.3.tgz", "w:gz") as tar:
        info = tarfile.TarInfo("qasper-train-v0.3.json")
        info.size = len(buf.getvalue())
        tar.addfile(info, buf)
    items = {it.id: it for it in load_qasper()}
    assert set(items) == {"qasper:q1", "qasper:q2"}  # q3's evidence cannot be placed: skipped
    q1 = items["qasper:q1"]
    assert q1.options == ["P1", "P2", "P3", "P4"] and q1.gold == [1, 2, 3] and "[P4] Table 1: Results." in q1.state
    assert items["qasper:q2"].gold == []


def test_window_keeps_gold_and_neighbours():
    from bzaf.data._units import window

    units = [f"unit {i} " + "x" * 90 for i in range(50)]
    text, keys, gold = window(units, {30}, budget=1100)
    assert 5 <= len(keys) < 50 and len(gold) == 1 and f"[{keys[gold[0]]}] unit 30 " in text
    assert window(["y" * 1000] * 3, {0, 1, 2}, budget=1500) == ("", [], [])  # the gold units alone do not fit


def test_wice_union_of_supporting_sets(raw):
    from bzaf.data.wice import load_wice

    rows = [{"label": "supported", "supporting_sentences": [[0, 2], [1]], "claim": "C1", "evidence": ["a", "b", "c", "d"], "meta": {"id": "w1"}},
            {"label": "not_supported", "supporting_sentences": [], "claim": "C2", "evidence": ["a", "b"], "meta": {"id": "w2"}}]
    (raw / "wice-claim-train.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    items = load_wice()
    assert [it.gold for it in items] == [[0, 1, 2], []] and items[0].options == ["S1", "S2", "S3", "S4"]


def test_squad2_questions_as_options(raw):
    from bzaf.data.squad2 import load_squad2

    data = {"data": [{"title": "Rivers", "paragraphs": [
        {"context": "The Nile is long.", "qas": [
            {"question": "Which river is long?", "is_impossible": False, "answers": [{"text": "Nile"}]},
            {"question": "Which river is short?", "is_impossible": True, "answers": [], "plausible_answers": [{"text": "Nile"}]}]},
        {"context": "The Amazon is wide.", "qas": [
            {"question": "Which river is wide?", "is_impossible": False, "answers": [{"text": "Amazon"}]},
            {"question": "Is the Nile long?", "is_impossible": False, "answers": [{"text": "Nile"}]}]}]}]}
    (raw / "squad-train-v2.0.json").write_text(json.dumps(data))
    first = load_squad2()[0]
    # the other paragraph's question whose answer ("Nile") occurs here is not used as a negative
    assert first.options == ["Which river is long?", "Which river is short?", "Which river is wide?"] and first.gold == [0]


def test_mams_three_questions(raw):
    from bzaf.data.mams import load_mams

    (raw / "mams-acsa-train.xml").write_text(
        '<sentences><sentence><text>Great food, rude staff.</text><aspectCategories>'
        '<aspectCategory category="food" polarity="positive"/><aspectCategory category="staff" polarity="negative"/>'
        '</aspectCategories></sentence></sentences>')
    items = {it.id.split(":")[-1]: it for it in load_mams()}
    names = items["mention"].options
    assert len(names) == 8 and len(items["mention"].meta["descriptions"]) == 8
    assert [names[g] for g in items["mention"].gold] == ["food", "staff"]
    assert [names[g] for g in items["praise"].gold] == ["food"] and [names[g] for g in items["criticise"].gold] == ["staff"]


def test_redocred_pairs_and_subjects(raw):
    from bzaf.data.redocred import RELATIONS, load_redocred

    doc = {"title": "Ghent", "sents": [["Ghent", "is", "in", "Belgium", "."], ["Bob", "lives", "there", "."]],
           "vertexSet": [[{"name": "Ghent"}], [{"name": "Belgium"}], [{"name": "Bob"}]],
           "labels": [{"r": "P17", "h": 0, "t": 1}, {"r": "P551", "h": 2, "t": 0}]}
    (raw / "redocred-train_revised.json").write_text(json.dumps([doc]))
    items = load_redocred()
    assert len(RELATIONS) == 96 and all(len(it.options) == 96 for it in items)
    pair = next(it for it in items if "«Ghent» to «Belgium»" in it.question)
    assert [pair.options[g] for g in pair.gold] == ["country"]
    assert any(not it.gold and " to " in it.question for it in items)  # an unrelated pair: empty answer


def test_dbpedia_entity_two_grades(raw):
    from bzaf.data.dbpedia_entity import load_dbpedia_entity

    (raw / "dbpedia-entity-queries-v2.txt").write_text("q1\tvietnam war movie\n")
    (raw / "dbpedia-entity-qrels-v2.txt").write_text(
        "q1\tQ0\t<dbpedia:Platoon_(film)>\t2\nq1\tQ0\t<dbpedia:Hamburger_Hill>\t1\nq1\tQ0\t<dbpedia:Paris>\t0\n")
    items = {it.id.split(":")[-1]: it for it in load_dbpedia_entity()}
    assert sorted(items["relevant"].options[g] for g in items["relevant"].gold) == ["Hamburger Hill", "Platoon (film)"]
    assert "Hamburger Hill" not in items["highly"].options and items["highly"].gold == [0]


def test_wands_exact_and_partial(raw):
    from bzaf.data.wands import load_wands

    (raw / "wands-product.csv").write_text("product_id\tproduct_name\tproduct_class\n1\toak bed\tBeds\n2\tpine bed\tBeds\n3\tlamp\tLamps\n")
    (raw / "wands-query.csv").write_text("query_id\tquery\tquery_class\n0\toak bed\tBeds\n")
    (raw / "wands-label.csv").write_text("id\tquery_id\tproduct_id\tlabel\n0\t0\t1\tExact\n1\t0\t2\tPartial\n2\t0\t3\tIrrelevant\n")
    items = {it.id.split(":")[-1]: it for it in load_wands()}
    assert items["exact"].options == ["oak bed", "lamp"] and items["exact"].gold == [0]
    assert items["partial"].gold == [0, 1] and items["partial"].meta["descriptions"][0] == "Beds"


def test_esci_three_questions(raw):
    pd = pytest.importorskip("pandas")
    from bzaf.data.esci import load_esci

    pd.DataFrame({"query_id": [7, 7, 7, 7], "query": ["usb cable"] * 4, "product_id": ["a", "b", "c", "d"],
                  "product_locale": ["us"] * 4, "esci_label": ["E", "S", "C", "I"], "split": ["train"] * 4}
                 ).to_parquet(raw / "esci-examples.parquet")
    pd.DataFrame({"product_id": ["a", "b", "c", "d"], "product_title": ["USB-C cable", "USB-A cable", "Charger", "Sock"],
                  "product_locale": ["us"] * 4}).to_parquet(raw / "esci-products.parquet")
    items = {it.id.split(":")[-1]: it for it in load_esci()}
    pick = {k: sorted(it.options[g] for g in it.gold) for k, it in items.items()}
    assert pick == {"exact": ["USB-C cable"], "acceptable": ["USB-A cable", "USB-C cable"], "complement": ["Charger"]}


def _qampari_zip(raw, n_questions=4):
    rows = []
    for q in range(n_questions):
        who = f"Person{q}"
        rows.append({"qid": f"{q}__wikidata_simple__train", "question_text": f"Which film had {who} as director?",
                     "entities": [{"entity_text": who}],
                     "answer_list": [{"answer_text": f"Film {q}-{a}", "proof": [{"proof_text": f"Film {q}-{a} is a film directed by {who.lower()}."}]}
                                     for a in range(3)]})
    rows.append({"qid": "x", "question_text": "What are the dates of films by Person0?", "entities": [{"entity_text": "Person0"}],
                 "answer_list": [{"answer_text": "1999", "proof": [{"proof_text": "A film by person0, released long ago."}]}]})
    with zipfile.ZipFile(raw / "qampari.zip", "w") as z:
        z.writestr("qampari_data/train_data.jsonl", "\n".join(json.dumps(r) for r in rows))


def test_qampari_distractors_come_from_sibling_questions(raw):
    from bzaf.data.qampari import QampariPool, load_qampari_questions

    _qampari_zip(raw)
    qs = load_qampari_questions()
    assert len(qs) == 4  # the numeric-answer question is dropped
    pool = QampariPool(qs)
    it = pool.draw(0, random.Random(0), 2, 5)
    gold = {it.options[g] for g in it.gold}
    assert len(it.options) == 5 and len(gold) == 2 and all(o.startswith("Film 0-") for o in gold)
    assert all(not o.startswith("Film 0-") for i, o in enumerate(it.options) if i not in it.gold)
    assert all(f"- {o}: " in it.state for o in it.options)  # every option has its fact


def test_count_buckets_and_option_draws():
    from bzaf.train.mix import draw_count, draw_options

    rng = random.Random(0)
    counts = Counter(draw_count(rng, 40) for _ in range(20000))
    assert abs(counts[0] / 20000 - 0.25) < 0.02 and abs(sum(v for k, v in counts.items() if k >= 5) / 20000 - 0.33) < 0.02
    assert max(counts) == 32 and max(draw_count(rng, 3) for _ in range(1000)) == 3
    ks = [draw_options(rng, 2, 100, 4, 80) for _ in range(5000)]
    assert min(ks) == 4 and max(ks) == 80 and draw_options(rng, 0, 1, 2, 8) is None


def test_build_e02b_offline(tmp_path):
    from bzaf.train.mix import Source, build_e02b

    many = [Item(f"m{i}", "many", f"text {i}", "Which apply?", [f"o{j}" for j in range(40)], list(range(i % 30)))
            for i in range(300)]
    few = [Item(f"f{i}", "few", f"note {i}", "Which apply?", ["a", "b", "c", "d"], [i % 4]) for i in range(100)]
    leaked = "this exact sentence of thirteen words or more also appears in the benchmark file today"
    bench = tmp_path / "bench"
    write_items([Item("b0", "x", f"prefix {leaked} suffix", "q", ["a", "b"], [0])], bench / "x.jsonl")
    few.append(Item("leak", "few", leaked, "Which apply?", ["a", "b", "c", "d"], [0]))
    sources = {"many": Source(400, (4, 40), lambda: many), "few": Source(200, (2, 4), lambda: few)}
    yn = [Item(f"b{i}", "boolq", f"passage {i}", "Is it?", ["no", "yes"], [i % 2], {"qtype": "noul"}) for i in range(30)]
    rows = build_e02b(0, {"boolq_distill": 20, "hellaswag_distill": 0, "sst5_distill": 0, "dbpedia_distill": 0}, bench,
                      sources=sources, distill_loaders={"boolq": lambda: yn}, stats_path=tmp_path / "s.json", log=lambda *_: None)
    sets = [r for r in rows if r.loss == "set"]
    assert len(sets) == 600 and sum(r.loss == "distill" for r in rows) == 20
    assert not any(r.state == leaked for r in rows)                      # 13-word overlap with the benchmark: dropped
    assert all(all(0 <= g < len(r.question["criteria"]) for g in r.gold) and len(r.gold) <= 32 for r in sets)
    many_counts = Counter(min(len(r.gold), 5) for r in sets if r.source == "many")
    assert 0.15 < many_counts[0] / 400 < 0.35 and many_counts[5] / 400 > 0.2  # counts follow the buckets, not the item
    assert Counter(r.id.rsplit("#", 1)[0] for r in sets).most_common(1)[0][1] <= 3
    stats = json.loads((tmp_path / "s.json").read_text())
    assert stats["set_rows"] == 600 and set(stats["per_source"]) == {"many", "few", "boolq_distill"}
