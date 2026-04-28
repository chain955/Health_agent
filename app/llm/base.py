"""LLMClient / EmbeddingsClient interfaces — see spec 1, 19.3."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Literal, Protocol


@dataclass(slots=True)
class ChatMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


@dataclass(slots=True)
class ChatResponse:
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str | None = None
    usage: dict[str, int] | None = None


@dataclass(slots=True)
class HealthStatus:
    healthy: bool
    backend: str
    detail: str | None = None
    latency_ms: float | None = None


class LLMClient(Protocol):
    backend: str

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
    ) -> ChatResponse: ...

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        seed: int | None = None,
    ) -> AsyncIterator[str]: ...

    async def health(self) -> HealthStatus: ...

    async def close(self) -> None: ...


class EmbeddingsClient(Protocol):
    backend: str
    dim: int

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]: ...

    async def health(self) -> HealthStatus: ...

    async def close(self) -> None: ...
