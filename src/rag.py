"""Core Retrieval-Augmented Generation logic for the Healthcare RAG PoC."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import faiss
import numpy as np
from openai import OpenAI

from config import AppConfig, load_config

SYSTEM_PROMPT = """You are a cautious, domain-aware healthcare information assistant.
You are not a doctor and you do not provide medical advice, diagnosis, or treatment.
You answer using only the provided reference materials and your general healthcare knowledge when appropriate.
You must:
- Be conservative and avoid speculation.
- Never tell users to start, stop, or change medications.
- Encourage users to consult a qualified healthcare professional.
- If the user describes symptoms that could indicate an emergency
  (e.g., chest pain, difficulty breathing, suicidal thoughts, stroke symptoms),
  urge them to seek emergency care immediately (e.g., call emergency services).

If the provided context does not contain enough information to answer safely,
say that you are unsure and recommend speaking to a healthcare professional."""


@dataclass
class RetrievedChunk:
    """A single retrieved context chunk from the knowledge base."""
    content: str
    source: str
    chunk_id: int
    score: float


class HealthcareRAG:
    """High-level RAG interface used by the CLI and other callers."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.client = OpenAI()
        self.index, self.metadata = self._load_index_and_metadata()

    def _load_index_and_metadata(self) -> Tuple[faiss.IndexFlatL2, List[Dict]]:
        index_path = Path(self.config.paths.index)
        metadata_path = Path(self.config.paths.metadata)

        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")

        index = faiss.read_index(str(index_path))
        with metadata_path.open("r", encoding="utf-8") as f:
            metadata: List[Dict] = json.load(f)

        return index, metadata

    def _embed_query(self, query: str) -> np.ndarray:
        """Embed a user query into the same vector space as the document chunks."""
        response = self.client.embeddings.create(
            model=self.config.openai.embedding_model,
            input=[query],
        )
        vector = np.array(response.data[0].embedding, dtype="float32")
        return vector.reshape(1, -1)

    def retrieve(self, query: str, top_k: int | None = None) -> List[RetrievedChunk]:
        """Retrieve the top-k most similar chunks for the given query."""
        if top_k is None:
            top_k = self.config.rag.top_k

        query_vec = self._embed_query(query)
        distances, indices = self.index.search(query_vec, top_k)

        results: List[RetrievedChunk] = []
        for rank, (idx, dist) in enumerate(zip(indices[0], distances[0])):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            results.append(
                RetrievedChunk(
                    content=meta["content"],
                    source=meta["source"],
                    chunk_id=meta.get("chunk_id", rank),
                    score=float(dist),
                )
            )
        return results

    def _build_messages(self, question: str, contexts: List[RetrievedChunk]) -> List[Dict]:
        """Build the chat messages for the OpenAI Chat Completions API."""
        context_text = "\n\n---\n\n".join(
            f"Source: {c.source} (chunk {c.chunk_id})\n\n{c.content}"
            for c in contexts
        )

        user_prompt = f"""You are answering a healthcare-related question.

Here are reference excerpts from patient-education materials:

{context_text}

User question:
{question}

Instructions:
- Base your answer primarily on the reference excerpts above.
- If the excerpts do not contain enough information, say so clearly.
- Keep your answer concise, clear, and in plain language.
- Include a brief reminder that you are not a doctor and cannot give medical advice."""

        messages: List[Dict] = [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ]
        return messages

    def answer(self, question: str, debug: bool = False) -> Dict:
        """Generate an answer for the user's question using RAG."""
        contexts = self.retrieve(question)
        messages = self._build_messages(question, contexts)

        response = self.client.chat.completions.create(
            model=self.config.openai.model,
            temperature=self.config.openai.temperature,
            messages=messages,
        )

        answer_text = response.choices[0].message.content.strip()

        result: Dict = {"answer": answer_text}
        if debug:
            result["contexts"] = [c.__dict__ for c in contexts]
        return result


if __name__ == "__main__":
    cfg = load_config()
    rag = HealthcareRAG(cfg)
    res = rag.answer("What are common signs of dehydration?", debug=True)
    print(res["answer"])
