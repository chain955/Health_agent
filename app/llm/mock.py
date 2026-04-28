"""Mock LLM and embeddings clients — used when no backend is available.

Deterministic by content hash so tests are reproducible. See spec answer to Q1.
"""

import hashlib
import math
import time
from collections.abc import AsyncIterator
from typing import Any

from app.llm.base import ChatMessage, ChatResponse, HealthStatus


class MockLLMClient:
    backend = "mock"

    def __init__(self, model: str = "mock-llm") -> None:
        self.model = model

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
        seed: int | None = None,
    ) -> ChatResponse:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return ChatResponse(
            content=f"[mock-llm reply to: {last_user[:60]}]",
            finish_reason="stop",
            usage={"prompt_tokens": 0, "completion_tokens": 0},
        )

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        seed: int | None = None,
    ) -> AsyncIterator[str]:
        reply = (await self.chat(messages, model=model)).content
        for word in reply.split(" "):
            yield word + " "

    async def health(self) -> HealthStatus:
        return HealthStatus(healthy=True, backend=self.backend, detail="mock always healthy")

    async def close(self) -> None:
        return None


class MockEmbeddingsClient:
    backend = "mock"

    def __init__(self, dim: int = 768, model: str = "mock-embeddings") -> None:
        self.dim = dim
        self.model = model

    def _vector(self, text: str) -> list[float]:
        # deterministic pseudo-vector from sha256, normalized to unit length
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw = [(b - 127.5) / 127.5 for b in digest]
        # tile/truncate to required dim
        out: list[float] = []
        i = 0
        while len(out) < self.dim:
            out.append(raw[i % len(raw)])
            i += 1
        norm = math.sqrt(sum(x * x for x in out)) or 1.0
        return [x / norm for x in out]

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    async def health(self) -> HealthStatus:
        start = time.perf_counter()
        await self.embed(["health-check"])
        elapsed = (time.perf_counter() - start) * 1000
        return HealthStatus(healthy=True, backend=self.backend, latency_ms=elapsed)

    async def close(self) -> None:
        return None
