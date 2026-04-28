"""Shared pytest fixtures."""

import asyncio
import os
from collections.abc import AsyncIterator, Iterator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("LLM_BACKEND", "mock")
os.environ.setdefault("EMBEDDINGS_BACKEND", "mock")
os.environ.setdefault("CHAT_API_KEY", "test_key")
os.environ.setdefault("ADMIN_LOGIN", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "change_me")


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
