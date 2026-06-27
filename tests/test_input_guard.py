"""Regression tests for deterministic input guard rules and intent handling."""

from __future__ import annotations

import pytest

from backend.input_guard.models import InputGuardResult
from backend.input_guard.rules import validate_basic_input
from backend.input_guard.validator import validate_symptom_input


@pytest.mark.parametrize(
    ("text", "expected_reason"),
    [
        ("", "empty_input"),
        ("Hello", "not_enough_words"),
        ("Test", "not_enough_words"),
        ("head head head pain", "repeated_or_low_information_text"),
        ("head heads pain", "near_duplicate_terms"),
        ("head tac toe pain", "short_unrecognized_terms"),
        ("pain pain test", "repeated_or_low_information_text"),
        ("ma doare capul", "non_english_input"),
        ("me duele la cabeza", "non_english_input"),
        ("j'ai mal a la tete", "non_english_input"),
        ("head arms legs, body torso", "body_location_only_list"),
        ("arms lego, homework, study, medical", "random_medical_word_list"),
        ("homework medical attribute fever cosinus head", "random_medical_word_list"),
    ],
)
def test_basic_rules_reject_known_invalid_inputs(
    text: str,
    expected_reason: str,
) -> None:
    result = validate_basic_input(text)

    assert result is not None
    assert not result.allowed
    assert result.reason == expected_reason


@pytest.mark.parametrize(
    "text",
    [
        "I have a headache and dizziness since this morning.",
        "My chest hurts and I feel short of breath.",
        "I have abdominal pain and vomiting.",
        "I have fever and a sore throat since yesterday.",
    ],
)
def test_basic_rules_allow_clear_symptom_descriptions(text: str) -> None:
    assert validate_basic_input(text) is None


class FakeIntentPipeline:
    classes_ = [
        "symptom_description",
        "medication_request",
        "diagnosis_request",
        "general_medical_question",
        "non_medical",
    ]

    def __init__(self, probabilities: list[float]) -> None:
        self._probabilities = probabilities

    def predict_proba(self, texts: list[str]) -> list[list[float]]:
        return [self._probabilities]


def test_full_guard_accepts_symptom_intent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "backend.input_guard.validator.load_intent_classifier",
        lambda: (
            FakeIntentPipeline([0.81, 0.05, 0.04, 0.06, 0.04]),
            {"valid_intent_confidence_threshold": 0.25},
        ),
    )

    result = validate_symptom_input("I have a headache and dizziness since morning.")

    assert result.allowed
    assert result.reason == "valid_symptom_description"
    assert result.intent == "symptom_description"


def test_full_guard_prioritizes_specific_intent_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.input_guard.validator.load_intent_classifier",
        lambda: (
            FakeIntentPipeline([0.08, 0.78, 0.04, 0.05, 0.05]),
            {"confidence_threshold": 0.50},
        ),
    )

    result = validate_symptom_input(
        "Can you recommend a painkiller for my headache?"
    )

    assert not result.allowed
    assert result.reason == "rejected_intent:medication_request"
    assert "cannot recommend medication" in result.message


def test_full_guard_blocks_low_confidence_symptom_intent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.input_guard.validator.load_intent_classifier",
        lambda: (
            FakeIntentPipeline([0.24, 0.20, 0.18, 0.18, 0.20]),
            {"valid_intent_confidence_threshold": 0.25},
        ),
    )

    result = validate_symptom_input("I have strange symptoms in my body today.")

    assert not result.allowed
    assert result.reason == "low_symptom_intent_confidence"
    assert "Please describe your symptoms in English" in result.message
