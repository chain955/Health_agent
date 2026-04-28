"""Ollama LLM client — native /api/chat endpoint."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.llm.base import ChatMessage, ChatResponse, HealthStatus

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = frozenset(range(500, 600))
_MAX_RETRIES = 2
_BACKOFF_BASE = 0.5  # seconds


def _build_ollama_messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
    return [{"role": m.role, "content": m.content} for m in messages]


class OllamaLLMClient:
    backend = "ollama"

    def __init__(
        self,
        base_url: str = "http://ollama:11434",
        model: str = "llama3.1:8b",
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout_seconds, connect=10.0),
        )

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        last_exc: BaseException | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = await self._client.request(method, url, **kwargs)
                if resp.status_code not in _RETRYABLE_STATUS or attempt == _MAX_RETRIES:
                    return resp
                last_exc = httpx.HTTPStatusError(
                    f"{resp.status_code}",
                    request=resp.request,
                    response=resp,
                )
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt == _MAX_RETRIES:
                    raise
            backoff = _BACKOFF_BASE * (2**attempt)
            logger.warning(
                "ollama retry %d/%d after %.1fs: %s",
                attempt + 1,
                _MAX_RETRIES,
                backoff,
                last_exc,
            )
            import asyncio

            await asyncio.sleep(backoff)
        raise RuntimeError("unreachable")  # pragma: no cover

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
        body: dict[str, Any] = {
            "model": model or self.model,
            "messages": _build_ollama_messages(messages),
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
            },
        }
        if max_tokens is not None:
            body["options"]["num_predict"] = max_tokens
        if seed is not None:
            body["options"]["seed"] = seed
        if response_format is not None:
            body["format"] = response_format

        resp = await self._request_with_retry("POST", "/api/chat", json=body)
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message", {})
        return ChatResponse(
            content=msg.get("content", ""),
            finish_reason=data.get("done_reason"),
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
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
        body: dict[str, Any] = {
            "model": model or self.model,
            "messages": _build_ollama_messages(messages),
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
            },
        }
        if max_tokens is not None:
            body["options"]["num_predict"] = max_tokens
        if seed is not None:
            body["options"]["seed"] = seed

        async with self._client.stream("POST", "/api/chat", json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token

    async def health(self) -> HealthStatus:
        start = time.perf_counter()
        try:
            resp = await self._client.get("/api/tags")
            elapsed = (time.perf_counter() - start) * 1000
            if resp.status_code == 200:
                return HealthStatus(
                    healthy=True,
                    backend=self.backend,
                    latency_ms=elapsed,
                )
            return HealthStatus(
                healthy=False,
                backend=self.backend,
                detail=f"status {resp.status_code}",
                latency_ms=elapsed,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return HealthStatus(
                healthy=False,
                backend=self.backend,
                detail=str(exc),
                latency_ms=elapsed,
            )

    async def close(self) -> None:
        await self._client.aclose()
