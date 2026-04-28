"""Redis client (single shared connection pool)."""

from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

from app.config import get_settings

_redis: Redis[Any] | None = None


def get_redis() -> Redis[Any]:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()  # type: ignore[attr-defined]
    _redis = None
