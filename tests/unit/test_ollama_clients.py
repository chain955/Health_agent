"""Tests for Ollama LLM and Embeddings clients using respx to mock httpx."""

import json

import httpx
import pytest
import respx

from app.llm.base import ChatMessage
from app.llm.ollama import OllamaLLMClient
from app.llm.ollama_embeddings import OllamaEmbeddingsClient

BASE = "http://ollama-test:11434"


# ---------------------------------------------------------------------------
# OllamaLLMClient — chat
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_happy_path() -> None:
    with respx.mock(base_url=BASE) as router:
        router.post("/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={
                    "message": {"role": "assistant", "content": "Hello!"},
                    "done": True,
                    "done_reason": "stop",
                    "prompt_eval_count": 10,
                    "eval_count": 5,
                },
            )
        )
        client = OllamaLLMClient(base_url=BASE, model="test-model")
        try:
            resp = await client.chat([ChatMessage(role="user", content="hi")])
            assert resp.content == "Hello!"
            assert resp.finish_reason == "stop"
            assert resp.usage == {"prompt_tokens": 10, "completion_tokens": 5}
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_chat_request_body_shape() -> None:
    with respx.mock(base_url=BASE) as router:
        route = router.post("/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={"message": {"content": "ok"}, "done": True},
            )
        )
        client = OllamaLLMClient(base_url=BASE, model="llama3")
        try:
            await client.chat(
                [ChatMessage(role="system", content="sys"), ChatMessage(role="user", content="q")],
                temperature=0.5,
                top_p=0.9,
                max_tokens=100,
                seed=42,
            )
            request = route.calls.last.request
            body = json.loads(request.content)
            assert body["model"] == "llama3"
            assert body["stream"] is False
            assert body["messages"] == [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "q"},
            ]
            assert body["options"]["temperature"] == 0.5
            assert body["options"]["top_p"] == 0.9
            assert body["options"]["num_predict"] == 100
            assert body["options"]["seed"] == 42
        finally:
            await client.close()


# ---------------------------------------------------------------------------
# OllamaLLMClient — stream
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_yields_tokens() -> None:
    chunks = [
        json.dumps({"message": {"content": "Hello"}, "done": False}),
        json.dumps({"message": {"content": " world"}, "done": False}),
        json.dumps({"message": {"content": ""}, "done": True}),
    ]
    ndjson = "\n".join(chunks)

    with respx.mock(base_url=BASE) as router:
        router.post("/api/chat").mock(return_value=httpx.Response(200, text=ndjson))
        client = OllamaLLMClient(base_url=BASE, model="test-model")
        try:
            tokens = [t async for t in client.stream([ChatMessage(role="user", content="hi")])]
            assert tokens == ["Hello", " world"]
        finally:
            await client.close()


# ---------------------------------------------------------------------------
# OllamaLLMClient — health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_returns_true_on_200() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/tags").mock(return_value=httpx.Response(200, json={"models": []}))
        client = OllamaLLMClient(base_url=BASE)
        try:
            status = await client.health()
            assert status.healthy is True
            assert status.backend == "ollama"
            assert status.latency_ms is not None
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_health_returns_false_on_non_200() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/tags").mock(return_value=httpx.Response(503, text="unavailable"))
        client = OllamaLLMClient(base_url=BASE)
        try:
            status = await client.health()
            assert status.healthy is False
            assert "503" in (status.detail or "")
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_health_returns_false_on_connection_error() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/tags").mock(side_effect=httpx.ConnectError("refused"))
        client = OllamaLLMClient(base_url=BASE)
        try:
            status = await client.health()
            assert status.healthy is False
            assert status.detail is not None
        finally:
            await client.close()


# ---------------------------------------------------------------------------
# OllamaEmbeddingsClient — embed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_happy_path() -> None:
    embedding = [0.1] * 768
    with respx.mock(base_url=BASE) as router:
        router.post("/api/embeddings").mock(
            return_value=httpx.Response(200, json={"embedding": embedding})
        )
        client = OllamaEmbeddingsClient(base_url=BASE, dim=768)
        try:
            result = await client.embed(["hello", "world"])
            assert len(result) == 2
            assert len(result[0]) == 768
            assert result[0] == embedding
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_embed_request_shape() -> None:
    embedding = [0.5] * 768
    with respx.mock(base_url=BASE) as router:
        route = router.post("/api/embeddings").mock(
            return_value=httpx.Response(200, json={"embedding": embedding})
        )
        client = OllamaEmbeddingsClient(base_url=BASE, model="nomic", dim=768)
        try:
            await client.embed(["test input"])
            request = route.calls.last.request
            body = json.loads(request.content)
            assert body["model"] == "nomic"
            assert body["prompt"] == "test input"
        finally:
            await client.close()


# ---------------------------------------------------------------------------
# OllamaEmbeddingsClient — health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_health_ok() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/tags").mock(return_value=httpx.Response(200, json={"models": []}))
        client = OllamaEmbeddingsClient(base_url=BASE)
        try:
            status = await client.health()
            assert status.healthy is True
            assert status.backend == "ollama"
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_embed_health_connection_error() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/tags").mock(side_effect=httpx.ConnectError("refused"))
        client = OllamaEmbeddingsClient(base_url=BASE)
        try:
            status = await client.health()
            assert status.healthy is False
        finally:
            await client.close()
