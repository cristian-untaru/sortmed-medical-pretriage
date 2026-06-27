"""Model loading and triage inference for SortMed."""

from __future__ import annotations

from typing import Any

import streamlit as st
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from backend.confidence import LABEL_LEVEL, assess_prediction_confidence
from backend.model_config import (
    ACTIVE_MODEL_KEY,
    LABEL_DISPLAY,
    MODEL_REGISTRY,
    get_model_base_key,
    get_model_method_key,
    get_model_method_short_name,
    model_requires_trust_remote_code,
)

def get_active_model_id(model_key: str | None = None) -> str | None:
    """
    Resolve the Hugging Face repository id for a configured model key.

    When no key is provided, the developer-selected ACTIVE_MODEL_KEY is used.
    Invalid keys return None so the caller can show a controlled error.
    """
    key = model_key if model_key is not None else ACTIVE_MODEL_KEY
    return MODEL_REGISTRY.get(key)


def get_model_status(model_key: str | None = None) -> dict[str, Any]:
    """
    Validate the selected model configuration before inference.

    The UI uses this status to display the active model and to avoid running
    analysis when the configured model key is not present in MODEL_REGISTRY.
    """
    resolved_key = model_key if model_key is not None else ACTIVE_MODEL_KEY
    model_id = get_active_model_id(resolved_key)

    if model_id is None:
        available_models = ", ".join(MODEL_REGISTRY.keys()) or "none"

        return {
            "ok": False,
            "active_key": resolved_key,
            "model_id": None,
            "message": (
                f"Invalid model key='{resolved_key}'. "
                f"Available models: {available_models}. "
                "Update ACTIVE_MODEL_KEY in backend/predictor.py."
            ),
        }

    return {
        "ok": True,
        "active_key": resolved_key,
        "model_id": model_id,
        "base_model_key": get_model_base_key(resolved_key),
        "model_method_key": get_model_method_key(resolved_key),
        "model_method_name": get_model_method_short_name(resolved_key),
        "message": f"Active model: {resolved_key} ({model_id})",
    }


# Cached model loading. Each selected model key gets its own cache entry.

@st.cache_resource(show_spinner="Loading AI model from Hugging Face...")
def load_model(model_key: str) -> tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """
    Load the selected Hugging Face model and tokenizer for inference.

    Streamlit caches this function by model_key, so switching between models
    downloads each checkpoint only once per running app process.
    """
    model_status = get_model_status(model_key)

    if not model_status["ok"]:
        raise ValueError(model_status["message"])

    model_id = model_status["model_id"]
    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id,
        trust_remote_code=model_requires_trust_remote_code(model_key),
    )

    model.to(device)
    model.eval()

    return model, tokenizer

def predict(
    text: str,
    model: AutoModelForSequenceClassification,
    tokenizer: AutoTokenizer,
    max_length: int = 128,
) -> dict[str, Any]:
    """
    Run triage inference for the current symptom description.

    The returned dictionary contains the predicted label, confidence score,
    per-class probabilities, display label, UI level, and confidence metadata.
    """
    device = next(model.parameters()).device

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=max_length,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=-1).squeeze().cpu().tolist()

    # Use the label mapping stored in the exported model configuration.
    id2label = model.config.id2label

    scores = {
        id2label.get(i, id2label.get(str(i), f"LABEL_{i}")): round(probs[i], 4)
        for i in range(len(probs))
    }

    pred_label = max(scores, key=scores.get)
    confidence = scores[pred_label]

    confidence_assessment = assess_prediction_confidence(scores)

    return {
        "label": pred_label,
        "confidence": confidence,
        "scores": scores,
        "display_label": LABEL_DISPLAY.get(pred_label, pred_label),
        "level": LABEL_LEVEL.get(pred_label, "info"),
        "confidence_level": confidence_assessment["level"],
        "confidence_message": confidence_assessment["message"],
        "confidence_margin": confidence_assessment["margin"],
    }
