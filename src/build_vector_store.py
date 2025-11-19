import json
from pathlib import Path

import faiss
from openai import OpenAI
from tqdm import tqdm

from .vector_store import get_embedding

try:
    import tomllib  # py3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


def load_config(path: str = "config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_texts() -> list[str]:
    base = Path("data/sample_docs")
    texts: list[str] = []
    for p in base.rglob("*.txt"):
        content = p.read_text(encoding="utf-8")
        for chunk in content.split("\n\n"):
            chunk = chunk.strip()
            if chunk:
                texts.append(chunk)
    return texts


def main():
    cfg = load_config()
    client = OpenAI(api_key=cfg["openai"]["api_key"])

    texts = load_texts()
    print(f"Loaded {len(texts)} text chunks")

    import numpy as np

    embeddings = []
    for t in tqdm(texts, desc="Embedding"):
        emb = get_embedding(client, t)
        embeddings.append(emb)

    dim = len(embeddings[0])
    index = faiss.IndexFlatIP(dim)
    index.add(np.array(embeddings).astype("float32"))

    index_path = Path(cfg["vector_store"]["index_path"])
    metadata_path = Path(cfg["vector_store"]["metadata_path"])
    index_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))
    metadata_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved index to {index_path} and metadata to {metadata_path}")


if __name__ == "__main__":
    main()
