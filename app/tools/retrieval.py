"""Tool retrieval — embed tool descriptions, select top-k by cosine similarity."""

from __future__ import annotations

import math

from app.llm.base import EmbeddingsClient
from app.tools.base import ToolSpec
from app.tools.registry import ToolRegistry


class ToolRetriever:
    """Caches tool-description embeddings; selects top-k tools for a query."""

    def __init__(self, registry: ToolRegistry, embeddings: EmbeddingsClient) -> None:
        self._registry = registry
        self._embeddings = embeddings
        self._cache: list[tuple[ToolSpec, list[float]]] | None = None
        self._cache_version: int = -1

    def _is_stale(self) -> bool:
        return self._cache is None or self._cache_version != self._registry.version

    async def _refresh(self) -> None:
        specs = self._registry.list()
        if not specs:
            self._cache = []
            self._cache_version = self._registry.version
            return
        descriptions = [s.description for s in specs]
        vectors = await self._embeddings.embed(descriptions)
        self._cache = list(zip(specs, vectors, strict=True))
        self._cache_version = self._registry.version

    async def select_tools(self, query: str, k: int = 3) -> list[ToolSpec]:
        if self._is_stale():
            await self._refresh()
        assert self._cache is not None
        if not self._cache:
            return []

        query_vec = (await self._embeddings.embed([query]))[0]
        scored: list[tuple[float, ToolSpec]] = []
        for spec, tool_vec in self._cache:
            sim = _cosine_similarity(query_vec, tool_vec)
            scored.append((sim, spec))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [spec for _, spec in scored[:k]]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
