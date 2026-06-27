"""Tests for prediction orchestration and MedQuAD context retrieval."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import torch

from backend import predictor


def test_model_status_accepts_registered_models() -> None:
    status = predictor.get_model_status("bottleneck-mlp-distilbert")

    assert status["ok"]
    assert status["active_key"] == "bottleneck-mlp-distilbert"
    assert status["base_model_key"] == "distilbert"
    assert status["model_method_key"] == "bottleneck_mlp"


def test_model_status_rejects_unknown_models() -> None:
    status = predictor.get_model_status("unknown-model")

    assert not status["ok"]
    assert status["model_id"] is None
    assert "Invalid model key" in status["message"]


@pytest.mark.parametrize(
    ("scores", "expected_level"),
    [
        ({"urgent": 0.70, "consult_gp": 0.20, "self_monitor": 0.10}, "high"),
        ({"urgent": 0.44, "consult_gp": 0.35, "self_monitor": 0.21}, "medium"),
        ({"urgent": 0.37, "consult_gp": 0.36, "self_monitor": 0.27}, "low"),
    ],
)
def test_confidence_assessment_uses_probability_and_margin(
    scores: dict[str, float],
    expected_level: str,
) -> None:
    result = predictor.assess_prediction_confidence(scores)

    assert result["level"] == expected_level
    assert "prediction" in result["message"].lower()


class FakeTokenizer:
    def __call__(self, text: str, **kwargs):
        return {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]]),
        }


class FakeModel:
    config = SimpleNamespace(
        id2label={
            0: "self_monitor",
            1: "consult_gp",
            2: "urgent",
        }
    )

    def parameters(self):
        yield torch.zeros(1)

    def __call__(self, **inputs):
        return SimpleNamespace(logits=torch.tensor([[0.2, 0.5, 2.0]]))


def test_predict_maps_logits_to_triage_labels() -> None:
    result = predictor.predict(
        "I have chest pain.",
        model=FakeModel(),
        tokenizer=FakeTokenizer(),
    )

    assert result["label"] == "urgent"
    assert result["display_label"] == "Urgent"
    assert result["confidence"] == result["scores"]["urgent"]
    assert set(result["scores"]) == {"self_monitor", "consult_gp", "urgent"}


class FakeEmbeddingModel:
    def encode(self, texts, **kwargs):
        return np.array([[1.0, 0.0]], dtype=np.float32)


def test_medquad_retrieval_filters_by_semantic_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    medquad_df = pd.DataFrame(
        [
            {
                "focus": "Headache",
                "question": "What is (are) Headache?",
                "answer": "Headache is pain in the head.",
                "retrieval_text": "headache pain head",
            },
            {
                "focus": "Unrelated",
                "question": "What is unrelated?",
                "answer": "Unrelated answer.",
                "retrieval_text": "unrelated text",
            },
        ]
    )
    embeddings = np.array(
        [
            [0.82, 0.57],
            [0.30, 0.95],
        ],
        dtype=np.float32,
    )

    monkeypatch.setattr(
        predictor,
        "load_medquad_semantic_index",
        lambda row_count: embeddings,
    )
    monkeypatch.setattr(
        predictor,
        "load_medquad_embedding_model",
        lambda: FakeEmbeddingModel(),
    )

    results = predictor.retrieve_medquad_context(
        "I have a headache today.",
        medquad_df,
        top_k=3,
    )

    assert len(results) == 1
    assert results[0]["focus"] == "Headache"
    assert results[0]["score"] == 0.82


def test_medquad_retrieval_suppresses_sensitive_terms_when_not_mentioned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    medquad_df = pd.DataFrame(
        [
            {
                "focus": "Cancer",
                "question": "What is cancer?",
                "answer": "Sensitive answer.",
                "retrieval_text": "cancer tumor",
            },
            {
                "focus": "Fatigue",
                "question": "What is fatigue?",
                "answer": "Fatigue is tiredness.",
                "retrieval_text": "fatigue tired",
            },
        ]
    )
    embeddings = np.array(
        [
            [0.62, 0.78],
            [0.60, 0.80],
        ],
        dtype=np.float32,
    )

    monkeypatch.setattr(
        predictor,
        "load_medquad_semantic_index",
        lambda row_count: embeddings,
    )
    monkeypatch.setattr(
        predictor,
        "load_medquad_embedding_model",
        lambda: FakeEmbeddingModel(),
    )

    results = predictor.retrieve_medquad_context(
        "I feel tired today.",
        medquad_df,
        top_k=3,
    )

    assert [item["focus"] for item in results] == ["Fatigue"]
