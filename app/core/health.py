"""Health checks for postgres, redis, llm, embeddings — see spec 14, 19.4."""

import time
from dataclasses import asdict, dataclass

from sqlalchemy import text

from app.core.redis import get_redis
from app.data.db import get_engine
from app.llm import build_embeddings_client, build_llm_client


@dataclass(slots=True)
class ComponentHealth:
    name: str
    healthy: bool
    detail: str | None = None
    latency_ms: float | None = None


async def check_postgres() -> ComponentHealth:
    start = time.perf_counter()
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return ComponentHealth(
            name="postgres",
            healthy=True,
            latency_ms=(time.perf_counter() - start) * 1000,
        )
    except Exception as exc:
        return ComponentHealth(name="postgres", healthy=False, detail=str(exc))


async def check_redis() -> ComponentHealth:
    start = time.perf_counter()
    try:
        client = get_redis()
        await client.ping()
        return ComponentHealth(
            name="redis",
            healthy=True,
            latency_ms=(time.perf_counter() - start) * 1000,
        )
    except Exception as exc:
        return ComponentHealth(name="redis", healthy=False, detail=str(exc))


async def check_llm() -> ComponentHealth:
    client = build_llm_client()
    try:
        status = await client.health()
        return ComponentHealth(
            name="llm",
            healthy=status.healthy,
            detail=status.detail,
            latency_ms=status.latency_ms,
        )
    finally:
        await client.close()


async def check_embeddings() -> ComponentHealth:
    client = build_embeddings_client()
    try:
        status = await client.health()
        return ComponentHealth(
            name="embeddings",
            healthy=status.healthy,
            detail=status.detail,
            latency_ms=status.latency_ms,
        )
    finally:
        await client.close()


async def overall_health() -> dict[str, object]:
    components = [
        await check_postgres(),
        await check_redis(),
        await check_llm(),
        await check_embeddings(),
    ]
    return {
        "status": "ok" if all(c.healthy for c in components) else "degraded",
        "components": [asdict(c) for c in components],
    }
