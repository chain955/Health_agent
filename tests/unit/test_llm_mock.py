import pytest

from app.llm import build_embeddings_client, build_llm_client
from app.llm.base import ChatMessage


@pytest.mark.asyncio
async def test_mock_llm_chat_returns_deterministic_reply() -> None:
    client = build_llm_client()
    try:
        resp = await client.chat([ChatMessage(role="user", content="hi")])
        assert "hi" in resp.content
        assert resp.finish_reason == "stop"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_mock_llm_stream_yields_tokens() -> None:
    client = build_llm_client()
    try:
        chunks = [c async for c in client.stream([ChatMessage(role="user", content="hello")])]
        assert chunks
        assert "".join(chunks).strip()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_mock_llm_health_ok() -> None:
    client = build_llm_client()
    try:
        status = await client.health()
        assert status.healthy is True
        assert status.backend == "mock"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_mock_embeddings_dim_and_determinism() -> None:
    client = build_embeddings_client()
    try:
        v1 = await client.embed(["foo", "bar"])
        v2 = await client.embed(["foo", "bar"])
        assert len(v1) == 2
        assert len(v1[0]) == client.dim == 768
        assert v1 == v2
        # different inputs produce different vectors
        assert v1[0] != v1[1]
    finally:
        await client.close()
