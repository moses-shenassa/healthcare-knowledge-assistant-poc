import json
from pathlib import Path
from typing import List, Tuple

import faiss
from openai import OpenAI

try:
    import tomllib  # py3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


class VectorStore:
    def __init__(self, index: faiss.IndexFlatIP, texts: List[str]):
        self.index = index
        self.texts = texts

    def search(self, embedding: list[float], k: int = 5) -> List[Tuple[float, str]]:
        import numpy as np

        vec = np.array([embedding]).astype("float32")
        scores, idxs = self.index.search(vec, k)
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue
            results.append((float(score), self.texts[idx]))
        return results


def load_vector_store(config_path: str = "config.toml") -> VectorStore:
    with open(config_path, "rb") as f:
        cfg = tomllib.load(f)

    index_path = Path(cfg["vector_store"]["index_path"])
    metadata_path = Path(cfg["vector_store"]["metadata_path"])

    index = faiss.read_index(str(index_path))
    texts = json.loads(metadata_path.read_text(encoding="utf-8"))
    return VectorStore(index=index, texts=texts)


def get_embedding(client: OpenAI, text: str) -> list[float]:
    # Simple, single-embedding helper
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return resp.data[0].embedding
