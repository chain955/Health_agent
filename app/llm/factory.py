"""Factory selecting LLM / embeddings client implementations from settings."""

from app.config import Settings, get_settings
from app.llm.base import EmbeddingsClient, LLMClient
from app.llm.mock import MockEmbeddingsClient, MockLLMClient
from app.llm.ollama import OllamaLLMClient
from app.llm.ollama_embeddings import OllamaEmbeddingsClient


def build_llm_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or get_settings()
    backend = settings.llm_backend
    if backend == "mock":
        return MockLLMClient(model=settings.llm_model)
    if backend == "ollama":
        return OllamaLLMClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_llm_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    if backend == "vllm":
        # OpenAI-compatible client lands in a later PR.
        return MockLLMClient(model=settings.llm_model)
    raise ValueError(f"unknown llm backend: {backend}")


def build_embeddings_client(settings: Settings | None = None) -> EmbeddingsClient:
    settings = settings or get_settings()
    backend = settings.embeddings_backend
    if backend == "mock":
        return MockEmbeddingsClient(dim=settings.embeddings_dim, model=settings.embeddings_model)
    if backend == "ollama":
        return OllamaEmbeddingsClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embed_model,
            dim=settings.embeddings_dim,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    if backend in {"tei", "infinity"}:
        # TEI / Infinity clients land in a later PR.
        return MockEmbeddingsClient(dim=settings.embeddings_dim, model=settings.embeddings_model)
    raise ValueError(f"unknown embeddings backend: {backend}")
