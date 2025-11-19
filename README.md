# Healthcare Knowledge Assistant – RAG PoC

This project is a small proof-of-concept for a **Custom GPT-style assistant**
that answers healthcare-related questions using a simple
**retrieval-augmented generation (RAG)** pattern over publicly available
patient education materials (no PHI).

The goal is to demonstrate how I would design and implement a safe,
domain-aware assistant for a healthcare client.

## Features

- Ingests local healthcare documents into a lightweight embedding index
- Uses vector search to retrieve relevant passages for each question
- Combines retrieved context with safety-focused system prompts
- CLI interface for interactive querying
- Configuration via `config.toml`

## Stack

- Python 3.11+
- OpenAI API (chat completions + embeddings)
- `faiss-cpu` for local vector search

## Quickstart

```bash
git clone https://github.com/moses-shenassa/healthcare-knowledge-assistant-poc.git
cd healthcare-knowledge-assistant-poc

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp config.example.toml config.toml  # then edit with your OpenAI key

python -m src.build_vector_store
python -m src.rag_cli
