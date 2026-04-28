"""Unit tests for tool retrieval — mock embeddings, top-k ordering."""

from __future__ import annotations

import pytest

# Ensure builtin tools are registered.
import app.tools.builtin  # noqa: F401
from app.llm.mock import MockEmbeddingsClient
from app.tools.registry import default_registry
from app.tools.retrieval import ToolRetriever


@pytest.fixture
def retriever() -> ToolRetriever:
    client = MockEmbeddingsClient(dim=768)
    return ToolRetriever(default_registry, client)


@pytest.mark.asyncio
async def test_select_tools_returns_k_results(retriever: ToolRetriever) -> None:
    results = await retriever.select_tools("покажи профиль", k=3)
    assert len(results) <= 3
    assert len(results) > 0


@pytest.mark.asyncio
async def test_select_tools_workout_query(retriever: ToolRetriever) -> None:
    results = await retriever.select_tools("сколько я пробежал на этой неделе", k=3)
    names = [s.name for s in results]
    assert any(n in names for n in ("get_recent_workouts", "get_period_summary")), (
        f"expected workout/period tool in top-3 but got {names}"
    )


@pytest.mark.asyncio
async def test_select_tools_metrics_query(retriever: ToolRetriever) -> None:
    results = await retriever.select_tools(
        "какой у меня пульс покоя и HRV за последнюю неделю", k=3
    )
    names = [s.name for s in results]
    assert any(
        n in names for n in ("get_metrics_range", "get_period_summary", "get_daily_metrics")
    ), f"expected metrics-related tool in top-3 but got {names}"


@pytest.mark.asyncio
async def test_select_tools_profile_query(retriever: ToolRetriever) -> None:
    results = await retriever.select_tools("покажи мой профиль", k=3)
    names = [s.name for s in results]
    assert "get_user_profile" in names, f"expected get_user_profile in top-3 but got {names}"


@pytest.mark.asyncio
async def test_cache_invalidation(retriever: ToolRetriever) -> None:
    await retriever.select_tools("test", k=1)
    assert not retriever._is_stale()
    # Simulate version bump
    retriever._cache_version = -1
    assert retriever._is_stale()


@pytest.mark.asyncio
async def test_select_tools_sleep_query(retriever: ToolRetriever) -> None:
    results = await retriever.select_tools("сколько я спал в среднем за неделю", k=3)
    names = [s.name for s in results]
    assert any(
        n in names for n in ("get_period_summary", "get_metrics_range", "get_daily_metrics")
    ), f"expected sleep-related tool in top-3 but got {names}"
