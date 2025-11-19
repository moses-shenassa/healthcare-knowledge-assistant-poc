"""Build a FAISS index from local healthcare documents for the RAG PoC."""

import json
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
from openai import OpenAI
from tqdm import tqdm

from config import AppConfig, load_config
from ingest import ingest_documents


def embed_texts(
    client: OpenAI,
    texts: List[str],
    model: str,
    batch_size: int = 64,
) -> np.ndarray:
    """Embed a list of texts using the specified OpenAI embedding model.

    Returns a NumPy array of shape (num_texts, embedding_dim).
    """
    embeddings: List[List[float]] = []

    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding chunks"):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=model,
            input=batch,
        )
        for item in response.data:
            embeddings.append(item.embedding)

    array = np.array(embeddings, dtype="float32")
    return array


def build_faiss_index(config: AppConfig) -> None:
    """Ingest documents, embed chunks, and build a FAISS index with metadata."""
    client = OpenAI()

    chunks = ingest_documents(config)
    texts = [c["content"] for c in chunks]

    if not texts:
        raise ValueError(
            "No text chunks found. Ensure documents are available in the configured directory."
        )

    vectors = embed_texts(
        client=client,
        texts=texts,
        model=config.openai.embedding_model,
    )

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    index_path = Path(config.paths.index)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))

    metadata_path = Path(config.paths.metadata)
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Built FAISS index with {vectors.shape[0]} vectors.")
    print(f"Index saved to: {index_path}")
    print(f"Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    cfg = load_config()
    build_faiss_index(cfg)
