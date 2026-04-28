"""Factory selecting LLM / embeddings client implementations from settings."""

from app.config import Settings, get_settings
from app.llm.base import EmbeddingsClient, LLMClient
from app.llm.mock import MockEmbeddingsClient, MockLLMClient


def build_llm_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or get_settings()
    backend = settings.llm_backend
    if backend == "mock":
        return MockLLMClient(model=settings.llm_model)
    if backend in {"ollama", "vllm"}:
        # OpenAI-compatible / Ollama implementations land in PR 3.
        # For now mock falls back so PR 1 is self-contained.
        return MockLLMClient(model=settings.llm_model)
    raise ValueError(f"unknown llm backend: {backend}")


def build_embeddings_client(settings: Settings | None = None) -> EmbeddingsClient:
    settings = settings or get_settings()
    backend = settings.embeddings_backend
    if backend == "mock":
        return MockEmbeddingsClient(dim=settings.embeddings_dim, model=settings.embeddings_model)
    if backend in {"ollama", "tei", "infinity"}:
        return MockEmbeddingsClient(dim=settings.embeddings_dim, model=settings.embeddings_model)
    raise ValueError(f"unknown embeddings backend: {backend}")
