from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import toml


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI models."""
    model: str
    embedding_model: str
    temperature: float = 0.1


@dataclass
class PathsConfig:
    """Filesystem paths used by the application."""
    documents: str
    index: str
    metadata: str


@dataclass
class RAGConfig:
    """RAG-specific configuration parameters."""
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4


@dataclass
class SafetyConfig:
    """Safety-related behaviors and flags."""
    conservative_mode: bool = True


@dataclass
class AppConfig:
    """Top-level application configuration object."""
    openai: OpenAIConfig
    paths: PathsConfig
    rag: RAGConfig
    safety: SafetyConfig


def load_config(path: str = "config.toml") -> AppConfig:
    """Load configuration from a TOML file into a typed AppConfig object."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    data: Dict[str, Any] = toml.load(config_path)

    openai_conf = OpenAIConfig(
        model=data["openai"]["model"],
        embedding_model=data["openai"]["embedding_model"],
        temperature=float(data["openai"].get("temperature", 0.1)),
    )

    paths_conf = PathsConfig(
        documents=data["paths"]["documents"],
        index=data["paths"]["index"],
        metadata=data["paths"]["metadata"],
    )

    rag_data = data.get("rag", {})
    rag_conf = RAGConfig(
        chunk_size=int(rag_data.get("chunk_size", 800)),
        chunk_overlap=int(rag_data.get("chunk_overlap", 150)),
        top_k=int(rag_data.get("top_k", 4)),
    )

    safety_data = data.get("safety", {})
    safety_conf = SafetyConfig(
        conservative_mode=bool(safety_data.get("conservative_mode", True))
    )

    return AppConfig(
        openai=openai_conf,
        paths=paths_conf,
        rag=rag_conf,
        safety=safety_conf,
    )
