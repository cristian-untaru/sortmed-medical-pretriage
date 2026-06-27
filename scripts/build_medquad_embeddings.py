"""Precompute semantic embeddings for MedQuAD retrieval."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_INPUT_CSV = Path("data/medquad_retrieval.csv")
DEFAULT_OUTPUT_NPY = Path("data/medquad_embeddings_minilm.npy")
DEFAULT_OUTPUT_META = Path("data/medquad_embeddings_minilm_meta.json")


# Computes a stable fingerprint so the backend can detect stale embeddings.
def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Loads the MedQuAD CSV and returns the exact text encoded by the model.
def load_retrieval_documents(csv_path: Path) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(csv_path)

    if "retrieval_text" not in df.columns:
        required = {"question", "answer"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"{csv_path} is missing required columns: {sorted(missing)}"
            )
        df["retrieval_text"] = (
            df["question"].fillna("").astype(str).str.strip()
            + " "
            + df["answer"].fillna("").astype(str).str.strip()
        ).str.strip()

    df = df.dropna(subset=["answer"]).copy()
    df["retrieval_text"] = df["retrieval_text"].fillna("").astype(str).str.strip()
    df = df[df["retrieval_text"].ne("")]

    return df, df["retrieval_text"].tolist()


# Builds normalized MiniLM embeddings and stores them as float32 vectors.
def build_embeddings(
    csv_path: Path,
    output_npy: Path,
    output_meta: Path,
    model_name: str,
    batch_size: int,
) -> None:
    df, documents = load_retrieval_documents(csv_path)

    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        documents,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)

    output_npy.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_npy, embeddings)

    metadata = {
        "model_name": model_name,
        "source_csv": str(csv_path.as_posix()),
        "source_sha256": file_sha256(csv_path),
        "row_count": int(len(df)),
        "embedding_dim": int(embeddings.shape[1]),
        "normalized": True,
        "dtype": str(embeddings.dtype),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    output_meta.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Saved embeddings: {output_npy}")
    print(f"Saved metadata:   {output_meta}")
    print(f"Shape:            {embeddings.shape}")


# Parses command-line options for reproducible offline embedding generation.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build precomputed MiniLM embeddings for MedQuAD retrieval."
    )
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT_CSV)
    parser.add_argument("--output-npy", type=Path, default=DEFAULT_OUTPUT_NPY)
    parser.add_argument("--output-meta", type=Path, default=DEFAULT_OUTPUT_META)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


# Entry point used from the project root.
def main() -> None:
    args = parse_args()
    build_embeddings(
        csv_path=args.input_csv,
        output_npy=args.output_npy,
        output_meta=args.output_meta,
        model_name=args.model_name,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
