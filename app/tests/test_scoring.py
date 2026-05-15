from app.scoring import score_opportunity


def test_scoring_keywords():
    score, rec, _, _ = score_opportunity("Fusion electromagnet prototype with pulsed power supply")
    assert score > 40
    assert rec in {"Bid", "Review"}
