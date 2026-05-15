import re


def make_dedupe_key(title: str, buyer: str = "", deadline: str = "") -> str:
    norm = re.sub(r"\W+", "", (title or "").lower())
    b = re.sub(r"\W+", "", (buyer or "").lower())
    d = re.sub(r"\W+", "", (deadline or "").lower())
    return f"{norm[:80]}|{b[:40]}|{d}"
