"""Integration tests requiring a live Postgres + Redis (CI services or local dev)."""

import os

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.skipif(
    os.environ.get("POSTGRES_HOST") in {None, ""},
    reason="needs live postgres / redis (run via CI services or docker compose)",
)


@pytest.mark.asyncio
async def test_health_endpoint_full_stack(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ok", "degraded"}
    names = {c["name"] for c in body["components"]}
    assert {"postgres", "redis", "llm", "embeddings"} <= names


@pytest.mark.asyncio
async def test_seed_runs_via_admin_config(client: AsyncClient) -> None:
    import base64

    creds = base64.b64encode(b"admin:change_me").decode()
    headers = {"Authorization": f"Basic {creds}"}
    # trigger lifespan by hitting any endpoint, then read config
    await client.get("/healthz")
    resp = await client.get("/admin/api/config", headers=headers)
    assert resp.status_code == 200
    config = resp.json()
    assert "llm.backend" in config
    assert "embeddings.dim" in config
