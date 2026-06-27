"""Prediction confidence interpretation for triage models."""

from __future__ import annotations

from typing import Any

LABEL_LEVEL = {
    "self_monitor": "warning",
    "consult_gp":   "success",
    "urgent":       "error",
}

# These thresholds are shared by all triage models that produce the same three
# labels. Confidence is the top class probability; margin is the gap between the
# two highest class probabilities.

HIGH_CONFIDENCE_THRESHOLD = 0.50
HIGH_MARGIN_THRESHOLD = 0.10

MEDIUM_CONFIDENCE_THRESHOLD = 0.40
MEDIUM_MARGIN_THRESHOLD = 0.05

def assess_prediction_confidence(scores: dict[str, float]) -> dict[str, Any]:
    """
    Interpret a prediction using both confidence and class-score margin.

    The returned level and message are used by the UI to indicate whether the
    model output is clear or should be treated as ambiguous.
    """
    if not scores:
        return {
            "level": "unknown",
            "message": "Confidence unavailable",
            "margin": 0.0,
        }

    sorted_scores = sorted(scores.values(), reverse=True)

    confidence = sorted_scores[0]
    second_best = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
    margin = confidence - second_best

    if confidence >= HIGH_CONFIDENCE_THRESHOLD and margin >= HIGH_MARGIN_THRESHOLD:
        level = "high"
        message = "High confidence prediction"
    elif confidence >= MEDIUM_CONFIDENCE_THRESHOLD and margin >= MEDIUM_MARGIN_THRESHOLD:
        level = "medium"
        message = "Medium confidence prediction - interpret with caution"
    else:
        level = "low"
        message = "Low confidence prediction - ambiguous result"

    return {
        "level": level,
        "message": message,
        "margin": round(margin, 4),
    }
