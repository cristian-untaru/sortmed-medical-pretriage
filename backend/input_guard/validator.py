"""Main input guard flow used by the Streamlit app."""

from __future__ import annotations

from backend.input_guard.config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_VALID_INTENT_CONFIDENCE_THRESHOLD,
    GENERIC_SYMPTOM_DESCRIPTION_MESSAGE,
    INTENT_MESSAGES,
)
from backend.input_guard.intent_classifier import load_intent_classifier
from backend.input_guard.models import InputGuardResult
from backend.input_guard.rules import validate_basic_input
from backend.input_guard.text_utils import normalize_text
from backend.model_config import VALID_INTENT


# Validates text first with rules, then with the trained intent classifier.
def validate_symptom_input(text: str) -> InputGuardResult:
    normalized_text = normalize_text(text)

    basic_error = validate_basic_input(normalized_text)
    if basic_error is not None:
        return basic_error

    try:
        pipeline, config = load_intent_classifier()
    except Exception as exc:
        return InputGuardResult(
            allowed=False,
            message=(
                "The input safety check is currently unavailable. Please try again "
                "in a moment."
            ),
            reason="intent_classifier_unavailable",
            scores={"error": str(exc)},
        )

    probabilities = pipeline.predict_proba([normalized_text])[0]
    classes = [str(class_name) for class_name in pipeline.classes_]
    best_index = max(range(len(probabilities)), key=lambda idx: probabilities[idx])
    intent = classes[best_index]
    confidence = float(probabilities[best_index])
    threshold = float(
        config.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
    )
    valid_intent_threshold = float(
        config.get(
            "valid_intent_confidence_threshold",
            DEFAULT_VALID_INTENT_CONFIDENCE_THRESHOLD,
        )
    )
    valid_intent = config.get("valid_intent", VALID_INTENT)
    scores = {
        class_name: round(float(probability), 4)
        for class_name, probability in zip(classes, probabilities)
    }

    if intent == valid_intent and confidence >= valid_intent_threshold:
        return InputGuardResult(
            allowed=True,
            intent=intent,
            confidence=round(confidence, 4),
            reason="valid_symptom_description",
            scores=scores,
        )

    if intent == valid_intent:
        return InputGuardResult(
            allowed=False,
            message=GENERIC_SYMPTOM_DESCRIPTION_MESSAGE,
            intent=intent,
            confidence=round(confidence, 4),
            reason="low_symptom_intent_confidence",
            scores=scores,
        )

    if intent in INTENT_MESSAGES:
        return InputGuardResult(
            allowed=False,
            message=INTENT_MESSAGES[intent],
            intent=intent,
            confidence=round(confidence, 4),
            reason=f"rejected_intent:{intent}",
            scores=scores,
        )

    if confidence < threshold:
        return InputGuardResult(
            allowed=False,
            message=GENERIC_SYMPTOM_DESCRIPTION_MESSAGE,
            intent=intent,
            confidence=round(confidence, 4),
            reason="low_intent_confidence",
            scores=scores,
        )

    return InputGuardResult(
        allowed=False,
        message=INTENT_MESSAGES.get(
            intent,
            "Please describe your symptoms in English before continuing.",
        ),
        intent=intent,
        confidence=round(confidence, 4),
        reason=f"rejected_intent:{intent}",
        scores=scores,
    )
