"""Constants and user-facing messages for the input guard."""

MIN_ALPHA_CHARS = 2
MIN_WORD_COUNT = 3
MIN_UNIQUE_WORD_COUNT = 2
MAX_REPEATED_WORD_SHARE = 0.50
NEAR_DUPLICATE_SIMILARITY = 0.86
SHORT_INPUT_WORD_LIMIT = 4
MAX_INPUT_CHARS = 1200
DEFAULT_CONFIDENCE_THRESHOLD = 0.50
DEFAULT_VALID_INTENT_CONFIDENCE_THRESHOLD = 0.25
INPUT_GUARD_RULE_VERSION = "2026-06-23-adversarial-rules-v10"

GENERIC_SYMPTOM_DESCRIPTION_MESSAGE = (
    "Please describe your symptoms in English, including what you feel, "
    "where it hurts, and how long it has been happening."
)

INTENT_MESSAGES = {
    "medication_request": (
        "SortMed cannot recommend medication or treatment. Please describe your "
        "symptoms in English without asking for a specific drug."
    ),
    "diagnosis_request": (
        "SortMed cannot diagnose a condition. Please describe what you are feeling "
        "in English, including symptoms, duration, and severity."
    ),
    "general_medical_question": (
        "SortMed is designed for symptom descriptions, not general medical questions. "
        "Please describe your symptoms in English."
    ),
    "non_medical": (
        "SortMed can only analyze symptom descriptions. Please enter your symptoms "
        "in English."
    ),
}
