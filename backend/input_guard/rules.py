"""Deterministic rules that run before the intent classifier."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Callable

from backend.input_guard.config import (
    MAX_INPUT_CHARS,
    MAX_REPEATED_WORD_SHARE,
    MIN_ALPHA_CHARS,
    MIN_UNIQUE_WORD_COUNT,
    MIN_WORD_COUNT,
    NEAR_DUPLICATE_SIMILARITY,
    SHORT_INPUT_WORD_LIMIT,
)
from backend.input_guard.lexicons import (
    BODY_LOCATION_TERMS,
    GIBBERISH_MARKERS,
    JOINED_MEDICAL_TERMS,
    LEET_TRANSLATION,
    NON_ENGLISH_MARKERS,
    ROMANIAN_DIACRITICS,
    SHORT_INPUT_ALLOWED_TERMS,
    SYMPTOM_CONTEXT_TERMS,
    SYMPTOM_SIGNAL_TERMS,
)
from backend.input_guard.models import InputGuardResult
from backend.input_guard.patterns import (
    ADVICE_OR_RISK_QUESTION_PATTERNS,
    CODE_LIKE_PATTERNS,
    CODE_SWITCH_PATTERNS,
    FUTURE_OR_PREVENTIVE_PATTERNS,
    HYPOTHETICAL_CASE_PATTERNS,
    INDIRECT_DIAGNOSIS_PATTERNS,
    META_COMMAND_TERMS,
    META_INSTRUCTION_PATTERNS,
    NEGATED_SYMPTOM_PATTERNS,
    NON_PATIENT_CONTEXT_PATTERNS,
    NO_SYMPTOMS_PATTERNS,
    REMOTE_HISTORY_PATTERNS,
    RESOLVED_SYMPTOMS_PATTERNS,
    SPACED_MEDICAL_TERM_PATTERNS,
    TEXT_REFERENCE_PATTERNS,
    TREATMENT_REQUEST_PATTERNS,
    WRITING_TASK_PATTERNS,
)
from backend.input_guard.text_utils import (
    canonical_word,
    content_words,
    matches_any_pattern,
    strip_accents,
    tokenize,
)

RuleCheck = Callable[[str, list[str]], bool]


# Stores a guard rule together with the rejection shown to the user.
@dataclass(frozen=True)
class InputRule:
    reason: str
    message: str
    check: RuleCheck

    # Converts a matched rule into the common InputGuardResult shape.
    def evaluate(self, text: str, words: list[str]) -> InputGuardResult | None:
        if not self.check(text, words):
            return None

        return InputGuardResult(
            allowed=False,
            message=self.message,
            reason=self.reason,
        )


# Counts symptom and body-location words in a token list.
def _medical_term_count(words: list[str]) -> int:
    return sum(
        1
        for word in words
        if word in SYMPTOM_SIGNAL_TERMS or word in BODY_LOCATION_TERMS
    )


# Flags obvious non-English symptom descriptions before model inference.
def _looks_non_english(text: str, words: list[str]) -> bool:
    if any(ch in ROMANIAN_DIACRITICS for ch in text):
        return True

    if not words:
        return False

    folded_tokens = {strip_accents(token) for token in words}
    markers = (folded_tokens | set(words)) & NON_ENGLISH_MARKERS

    return len(markers) >= 2


# Catches short inputs that have no symptom signal at all.
def _looks_like_short_low_information_text(text: str, words: list[str]) -> bool:
    if len(words) > SHORT_INPUT_WORD_LIMIT:
        return False

    return not any(word in SYMPTOM_SIGNAL_TERMS for word in words)


# Detects repeated or slightly altered words such as head/heads.
def _has_near_duplicate_content_words(text: str, words: list[str]) -> bool:
    relevant_words = content_words(words)

    for index, word in enumerate(relevant_words):
        if len(word) < 3:
            continue

        canonical = canonical_word(word)
        for other_word in relevant_words[index + 1:]:
            if len(other_word) < 3:
                continue

            if canonical == canonical_word(other_word):
                return True

            similarity = SequenceMatcher(None, word, other_word).ratio()
            if similarity >= NEAR_DUPLICATE_SIMILARITY:
                return True

    return False


# Rejects very short symptom-looking text padded with unrelated words.
def _has_unrecognized_short_terms(text: str, words: list[str]) -> bool:
    if len(words) > SHORT_INPUT_WORD_LIMIT:
        return False

    return any(
        word not in SHORT_INPUT_ALLOWED_TERMS
        for word in content_words(words)
    )


# Catches prompts that try to instruct the model instead of describing symptoms.
def _looks_like_meta_instruction_text(text: str, words: list[str]) -> bool:
    if matches_any_pattern(text, META_INSTRUCTION_PATTERNS):
        return True

    command_term_count = sum(1 for word in words if word in META_COMMAND_TERMS)
    return command_term_count >= 2


# Identifies requests for medicines or treatment steps.
def _looks_like_treatment_request(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, TREATMENT_REQUEST_PATTERNS)


# Identifies questions about urgency, risk, or whether to see a doctor.
def _looks_like_advice_or_risk_question(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, ADVICE_OR_RISK_QUESTION_PATTERNS)


# Catches texts that discuss medical words rather than current symptoms.
def _looks_like_text_reference_or_example(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, TEXT_REFERENCE_PATTERNS)


# Rejects writing, translation, quiz, and summary tasks containing medical terms.
def _looks_like_writing_or_translation_task(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, WRITING_TASK_PATTERNS)


# Rejects sample patients, roleplay, and hypothetical medical scenarios.
def _looks_like_hypothetical_case_text(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, HYPOTHETICAL_CASE_PATTERNS)


# Detects inputs that explicitly say there are no current symptoms.
def _looks_like_no_symptoms_text(text: str, words: list[str]) -> bool:
    if matches_any_pattern(text, NO_SYMPTOMS_PATTERNS):
        return True

    no_count = sum(1 for word in words if word == "no")
    return no_count >= 2 and _medical_term_count(words) >= 2


# Allows "I do not have fever, but I have chest pain" to remain valid.
def _has_positive_symptom_contrast(text: str) -> bool:
    contrast_parts = re.split(r"\b(?:but|however|though)\b", text.lower(), maxsplit=1)
    if len(contrast_parts) < 2:
        return False

    contrast_words = tokenize(contrast_parts[1])
    if _medical_term_count(contrast_words) == 0:
        return False

    return re.search(
        r"\b(i\s+)?(have|feel|am|i'm|im|experience|experiencing|got|getting)\b",
        contrast_parts[1],
    ) is not None


# Blocks negated symptoms unless the sentence later states a real symptom.
def _looks_like_negated_symptom_text(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    if _has_positive_symptom_contrast(text):
        return False

    return matches_any_pattern(text, NEGATED_SYMPTOM_PATTERNS)


# Rejects non-human, fictional, vehicle, or software contexts.
def _looks_like_non_patient_context(text: str, words: list[str]) -> bool:
    return matches_any_pattern(text, NON_PATIENT_CONTEXT_PATTERNS)


# Catches symptoms described as already resolved.
def _looks_like_resolved_past_symptoms(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, RESOLVED_SYMPTOMS_PATTERNS)


# Catches distant medical history that is not a current symptom.
def _looks_like_remote_history_text(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, REMOTE_HISTORY_PATTERNS)


# Blocks prevention questions and possible future symptoms.
def _looks_like_future_or_preventive_text(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, FUTURE_OR_PREVENTIVE_PATTERNS)


# Rejects diagnosis questions phrased through symptoms.
def _looks_like_indirect_diagnosis_question(text: str, words: list[str]) -> bool:
    return matches_any_pattern(text, INDIRECT_DIAGNOSIS_PATTERNS)


# Rejects code, API calls, markup, or structured payloads.
def _looks_like_code_or_structured_text(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0 and not any(
        word in {"urgent", "triage"} for word in words
    ):
        return False

    return matches_any_pattern(text, CODE_LIKE_PATTERNS)


# Catches obvious mixed-language symptom text.
def _looks_like_code_switching_text(text: str, words: list[str]) -> bool:
    if _medical_term_count(words) == 0:
        return False

    return matches_any_pattern(text, CODE_SWITCH_PATTERNS)


# Rejects split, leetspeak, joined, or distorted medical terms.
def _looks_like_obfuscated_medical_text(text: str, words: list[str]) -> bool:
    lower_text = text.lower()

    if matches_any_pattern(lower_text, SPACED_MEDICAL_TERM_PATTERNS):
        return True

    raw_tokens = re.findall(r"[a-z0-9]+", lower_text)
    leet_medical_count = 0
    for token in raw_tokens:
        if not any(char.isdigit() for char in token):
            continue
        translated = token.translate(LEET_TRANSLATION)
        if translated in SYMPTOM_SIGNAL_TERMS or translated in BODY_LOCATION_TERMS:
            leet_medical_count += 1

    if leet_medical_count >= 2:
        return True

    relevant_words = content_words(words)
    joined_medical_count = sum(
        1 for word in relevant_words if word in JOINED_MEDICAL_TERMS
    )

    medical_terms = {
        term
        for term in (SYMPTOM_SIGNAL_TERMS | BODY_LOCATION_TERMS)
        if len(term) >= 4
    }
    distorted_count = 0
    for word in relevant_words:
        if len(word) < 4 or word in medical_terms:
            continue

        collapsed = re.sub(r"(.)\1{1,}", r"\1", word)
        candidates = {word, collapsed}
        for candidate in candidates:
            if any(
                abs(len(candidate) - len(term)) <= 3
                and SequenceMatcher(None, candidate, term).ratio() >= 0.84
                for term in medical_terms
            ):
                distorted_count += 1
                break

    return joined_medical_count > 0 or distorted_count >= 2


# Checks known filler words when they appear beside medical terms.
def _has_gibberish_markers(text: str, words: list[str]) -> bool:
    return bool(set(words) & GIBBERISH_MARKERS)


# Blocks compact symptom lists that use punctuation separators.
def _looks_like_bare_symptom_word_list(text: str, words: list[str]) -> bool:
    relevant_words = content_words(words)
    if not 3 <= len(relevant_words) <= SHORT_INPUT_WORD_LIMIT:
        return False

    if any(word in BODY_LOCATION_TERMS for word in relevant_words):
        return False

    if any(word in SYMPTOM_CONTEXT_TERMS for word in relevant_words):
        return False

    has_list_separator = re.search(r"[,/+_-]", text) is not None
    return (
        has_list_separator
        and all(word in SYMPTOM_SIGNAL_TERMS for word in relevant_words)
    )


# Blocks short symptom-only sequences without sentence structure.
def _looks_like_bare_symptom_word_sequence(text: str, words: list[str]) -> bool:
    relevant_words = content_words(words)
    if not 3 <= len(relevant_words) <= 5:
        return False

    if "and" in words:
        return False

    if any(word in SYMPTOM_CONTEXT_TERMS for word in relevant_words):
        return False

    return all(
        word in SYMPTOM_SIGNAL_TERMS or word in BODY_LOCATION_TERMS
        for word in relevant_words
    )


# Rejects lists of body locations without any actual symptom.
def _looks_like_body_location_only_list(text: str, words: list[str]) -> bool:
    relevant_words = content_words(words)
    if len(relevant_words) < 3:
        return False

    if any(word in SYMPTOM_SIGNAL_TERMS for word in relevant_words):
        return False

    body_location_count = sum(
        1 for word in relevant_words if word in BODY_LOCATION_TERMS
    )
    return body_location_count >= 3 and body_location_count == len(relevant_words)


# Blocks random word lists padded with one or more medical/body terms.
def _looks_like_random_medical_word_list(text: str, words: list[str]) -> bool:
    if _has_positive_symptom_contrast(text):
        return False

    relevant_words = content_words(words)
    if len(relevant_words) < 4:
        return False

    medical_term_count = _medical_term_count(relevant_words)
    if medical_term_count == 0:
        return False

    symptom_signal_count = sum(
        1 for word in relevant_words if word in SYMPTOM_SIGNAL_TERMS
    )
    context_count = sum(1 for word in words if word in SYMPTOM_CONTEXT_TERMS)
    unrelated_count = sum(
        1
        for word in relevant_words
        if (
            word not in SYMPTOM_SIGNAL_TERMS
            and word not in BODY_LOCATION_TERMS
            and word not in SYMPTOM_CONTEXT_TERMS
        )
    )
    has_list_separator = re.search(r"[,;/+]", text) is not None

    if unrelated_count < 2:
        return False

    if has_list_separator:
        return True

    if context_count == 0:
        return True

    return symptom_signal_count == 0 and unrelated_count >= 3


# Rejects short inputs wrapped in punctuation or symbol noise.
def _has_excessive_symbol_noise(text: str, words: list[str]) -> bool:
    if len(words) > SHORT_INPUT_WORD_LIMIT:
        return False

    symbols = [
        char for char in text
        if not char.isalnum() and not char.isspace() and char not in {"'", "-"}
    ]
    symbol_share = len(symbols) / max(len(text), 1)

    return (
        (len(symbols) >= 6 and symbol_share >= 0.20)
        or re.search(r"[!?.,:;#@$%^&*]{3,}", text) is not None
    )


SEMANTIC_RULES = (
    InputRule(
        "code_like_input",
        "Please describe your symptoms in plain English, not code, commands, "
        "markup, or structured data.",
        _looks_like_code_or_structured_text,
    ),
    InputRule(
        "obfuscated_medical_text",
        "Please describe your symptoms using normal English spelling, without "
        "obfuscated or split-up medical words.",
        _looks_like_obfuscated_medical_text,
    ),
    InputRule(
        "meta_instruction_input",
        "Please describe your symptoms in English instead of giving instructions "
        "to the app or model.",
        _looks_like_meta_instruction_text,
    ),
    InputRule(
        "treatment_request",
        "SortMed cannot recommend medication or treatment. Please describe your "
        "symptoms in English without asking how to treat them or what medicine to take.",
        _looks_like_treatment_request,
    ),
    InputRule(
        "advice_or_risk_question",
        "SortMed is designed for direct symptom descriptions, not questions about "
        "risk, urgency, or whether you need a doctor.",
        _looks_like_advice_or_risk_question,
    ),
    InputRule(
        "writing_or_translation_task",
        "SortMed cannot complete writing, translation, quiz, or summary tasks. "
        "Please describe symptoms directly in English.",
        _looks_like_writing_or_translation_task,
    ),
    InputRule(
        "hypothetical_case_text",
        "Please enter a real symptom description, not a hypothetical, sample, "
        "or case-study scenario.",
        _looks_like_hypothetical_case_text,
    ),
    InputRule(
        "medical_word_reference_text",
        "Please describe symptoms you are experiencing, not example medical words "
        "or test tokens.",
        _looks_like_text_reference_or_example,
    ),
    InputRule(
        "future_or_preventive_text",
        "SortMed is intended for symptoms you are currently feeling, not possible "
        "future symptoms or prevention questions.",
        _looks_like_future_or_preventive_text,
    ),
    InputRule(
        "resolved_past_symptoms",
        "SortMed is intended for current symptoms. Please enter what you are "
        "feeling now if symptoms are present.",
        _looks_like_resolved_past_symptoms,
    ),
    InputRule(
        "remote_history_text",
        "SortMed is intended for current symptoms. Please enter what you are "
        "feeling now, not symptoms from the distant past.",
        _looks_like_remote_history_text,
    ),
    InputRule(
        "negated_symptom_text",
        "SortMed can only analyze symptoms that are currently present. Please "
        "describe what you are feeling if you have symptoms.",
        _looks_like_negated_symptom_text,
    ),
    InputRule(
        "no_symptoms_input",
        "SortMed can only analyze current symptom descriptions. Please enter what "
        "you are feeling if you have symptoms.",
        _looks_like_no_symptoms_text,
    ),
    InputRule(
        "non_patient_context",
        "Please enter a real human symptom description, not animal, vehicle, "
        "fictional, or story text.",
        _looks_like_non_patient_context,
    ),
    InputRule(
        "indirect_diagnosis_question",
        "SortMed cannot identify a condition from a question. Please describe "
        "symptoms directly in English.",
        _looks_like_indirect_diagnosis_question,
    ),
    InputRule(
        "gibberish_with_medical_terms",
        "Please describe your symptoms using clear English words, without random "
        "filler text.",
        lambda text, words: _has_gibberish_markers(text, words)
        and _medical_term_count(words) > 0,
    ),
    InputRule(
        "symbol_noise_input",
        "Please describe your symptoms using clear words, without extra symbols "
        "or punctuation noise.",
        _has_excessive_symbol_noise,
    ),
    InputRule(
        "non_english_input",
        "Please describe your symptoms in English. SortMed currently supports "
        "English symptom descriptions only.",
        _looks_non_english,
    ),
    InputRule(
        "mixed_language_input",
        "Please describe your symptoms fully in English. SortMed does not accept "
        "mixed-language symptom descriptions.",
        _looks_like_code_switching_text,
    ),
    InputRule(
        "body_location_only_list",
        "Please describe what you feel in those body areas, not only a list of "
        "body parts.",
        _looks_like_body_location_only_list,
    ),
    InputRule(
        "random_medical_word_list",
        "Please describe your symptoms as a clear sentence, not as random words "
        "mixed with medical terms.",
        _looks_like_random_medical_word_list,
    ),
    InputRule(
        "short_low_information_text",
        "Please describe your symptoms as a clear sentence, including what you "
        "feel and where it hurts.",
        _looks_like_short_low_information_text,
    ),
    InputRule(
        "bare_symptom_word_list",
        "Please describe your symptoms as a clear sentence, including what you "
        "feel and where it hurts.",
        _looks_like_bare_symptom_word_list,
    ),
    InputRule(
        "bare_symptom_word_sequence",
        "Please describe your symptoms as a clear sentence, not only as a list "
        "of symptom words.",
        _looks_like_bare_symptom_word_sequence,
    ),
    InputRule(
        "near_duplicate_terms",
        "Please describe your symptoms as a clear sentence in English, without "
        "repeating or slightly changing the same word.",
        _has_near_duplicate_content_words,
    ),
    InputRule(
        "short_unrecognized_terms",
        "Please describe your symptoms as a clear sentence, including what you "
        "feel and where it hurts.",
        _has_unrecognized_short_terms,
    ),
)


# Runs deterministic checks before the intent classifier is allowed to load.
def validate_basic_input(text: str) -> InputGuardResult | None:
    if not text:
        return InputGuardResult(
            allowed=False,
            message="Please enter your symptoms before continuing.",
            reason="empty_input",
        )

    if len(text) > MAX_INPUT_CHARS:
        return InputGuardResult(
            allowed=False,
            message=(
                "Please shorten your symptom description. Keep it under "
                f"{MAX_INPUT_CHARS} characters."
            ),
            reason="input_too_long",
        )

    alpha_chars = [char for char in text if char.isalpha()]
    if len(alpha_chars) < MIN_ALPHA_CHARS:
        return InputGuardResult(
            allowed=False,
            message="Please describe your symptoms in words.",
            reason="not_enough_text",
        )

    words = tokenize(text)
    if len(words) < MIN_WORD_COUNT:
        return InputGuardResult(
            allowed=False,
            message=(
                "Please describe your symptoms in English using at least a few "
                "words, including what you feel and where it hurts."
            ),
            reason="not_enough_words",
        )

    word_counts = {word: words.count(word) for word in set(words)}
    most_repeated_share = max(word_counts.values()) / len(words)
    if (
        len(word_counts) < MIN_UNIQUE_WORD_COUNT
        or most_repeated_share >= MAX_REPEATED_WORD_SHARE
    ):
        return InputGuardResult(
            allowed=False,
            message=(
                "Please describe your symptoms as a complete sentence in English, "
                "without repeating the same word."
            ),
            reason="repeated_or_low_information_text",
        )

    for rule in SEMANTIC_RULES:
        result = rule.evaluate(text, words)
        if result is not None:
            return result

    return None
