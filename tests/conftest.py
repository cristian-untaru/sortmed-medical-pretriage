"""Shared pytest fixtures for isolated storage and sample analysis data."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest


@pytest.fixture(autouse=True)
def clear_streamlit_caches():
    import streamlit as st

    try:
        st.cache_data.clear()
        st.cache_resource.clear()
    except Exception:
        pass


@pytest.fixture
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from backend import database

    monkeypatch.setenv("SORTMED_DISABLE_BROWSER_COOKIES", "1")
    database._db_initialized = False

    try:
        database.get_connection().close()
    except Exception as exc:
        pytest.skip(f"Supabase PostgreSQL is not configured for this test run: {exc}")

    return tmp_path


@pytest.fixture
def unique_email() -> str:
    return f"test_{uuid4().hex[:12]}@example.com"


@pytest.fixture
def sample_analysis() -> dict[str, Any]:
    return {
        "active_model_key": "lora-distilbert",
        "active_model_id": "cristian-untaru/lora-distilbert-medical-triage",
        "base_model_key": "distilbert",
        "model_method_key": "lora",
        "model_method_name": "LoRA",
        "result": "Self-monitor",
        "label": "self_monitor",
        "level": "warning",
        "confidence": 0.72,
        "confidence_message": "High confidence prediction",
        "confidence_level": "high",
        "confidence_margin": 0.31,
        "scores": {
            "self_monitor": 0.72,
            "consult_gp": 0.21,
            "urgent": 0.07,
        },
        "context": [
            {
                "focus": "Fatigue",
                "question": "What is (are) Fatigue?",
                "answer": "Fatigue is a feeling of tiredness or lack of energy.",
                "score": 0.64,
            }
        ],
        "symptoms": ["Fatigue"],
    }
