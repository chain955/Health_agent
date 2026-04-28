"""Ollama embeddings client — native /api/embeddings endpoint."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.llm.base import HealthStatus

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = frozenset(range(500, 600))
_MAX_RETRIES = 2
_BACKOFF_BASE = 0.5


class OllamaEmbeddingsClient:
    backend = "ollama"

    def __init__(
        self,
        base_url: str = "http://ollama:11434",
        model: str = "nomic-embed-text-v2-moe",
        dim: int = 768,
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.dim = dim
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
                "ollama-embed retry %d/%d after %.1fs: %s",
                attempt + 1,
                _MAX_RETRIES,
                backoff,
                last_exc,
            )
            import asyncio

            await asyncio.sleep(backoff)
        raise RuntimeError("unreachable")  # pragma: no cover

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        results: list[list[float]] = []
        use_model = model or self.model
        for text in texts:
            body = {"model": use_model, "prompt": text}
            resp = await self._request_with_retry("POST", "/api/embeddings", json=body)
            resp.raise_for_status()
            data = resp.json()
            results.append(data["embedding"])
        return results

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
