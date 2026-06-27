"""Hugging Face intent classifier loading for the input guard."""

from __future__ import annotations

import json
from typing import Any

import joblib
import streamlit as st
from huggingface_hub import hf_hub_download

from backend.model_config import (
    INTENT_CLASSIFIER_CONFIG_FILE,
    INTENT_CLASSIFIER_MODEL_FILE,
    INTENT_CLASSIFIER_REPO,
)


# Loads the small intent model once per Streamlit session.
@st.cache_resource(show_spinner="Loading input safety check...")
def load_intent_classifier() -> tuple[Any, dict[str, Any]]:
    model_path = hf_hub_download(
        repo_id=INTENT_CLASSIFIER_REPO,
        filename=INTENT_CLASSIFIER_MODEL_FILE,
    )
    config_path = hf_hub_download(
        repo_id=INTENT_CLASSIFIER_REPO,
        filename=INTENT_CLASSIFIER_CONFIG_FILE,
    )

    pipeline = joblib.load(model_path)
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    return pipeline, config
