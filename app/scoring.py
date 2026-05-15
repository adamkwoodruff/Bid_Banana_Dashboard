from typing import Tuple

PRIORITY_KEYWORDS = {
    "helmholtz": 15,
    "solenoid": 14,
    "electromagnet": 14,
    "magnetic field": 13,
    "pulsed power": 13,
    "dc power supply": 10,
    "ac power supply": 10,
    "high-voltage": 11,
    "high current": 11,
    "interlock": 9,
    "control systems": 9,
    "fusion": 14,
    "plasma": 13,
    "accelerator": 13,
    "scientific equipment": 10,
    "prototype": 12,
    "bespoke": 10,
}


def score_opportunity(text: str) -> Tuple[float, str, str, str]:
    lowered = (text or "").lower()
    score = 0
    matches = []
    for keyword, pts in PRIORITY_KEYWORDS.items():
        if keyword in lowered:
            score += pts
            matches.append(keyword)

    score = min(100, float(score))
    if score >= 45:
        rec = "Bid"
    elif score >= 25:
        rec = "Review"
    else:
        rec = "No Bid"

    why = f"Matched keywords: {', '.join(matches)}" if matches else "Limited overlap with target capabilities"
    risks = "May be out-of-scope if heavy civil/IT scope dominates." if score < 25 else "Validate delivery timeline, compliance, and manufacturing capacity."
    reqs = "Derived from title/description keyword extraction for MVP."
    return score, rec, why, risks
