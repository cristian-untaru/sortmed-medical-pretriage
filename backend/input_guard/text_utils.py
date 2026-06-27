"""Text normalization and token helpers for input guard rules."""

from __future__ import annotations

import re
import unicodedata

from backend.input_guard.lexicons import LOW_INFORMATION_STOPWORDS


# Collapses user input to the same form used by both rules and classifier.
def normalize_text(text: str) -> str:
    return " ".join(str(text or "").strip().split())


# Extracts word-like tokens while keeping contractions such as j'ai intact.
def tokenize(text: str) -> list[str]:
    return re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", text.lower())


# Removes accents so non-English marker checks can compare folded words.
def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


# Keeps the meaningful words after dropping very common filler terms.
def content_words(words: list[str]) -> list[str]:
    return [word for word in words if word not in LOW_INFORMATION_STOPWORDS]


# Normalizes simple plural endings for near-duplicate word checks.
def canonical_word(word: str) -> str:
    if word.endswith("'s"):
        word = word[:-2]
    if len(word) > 4 and word.endswith("ies"):
        return f"{word[:-3]}y"
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


# Tests a text against a tuple of regex patterns using a common lowercased form.
def matches_any_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    lower_text = text.lower()
    return any(re.search(pattern, lower_text) for pattern in patterns)
