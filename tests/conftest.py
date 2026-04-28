"""Shared pytest fixtures."""

import os
from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("LLM_BACKEND", "mock")
os.environ.setdefault("EMBEDDINGS_BACKEND", "mock")
os.environ.setdefault("CHAT_API_KEY", "test_key")
os.environ.setdefault("ADMIN_LOGIN", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "change_me")


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    from app.data.db import dispose_engine
    from app.main import create_app

    # Dispose any engine from a prior test so it doesn't bind to a stale event loop.
    await dispose_engine()

    app = create_app()
    transport = ASGITransport(app=app)
    async with (
        LifespanManager(app),
        AsyncClient(transport=transport, base_url="http://test") as ac,
    ):
        yield ac

    await dispose_engine()
