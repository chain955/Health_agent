"""Smoke tests against the FastAPI app (no real DB / Redis required for these endpoints)."""

import base64

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_responds(client: AsyncClient) -> None:
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "health-assistant"
    assert body["docs"] == "/api/docs"


@pytest.mark.asyncio
async def test_healthz_no_auth(client: AsyncClient) -> None:
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_openapi_published(client: AsyncClient) -> None:
    resp = await client.get("/api/openapi.json")
    assert resp.status_code == 200
    spec = resp.json()
    paths = spec["paths"]
    assert "/api/chat/ping" in paths
    assert "/admin/api/ping" in paths
    assert "/testchat/api/ping" in paths


@pytest.mark.asyncio
async def test_chat_requires_bearer_token(client: AsyncClient) -> None:
    resp = await client.get("/api/chat/ping")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_accepts_valid_token(client: AsyncClient) -> None:
    resp = await client.get("/api/chat/ping", headers={"Authorization": "Bearer test_key"})
    assert resp.status_code == 200
    assert resp.json()["scope"] == "chat"


@pytest.mark.asyncio
async def test_chat_rejects_invalid_token(client: AsyncClient) -> None:
    resp = await client.get("/api/chat/ping", headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_requires_basic_auth(client: AsyncClient) -> None:
    resp = await client.get("/admin/api/ping")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_accepts_basic_auth(client: AsyncClient) -> None:
    creds = base64.b64encode(b"admin:change_me").decode()
    resp = await client.get("/admin/api/ping", headers={"Authorization": f"Basic {creds}"})
    assert resp.status_code == 200
    assert resp.json()["scope"] == "admin"


@pytest.mark.asyncio
async def test_testchat_requires_basic_auth(client: AsyncClient) -> None:
    resp = await client.get("/testchat/api/ping")
    assert resp.status_code == 401
