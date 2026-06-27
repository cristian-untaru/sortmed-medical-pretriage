"""Facade for model inference and MedQuAD retrieval."""

from __future__ import annotations

from typing import Any

from backend.model_config import ACTIVE_MODEL_KEY
from backend.confidence import assess_prediction_confidence
from backend.model_inference import (
    get_active_model_id,
    get_model_status,
    load_model,
    predict,
)
from backend import medquad_retrieval as _medquad
from backend.medquad_retrieval import (
    load_medquad,
    load_medquad_embedding_model,
    load_medquad_reranker,
    load_medquad_semantic_index,
)


def retrieve_medquad_context(user_text: str, medquad_df, top_k: int = 3) -> list[dict[str, Any]]:
    # Keep old monkeypatch points on backend.predictor working in tests.
    _medquad.load_medquad_embedding_model = load_medquad_embedding_model
    _medquad.load_medquad_semantic_index = load_medquad_semantic_index
    _medquad.load_medquad_reranker = load_medquad_reranker
    return _medquad.retrieve_medquad_context(user_text, medquad_df, top_k=top_k)


def run_full_analysis(user_text: str, model_key: str | None = None) -> dict[str, Any]:
    resolved_key = model_key if model_key is not None else ACTIVE_MODEL_KEY

    model, tokenizer = load_model(resolved_key)
    medquad_df = load_medquad()

    triage = predict(user_text, model, tokenizer)
    context = retrieve_medquad_context(user_text, medquad_df, top_k=3)

    model_status = get_model_status(resolved_key)

    return {
        "active_model_key": model_status["active_key"],
        "active_model_id": model_status["model_id"],
        "base_model_key": model_status["base_model_key"],
        "model_method_key": model_status["model_method_key"],
        "model_method_name": model_status["model_method_name"],
        "result": triage["display_label"],
        "label": triage["label"],
        "level": triage["level"],
        "confidence": triage["confidence"],
        "confidence_message": triage["confidence_message"],
        "confidence_level": triage["confidence_level"],
        "confidence_margin": triage["confidence_margin"],
        "scores": triage["scores"],
        "context": context,
        "symptoms": [c["focus"] for c in context] if context else ["N/A"],
    }


__all__ = [
    "assess_prediction_confidence",
    "get_active_model_id",
    "get_model_status",
    "load_medquad",
    "load_medquad_embedding_model",
    "load_medquad_reranker",
    "load_medquad_semantic_index",
    "load_model",
    "predict",
    "retrieve_medquad_context",
    "run_full_analysis",
]
