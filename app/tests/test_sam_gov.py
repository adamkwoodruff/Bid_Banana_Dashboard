from app.sources.sam_gov import fetch_sam_opportunities


def test_sam_without_key_returns_empty(monkeypatch):
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    assert fetch_sam_opportunities() == []
