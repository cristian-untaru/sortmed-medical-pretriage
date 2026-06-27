"""Tests for model registry consistency and display metadata."""

from __future__ import annotations

from backend import model_config as cfg


def test_all_configured_models_are_registered() -> None:
    assert len(cfg.MODEL_METADATA) == 16
    assert len(cfg.ALL_MODEL_REGISTRY) == 16

    for method_key in cfg.MODEL_METHOD_OPTIONS:
        for base_key in cfg.BASE_MODEL_KEYS:
            model_key = cfg.build_model_key(method_key, base_key)
            assert model_key in cfg.MODEL_METADATA
            assert model_key in cfg.ALL_MODEL_REGISTRY


def test_peft_model_keys_map_back_to_their_base_model() -> None:
    assert cfg.get_model_base_key("lora-distilbert") == "distilbert"
    assert cfg.get_model_base_key("bottleneck-mlp-biobert") == "biobert"
    assert cfg.get_model_base_key("frozen-encoder-roberta") == "roberta"
    assert cfg.get_model_base_key("biomedbert") == "biomedbert"


def test_only_bottleneck_models_require_remote_code() -> None:
    assert cfg.model_requires_trust_remote_code("bottleneck-mlp-distilbert")
    assert cfg.model_requires_trust_remote_code("bottleneck-mlp-biomedbert")
    assert not cfg.model_requires_trust_remote_code("lora-distilbert")
    assert not cfg.model_requires_trust_remote_code("frozen-encoder-distilbert")
    assert not cfg.model_requires_trust_remote_code("distilbert")


def test_history_display_names_are_public_facing() -> None:
    assert cfg.get_model_history_display_name("distilbert") == "DistilBERT"
    assert cfg.get_model_history_display_name("lora-roberta") == "RoBERTa (LoRA)"
    assert (
        cfg.get_model_method_display_name("frozen-encoder-biobert")
        == "Frozen Encoder"
    )
