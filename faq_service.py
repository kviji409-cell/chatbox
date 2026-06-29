"""
faq_service.py
Loads faq.json and uses rapidfuzz for fuzzy matching across
question and keywords fields. Handles typos, short forms,
and badly typed questions like "wat is ur timing".
"""

import json
import os
from rapidfuzz import fuzz, process

# Load FAQ data once at import time
_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "faq.json")

with open(_DATA_PATH, encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

# Build flat search corpus: searchable string → FAQ item
_CORPUS: list[tuple[str, dict]] = []

for item in FAQ_DATA:
    _CORPUS.append((item["question"].lower(), item))
    for kw in item.get("keywords", []):
        _CORPUS.append((kw.lower(), item))

_STRINGS = [pair[0] for pair in _CORPUS]

THRESHOLD = 60


def search_faq(user_message: str) -> dict:
    """
    Search FAQ corpus for the best fuzzy match.
    Returns match dict with found/answer/question/category/score
    or {"found": False}.
    """
    if not user_message or not user_message.strip():
        return {"found": False}

    query = user_message.strip().lower()

    result = process.extractOne(
        query,
        _STRINGS,
        scorer=fuzz.token_set_ratio,
        score_cutoff=THRESHOLD,
    )

    if result is None:
        return {"found": False}

    matched_string, score, index = result
    item = _CORPUS[index][1]

    return {
        "found":    True,
        "answer":   item["answer"],
        "question": item["question"],
        "category": item["category"],
        "score":    round(score, 2),
        "id":       item["id"],
    }