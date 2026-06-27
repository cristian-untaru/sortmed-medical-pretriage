"""Tests for small UI formatting helpers."""

from __future__ import annotations

from ui.helpers import format_semantic_score


def test_semantic_scores_are_displayed_consistently() -> None:
    assert format_semantic_score(0.6152) == "0.62"
    assert format_semantic_score("0.5") == "0.50"
    assert format_semantic_score(None) == "N/A"
