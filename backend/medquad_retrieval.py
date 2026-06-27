"""Context-aware MedQuAD retrieval based on MiniLM embeddings."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
from huggingface_hub import hf_hub_download

_BASE_DIR = Path(__file__).parent.parent

MEDQUAD_HF_REPO_ID = os.getenv(
    "SORTMED_MEDQUAD_REPO_ID",
    "cristian-untaru/medquad-retrieval-pretriage",
)
MEDQUAD_HF_REPO_TYPE = "dataset"
MEDQUAD_HF_CSV_FILENAME = "medquad_retrieval.csv"
MEDQUAD_HF_EMBEDDINGS_FILENAME = "artifacts/medquad_embeddings_minilm.npy"
MEDQUAD_HF_EMBEDDINGS_META_FILENAME = "artifacts/medquad_embeddings_minilm_meta.json"

MEDQUAD_PATH = _BASE_DIR / "data" / "medquad_retrieval.csv"
MEDQUAD_EMBEDDINGS_PATH = _BASE_DIR / "data" / "medquad_embeddings_minilm.npy"
MEDQUAD_EMBEDDINGS_META_PATH = _BASE_DIR / "data" / "medquad_embeddings_minilm_meta.json"
MEDQUAD_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MEDQUAD_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MEDQUAD_RERANK_CANDIDATES = 20
MIN_MEDQUAD_SEMANTIC_SIMILARITY = 0.50
SENSITIVE_TERM_MIN_SIMILARITY = 0.65
ENABLE_MEDQUAD_RERANKER = os.getenv("SORTMED_ENABLE_MEDQUAD_RERANKER", "").lower() in {
    "1",
    "true",
    "yes",
}

SENSITIVE_MEDQUAD_TERMS = {
    "cancer",
    "carcinoma",
    "tumor",
    "tumour",
    "leukemia",
    "lymphoma",
    "melanoma",
    "metastatic",
    "metastasis",
    "mutation",
    "genetic",
    "syndrome",
    "rare disease",
}

def _resolve_medquad_file(
    hf_filename: str,
    local_fallback: Path,
    label: str,
) -> Path | None:
    """
    Resolve a MedQuAD artifact from Hugging Face, with a local fallback.

    The deployed app uses the dataset repository as the primary source. Local
    files are kept only as a development fallback when available.
    """
    try:
        downloaded_path = hf_hub_download(
            repo_id=MEDQUAD_HF_REPO_ID,
            filename=hf_filename,
            repo_type=MEDQUAD_HF_REPO_TYPE,
        )
        return Path(downloaded_path)
    except Exception as exc:
        if local_fallback.exists():
            return local_fallback

        st.warning(
            f"{label} could not be loaded from Hugging Face Hub "
            f"({MEDQUAD_HF_REPO_ID}/{hf_filename}): {exc}"
        )
        return None


@st.cache_resource(show_spinner="Loading medical knowledge base...")
def load_medquad() -> pd.DataFrame:
    """
    Load the MedQuAD retrieval table used by the semantic search pipeline.

    The retrieval CSV contains the prebuilt retrieval_text field used for
    embedding-based matching against the user's symptom description.
    """
    medquad_path = _resolve_medquad_file(
        MEDQUAD_HF_CSV_FILENAME,
        MEDQUAD_PATH,
        "MedQuAD retrieval CSV",
    )

    if medquad_path is None:
        st.warning(
            f"MedQuAD was not found at {MEDQUAD_PATH}. "
            "Context-aware retrieval will be disabled."
        )
        return pd.DataFrame(columns=["focus", "question", "answer", "retrieval_text"])

    df = pd.read_csv(medquad_path)

    required_columns = ["focus", "question", "answer", "retrieval_text"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    df = df.dropna(subset=["answer"])
    df["answer"] = df["answer"].astype(str).str.strip()
    df["question"] = df["question"].fillna("").astype(str).str.strip()
    df["focus"] = df["focus"].fillna("").astype(str).str.strip()
    df["retrieval_text"] = df["retrieval_text"].fillna("").astype(str).str.strip()

    return df

def _safe_text(value: Any, fallback: str = "General") -> str:
    """
    Convert DataFrame values into safe display text.

    Missing values are replaced with a clear fallback instead of being rendered
    as pandas placeholders such as 'nan'.
    """
    if pd.isna(value):
        return fallback

    text = str(value).strip()

    if not text or text.lower() == "nan":
        return fallback

    return text


def _extract_topic_from_question(question: str) -> str | None:
    """
    Extract a readable medical topic when the MedQuAD focus field is missing.

    Examples:
      "What are the symptoms of Heart Attack?" -> "Heart Attack"
      "What is (are) Aicardi-Goutières syndrome?" -> "Aicardi-Goutières syndrome"
      "How to diagnose Asthma?" -> "Asthma"
    """
    question = _safe_text(question, fallback="")

    if not question:
        return None

    patterns = [
        r"what are the symptoms of (.+?)\??$",
        r"what are the signs and symptoms of (.+?)\??$",
        r"what is \(are\) (.+?)\??$",
        r"what is (.+?)\??$",
        r"what causes (.+?)\??$",
        r"how to diagnose (.+?)\??$",
        r"how is (.+?) diagnosed\??$",
        r"how to treat (.+?)\??$",
        r"how is (.+?) treated\??$",
    ]

    for pattern in patterns:
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            topic = match.group(1).strip()
            topic = re.sub(r"\s+", " ", topic)
            topic = topic.strip(" ?.,;:")

            if topic:
                return topic[0].upper() + topic[1:]

    return None


def _resolve_topic(focus: Any, question: Any) -> str:
    """
    Choose the topic displayed for a retrieved MedQuAD entry.

    Priority is: explicit focus field, topic extracted from the question, then
    the generic fallback label.
    """
    focus_text = _safe_text(focus, fallback="")

    if focus_text:
        return focus_text

    question_text = _safe_text(question, fallback="")
    extracted_topic = _extract_topic_from_question(question_text)

    if extracted_topic:
        return extracted_topic

    return "General"


def _load_sentence_transformer(model_name: str):
    from sentence_transformers import SentenceTransformer

    try:
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        return SentenceTransformer(model_name)


def _load_cross_encoder(model_name: str):
    from sentence_transformers import CrossEncoder

    try:
        return CrossEncoder(model_name, local_files_only=True)
    except Exception:
        return CrossEncoder(model_name)


def _read_medquad_embedding_metadata() -> dict[str, Any]:
    metadata_path = _resolve_medquad_file(
        MEDQUAD_HF_EMBEDDINGS_META_FILENAME,
        MEDQUAD_EMBEDDINGS_META_PATH,
        "MedQuAD embedding metadata",
    )

    if metadata_path is None:
        return {}

    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


@st.cache_resource(show_spinner="Loading MedQuAD semantic retrieval model...")
def load_medquad_embedding_model():
    """
    Load the MiniLM model used to embed the current user query.

    MedQuAD document embeddings are precomputed, so runtime work is limited to
    encoding the symptom text submitted by the user.
    """
    return _load_sentence_transformer(MEDQUAD_EMBEDDING_MODEL)


@st.cache_resource(show_spinner="Loading MedQuAD semantic index...")
def load_medquad_semantic_index(row_count: int) -> np.ndarray | None:
    """
    Load the precomputed MedQuAD embeddings and validate their row alignment.

    If the embedding artifact is missing or does not match the CSV row count,
    semantic retrieval is disabled instead of rebuilding the index at runtime.
    """
    embeddings_path = _resolve_medquad_file(
        MEDQUAD_HF_EMBEDDINGS_FILENAME,
        MEDQUAD_EMBEDDINGS_PATH,
        "MedQuAD semantic embeddings",
    )

    if embeddings_path is None:
        st.warning(
            "MedQuAD semantic embeddings were not found. Run "
            "scripts/build_medquad_embeddings.py before using semantic retrieval."
        )
        return None

    embeddings = np.load(embeddings_path)
    if embeddings.shape[0] != row_count:
        st.warning(
            "MedQuAD embeddings do not match the MedQuAD CSV row count. "
            "Regenerate data/medquad_embeddings_minilm.npy."
        )
        return None

    metadata = _read_medquad_embedding_metadata()
    if metadata and metadata.get("model_name") != MEDQUAD_EMBEDDING_MODEL:
        st.warning(
            "MedQuAD embeddings were built with a different embedding model. "
            "Regenerate them to avoid inconsistent retrieval scores."
        )

    return embeddings.astype(np.float32, copy=False)


@st.cache_resource(show_spinner="Loading MedQuAD semantic reranker...")
def load_medquad_reranker():
    """
    Load the optional cross-encoder reranker for top MedQuAD candidates.

    It is disabled by default because it adds another model to the runtime path.
    Set SORTMED_ENABLE_MEDQUAD_RERANKER=true to enable it.
    """
    return _load_cross_encoder(MEDQUAD_RERANKER_MODEL)


def _contains_sensitive_medquad_term(text: str) -> bool:
    lower_text = text.lower()
    return any(term in lower_text for term in SENSITIVE_MEDQUAD_TERMS)


def _passes_sensitive_term_filter(
    user_text: str,
    document_text: str,
    score: float,
) -> bool:
    """
    Avoid surfacing sensitive conditions unless the user mentions them directly.

    This reduces cases where common symptoms retrieve serious or rare conditions
    only because the retrieved document shares broad medical terms.
    """
    if not _contains_sensitive_medquad_term(document_text):
        return True

    if _contains_sensitive_medquad_term(user_text):
        return True

    return score >= SENSITIVE_TERM_MIN_SIMILARITY


def _semantic_candidate_indices(
    similarities: np.ndarray,
    candidate_count: int,
) -> list[int]:
    if similarities.size == 0:
        return []

    candidate_count = min(candidate_count, similarities.size)
    candidate_indices = np.argpartition(similarities, -candidate_count)[-candidate_count:]
    return candidate_indices[np.argsort(similarities[candidate_indices])[::-1]].tolist()


def _rerank_medquad_candidates(
    user_text: str,
    documents: list[str],
    candidate_indices: list[int],
) -> list[int]:
    if not ENABLE_MEDQUAD_RERANKER or not candidate_indices:
        return candidate_indices

    try:
        reranker = load_medquad_reranker()
        pairs = [(user_text, documents[idx]) for idx in candidate_indices]
        rerank_scores = reranker.predict(pairs)
    except Exception:
        return candidate_indices

    ranked_pairs = sorted(
        zip(candidate_indices, rerank_scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )
    return [idx for idx, _ in ranked_pairs]


def retrieve_medquad_context(
    user_text: str,
    medquad_df: pd.DataFrame,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant MedQuAD Q&A pairs for the symptom text.

    Each MedQuAD row is represented by a precomputed MiniLM embedding. The user
    query is embedded in the same vector space, and the displayed relevance score
    is cosine similarity between normalized embeddings, not a medical probability.
    """
    if medquad_df.empty:
        return []

    if not user_text.strip():
        return []

    documents = medquad_df["retrieval_text"].fillna("").astype(str).tolist()
    document_embeddings = load_medquad_semantic_index(len(medquad_df))
    if document_embeddings is None:
        return []

    embedding_model = load_medquad_embedding_model()
    query_embedding = embedding_model.encode(
        [user_text],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(np.float32)

    similarities = (query_embedding @ document_embeddings.T).flatten()
    candidate_count = max(top_k, MEDQUAD_RERANK_CANDIDATES)
    candidate_indices = _semantic_candidate_indices(similarities, candidate_count)
    ranked_indices = _rerank_medquad_candidates(user_text, documents, candidate_indices)

    results = []

    for idx in ranked_indices:
        score = float(similarities[idx])
        if score < MIN_MEDQUAD_SEMANTIC_SIMILARITY:
            continue

        row = medquad_df.iloc[idx]

        question = _safe_text(row.get("question", ""), fallback="Related medical question")
        topic = _resolve_topic(row.get("focus", ""), question)
        candidate_label_text = f"{topic} {question}"

        if not _passes_sensitive_term_filter(user_text, candidate_label_text, score):
            continue

        answer = _safe_text(row.get("answer", ""), fallback="No answer available.")

        results.append({
            "focus": topic,
            "question": question,
            "answer": answer,
            "score": round(score, 4),
        })

        if len(results) >= top_k:
            break

    return results
