"""Central model configuration used by the Streamlit app and backend."""

from __future__ import annotations

ENABLE_PEFT_MODEL_SELECTION = True
USER_CAN_SELECT_MODEL = True
ACTIVE_MODEL_KEY = "biomedbert"

BASE_MODEL_KEYS: tuple[str, ...] = (
    "distilbert",
    "biobert",
    "roberta",
    "biomedbert",
)

BASE_MODEL_DISPLAY_NAMES: dict[str, str] = {
    "distilbert": "DistilBERT",
    "biobert": "BioBERT",
    "roberta": "RoBERTa",
    "biomedbert": "BioMedBERT",
}

MODEL_METHOD_DISPLAY_NAMES: dict[str, str] = {
    "full": "Full fine-tuning",
    "lora": "LoRA",
    "bottleneck_mlp": "Bottleneck MLP Adapter",
    "frozen_encoder": "Frozen Encoder",
}

MODEL_METHOD_SHORT_NAMES: dict[str, str] = {
    "full": "Full",
    "lora": "LoRA",
    "bottleneck_mlp": "Bottleneck MLP",
    "frozen_encoder": "Frozen Encoder",
}

MODEL_METHOD_OPTIONS: tuple[str, ...] = (
    "full",
    "lora",
    "bottleneck_mlp",
    "frozen_encoder",
)

MODEL_REPOS_BY_METHOD: dict[str, dict[str, str]] = {
    "full": {
        "distilbert": "cristian-untaru/distilbert-medical-triage",
        "biobert": "cristian-untaru/biobert-medical-triage",
        "roberta": "cristian-untaru/roberta-medical-triage",
        "biomedbert": "cristian-untaru/biomedbert-medical-triage",
    },
    "lora": {
        "distilbert": "cristian-untaru/lora-distilbert-medical-triage",
        "biobert": "cristian-untaru/lora-biobert-medical-triage",
        "roberta": "cristian-untaru/lora-roberta-medical-triage",
        "biomedbert": "cristian-untaru/lora-biomedbert-medical-triage",
    },
    "bottleneck_mlp": {
        "distilbert": "cristian-untaru/bottleneck-mlp-distilbert-medical-triage",
        "biobert": "cristian-untaru/bottleneck-mlp-biobert-medical-triage",
        "roberta": "cristian-untaru/bottleneck-mlp-roberta-medical-triage",
        "biomedbert": "cristian-untaru/bottleneck-mlp-biomedbert-medical-triage",
    },
    "frozen_encoder": {
        "distilbert": "cristian-untaru/frozen-encoder-distilbert-medical-triage",
        "biobert": "cristian-untaru/frozen-encoder-biobert-medical-triage",
        "roberta": "cristian-untaru/frozen-encoder-roberta-medical-triage",
        "biomedbert": "cristian-untaru/frozen-encoder-biomedbert-medical-triage",
    },
}

LABEL_DISPLAY: dict[str, str] = {
    "self_monitor": "Self-monitor",
    "consult_gp": "Consult GP",
    "urgent": "Urgent",
}

INTENT_CLASSIFIER_REPO = "cristian-untaru/sortmed-intent-classifier"
INTENT_CLASSIFIER_MODEL_FILE = "intent_pipeline.joblib"
INTENT_CLASSIFIER_CONFIG_FILE = "intent_config.json"
VALID_INTENT = "symptom_description"


def build_model_key(method_key: str, base_model_key: str) -> str:
    if method_key == "full":
        return base_model_key
    if method_key == "bottleneck_mlp":
        return f"bottleneck-mlp-{base_model_key}"
    if method_key == "frozen_encoder":
        return f"frozen-encoder-{base_model_key}"
    return f"{method_key}-{base_model_key}"


def _build_model_metadata() -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    for method_key, repos in MODEL_REPOS_BY_METHOD.items():
        for base_model_key, repo_id in repos.items():
            model_key = build_model_key(method_key, base_model_key)
            metadata[model_key] = {
                "base_model_key": base_model_key,
                "method_key": method_key,
                "repo_id": repo_id,
            }
    return metadata


MODEL_METADATA = _build_model_metadata()
FULL_MODEL_REGISTRY = MODEL_REPOS_BY_METHOD["full"].copy()
ALL_MODEL_REGISTRY = {
    model_key: metadata["repo_id"]
    for model_key, metadata in MODEL_METADATA.items()
}

MODEL_REGISTRY: dict[str, str] = (
    ALL_MODEL_REGISTRY if ENABLE_PEFT_MODEL_SELECTION else FULL_MODEL_REGISTRY
)

MODEL_DISPLAY_NAMES: dict[str, str] = {
    model_key: (
        BASE_MODEL_DISPLAY_NAMES[metadata["base_model_key"]]
        if metadata["method_key"] == "full"
        else (
            f"{MODEL_METHOD_SHORT_NAMES[metadata['method_key']]} - "
            f"{BASE_MODEL_DISPLAY_NAMES[metadata['base_model_key']]}"
        )
    )
    for model_key, metadata in MODEL_METADATA.items()
}


def get_model_metadata(model_key: str | None) -> dict[str, str] | None:
    if not model_key:
        return None
    return MODEL_METADATA.get(model_key)


def get_model_base_key(model_key: str | None) -> str | None:
    metadata = get_model_metadata(model_key)
    if metadata:
        return metadata["base_model_key"]
    return model_key if model_key in BASE_MODEL_KEYS else None


def get_model_method_key(model_key: str | None) -> str:
    metadata = get_model_metadata(model_key)
    return metadata["method_key"] if metadata else "full"


def get_base_model_display_name(model_key: str | None) -> str:
    base_key = get_model_base_key(model_key)
    if not base_key:
        return model_key or "N/A"
    return BASE_MODEL_DISPLAY_NAMES.get(base_key, base_key)


def get_model_method_display_name(model_key: str | None) -> str:
    method_key = get_model_method_key(model_key)
    return MODEL_METHOD_DISPLAY_NAMES.get(method_key, method_key)


def get_model_method_short_name(model_key: str | None) -> str:
    method_key = get_model_method_key(model_key)
    return MODEL_METHOD_SHORT_NAMES.get(method_key, method_key)


def get_model_history_display_name(model_key: str | None) -> str:
    base_name = get_base_model_display_name(model_key)
    method_name = get_model_method_short_name(model_key)
    if get_model_method_key(model_key) == "full":
        return base_name
    return f"{base_name} ({method_name})"


def model_requires_trust_remote_code(model_key: str | None) -> bool:
    return get_model_method_key(model_key) == "bottleneck_mlp"
