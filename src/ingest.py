"""Document ingestion and chunking utilities for the Healthcare RAG PoC."""

from pathlib import Path
from typing import Dict, List

from config import AppConfig

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_raw_documents(documents_dir: str) -> List[Dict]:
    """Load text documents from the given directory.

    Only simple text-based formats (e.g., .txt, .md) are supported in this PoC.
    This keeps ingestion predictable and easy to extend later (e.g., adding PDF support).
    """
    base = Path(documents_dir)
    if not base.exists():
        raise FileNotFoundError(f"Documents directory not found: {base}")

    docs: List[Dict] = []
    for path in base.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append(
                {
                    "source": str(path),
                    "content": text.strip(),
                }
            )
    return docs


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Naively split text into overlapping character-based chunks.

    For a PoC, character-based chunking is sufficient and easy to reason about.
    In production, you might replace this with token-based chunking.
    """
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end >= length:
            break
        # Slide the window forward with overlap
        start = end - chunk_overlap

    # Filter out any empty strings
    return [c for c in chunks if c]


def ingest_documents(config: AppConfig) -> List[Dict]:
    """Load and chunk documents according to configuration.

    Returns a list of chunk dicts with:
    - source: original file path
    - chunk_id: index of the chunk within the source document
    - content: chunk text
    """
    docs = load_raw_documents(config.paths.documents)
    all_chunks: List[Dict] = []
    for doc in docs:
        chunks = chunk_text(
            doc["content"],
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
        )
        for idx, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "source": doc["source"],
                    "chunk_id": idx,
                    "content": chunk,
                }
            )

    return all_chunks


if __name__ == "__main__":
    from config import load_config

    cfg = load_config()
    chunks = ingest_documents(cfg)
    print(f"Ingested {len(chunks)} chunks from documents in {cfg.paths.documents}")
