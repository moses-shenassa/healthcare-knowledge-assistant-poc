# Healthcare Knowledge Assistant — RAG Proof of Concept

This project is a small but realistic proof-of-concept for building a safe, conservative, domain-aware healthcare assistant using **Retrieval-Augmented Generation (RAG)**.  
It demonstrates how a healthcare-facing client solution might be designed using:

- Python 3.11+
- OpenAI API (Chat Completions + Embeddings)
- FAISS for vector search
- A configurable `config.toml`
- A simple CLI for interactive querying
- Public patient-education materials only (no PHI)

## 🎯 Project Goals

- Show how a safe, medically conservative AI assistant can retrieve and use vetted healthcare educational materials.
- Demonstrate a minimal but extensible architecture for healthcare RAG systems.
- Use local documents → chunking → embeddings → FAISS → retrieval → safe prompting.
- Emphasize **safety, transparency, and limitations** in all generated outputs.

## 🧱 Architecture Overview

local documents  
   ↓ ingestion & chunking  
embeddings  
   ↓  
FAISS vector index  
   ↓  
user question → retrieval  
   ↓  
RAG prompt (system + safety + retrieved context)  
   ↓  
OpenAI completion  

## 📁 Repository Structure

healthcare-rag-poc/
│
├── ingest.py            # Load & chunk documents
├── build_index.py       # Create FAISS index
├── rag.py               # Retrieval + prompt construction
├── cli.py               # Interactive CLI interface
├── config.py            # Loads config.toml
├── config.toml          # Model + index + safety configuration
├── /data                # Source patient-education materials
├── /index               # Saved FAISS index + metadata
└── README.md            # Project documentation (this file)

## ⚙️ Configuration (`config.toml`)

Example:

[openai]
model = "gpt-4.1"
embedding_model = "text-embedding-3-large"
temperature = 0.1

[paths]
documents = "data/"
index = "index/faiss.index"
metadata = "index/metadata.json"

[rag]
chunk_size = 800
chunk_overlap = 150
top_k = 4

[safety]
conservative_mode = true

## 🩺 Safety Philosophy

Even though this PoC uses *public* health education documents, the assistant follows strict behavioral constraints:

- Does **not** diagnose conditions.
- Does **not** recommend starting/stopping medications.
- Answers are **informational only**.
- Encourages speaking with a qualified healthcare professional.
- If a question resembles an emergency, the assistant advises seeking urgent/ER care.

## ▶️ Running the PoC

### 1. Install dependencies
pip install -r requirements.txt

### 2. Build the index
python build_index.py

### 3. Run the CLI
python cli.py

Example query:

> What are early signs of dehydration?

## 📌 Notes

- This is **not** a medical device.
- No PHI should be stored or queried.
- This PoC is designed to illustrate engineering approach, not to provide medical guidance.

## 📄 License

MIT (or customize as needed)
