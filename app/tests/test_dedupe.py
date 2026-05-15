from app.dedupe import make_dedupe_key


def test_dedupe_stable():
    k1 = make_dedupe_key("Electromagnet System", "DOE", "2026-01-01")
    k2 = make_dedupe_key("Electromagnet System!", "DOE", "2026-01-01")
    assert k1 == k2
