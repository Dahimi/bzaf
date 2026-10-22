"""The bar-wording probe pairs (bzaf.data.bar_probe) on a stand-in source: same options, strict answer inside the loose
one, the two answers always differ, deterministic."""
from bzaf.data import bar_probe


def fake_judged():
    labs = ["Exact", "Partial", "Irrelevant"]
    return {f"q{n}": (f"query {n}", [(f"product {n}-{j}", "cls", labs[(n + j) % 3 if n % 2 else 0]) for j in range(10)])
            for n in range(40)}


def test_pairs(monkeypatch):
    monkeypatch.setitem(bar_probe.SOURCES, "fake", (fake_judged, "Search query: {}", ("Strict?", {"Exact"}),
                                                    ("Loose?", {"Exact", "Partial"})))
    items = bar_probe.load_bar_probe("fake", n=5)
    assert items == bar_probe.load_bar_probe("fake", n=5)
    assert len(items) == 10   # even queries have only Exact products, so the answers never differ: dropped
    for s, lo in zip(items[::2], items[1::2]):
        assert s.meta["bar"] == "strict" and lo.meta["bar"] == "loose" and s.options == lo.options
        assert s.question == "Strict?" and lo.question == "Loose?" and s.meta["descriptions"] == ["cls"] * 8
        assert set(s.gold) < set(lo.gold)
