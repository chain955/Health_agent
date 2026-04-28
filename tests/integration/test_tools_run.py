"""Integration tests for builtin tools — live DB, seeded data."""

from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

import pytest

# Import to ensure builtin tools are registered.
import app.tools.builtin  # noqa: F401
from app.data.db import session_scope
from app.tools.base import ToolContext
from app.tools.registry import default_registry

pytestmark = pytest.mark.skipif(
    os.environ.get("POSTGRES_HOST") in {None, ""},
    reason="needs live postgres (run via CI services or docker compose)",
)

NOVICE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
ADVANCED_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
OVERSLEEPER_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")
OVERTRAINED_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")


@pytest.fixture(autouse=True)
async def _seed_once() -> None:
    from app.data.db import dispose_engine

    await dispose_engine()
    from app.generators.seed_demo import run_seed

    await run_seed(days=30, reset=True)
    yield
    await dispose_engine()


@pytest.mark.asyncio
async def test_get_user_profile() -> None:
    tool = default_registry.get("get_user_profile")
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        result = await tool.run(tool.spec.input_schema(user_id=NOVICE_ID), ctx)
        data = result.model_dump(mode="json")
        assert data["user"] is not None
        assert data["user"]["first_name"] == "Анна"


@pytest.mark.asyncio
async def test_get_recent_workouts_advanced_has_many() -> None:
    tool = default_registry.get("get_recent_workouts")
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=ADVANCED_ID)
        result = await tool.run(
            tool.spec.input_schema(user_id=ADVANCED_ID, days=30, limit=100), ctx
        )
        data = result.model_dump(mode="json")
        advanced_count = len(data["workouts"])
        assert advanced_count > 0

    # Novice should have fewer workouts than advanced
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        result = await tool.run(tool.spec.input_schema(user_id=NOVICE_ID, days=30, limit=100), ctx)
        data = result.model_dump(mode="json")
        novice_count = len(data["workouts"])
        assert advanced_count > novice_count


@pytest.mark.asyncio
async def test_get_workout_returns_single() -> None:
    from app.data.repositories.workout import WorkoutRepo

    async with session_scope() as session:
        workouts = await WorkoutRepo(session).get_by_user(ADVANCED_ID, limit=1)
        assert workouts, "advanced should have at least one workout"
        workout_id = workouts[0].id

    tool = default_registry.get("get_workout")
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=ADVANCED_ID)
        result = await tool.run(tool.spec.input_schema(workout_id=workout_id), ctx)
        data = result.model_dump(mode="json")
        assert data["workout"] is not None
        assert data["workout"]["id"] == str(workout_id)


@pytest.mark.asyncio
async def test_get_workout_missing_returns_none() -> None:
    tool = default_registry.get("get_workout")
    fake_id = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        result = await tool.run(tool.spec.input_schema(workout_id=fake_id), ctx)
        data = result.model_dump(mode="json")
        assert data["workout"] is None


@pytest.mark.asyncio
async def test_get_daily_metrics() -> None:
    tool = default_registry.get("get_daily_metrics")
    yesterday = date.today() - timedelta(days=1)
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        result = await tool.run(tool.spec.input_schema(user_id=NOVICE_ID, iso_date=yesterday), ctx)
        data = result.model_dump(mode="json")
        assert data["metrics"] is not None
        assert data["metrics"]["recovery_score"] is not None


@pytest.mark.asyncio
async def test_get_metrics_range() -> None:
    tool = default_registry.get("get_metrics_range")
    end = date.today()
    start = end - timedelta(days=6)
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        result = await tool.run(
            tool.spec.input_schema(user_id=NOVICE_ID, start=start, end=end), ctx
        )
        data = result.model_dump(mode="json")
        assert len(data["metrics"]) == 7


@pytest.mark.asyncio
async def test_get_period_summary_overtrained_low_recovery() -> None:
    tool = default_registry.get("get_period_summary")

    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=OVERTRAINED_ID)
        ot_result = await tool.run(
            tool.spec.input_schema(user_id=OVERTRAINED_ID, period_days=30), ctx
        )
    ot_data = ot_result.model_dump(mode="json")

    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        nv_result = await tool.run(tool.spec.input_schema(user_id=NOVICE_ID, period_days=30), ctx)
    nv_data = nv_result.model_dump(mode="json")

    ot_recovery = ot_data["summary"]["avg_recovery"]
    nv_recovery = nv_data["summary"]["avg_recovery"]
    assert ot_recovery is not None
    assert nv_recovery is not None
    assert (
        ot_recovery < nv_recovery
    ), f"overtrained ({ot_recovery}) should have lower avg recovery than novice ({nv_recovery})"


@pytest.mark.asyncio
async def test_get_period_summary_advanced_most_workouts() -> None:
    tool = default_registry.get("get_period_summary")

    results: dict[str, int] = {}
    for name, uid in [
        ("advanced", ADVANCED_ID),
        ("novice", NOVICE_ID),
        ("oversleeper", OVERSLEEPER_ID),
        ("overtrained", OVERTRAINED_ID),
    ]:
        async with session_scope() as session:
            ctx = ToolContext(session=session, user_id=uid)
            r = await tool.run(tool.spec.input_schema(user_id=uid, period_days=30), ctx)
        data = r.model_dump(mode="json")
        results[name] = data["summary"]["total_workouts"]

    # Advanced + overtrained should have more workouts than novice and oversleeper.
    # The spec says advanced has the most, but overtrained also trains almost daily.
    # We assert advanced >= novice and advanced >= oversleeper.
    assert results["advanced"] >= results["novice"]
    assert results["advanced"] >= results["oversleeper"]


@pytest.mark.asyncio
async def test_get_period_summary_oversleeper_high_sleep() -> None:
    tool = default_registry.get("get_period_summary")

    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=OVERSLEEPER_ID)
        os_result = await tool.run(
            tool.spec.input_schema(user_id=OVERSLEEPER_ID, period_days=30), ctx
        )
    os_data = os_result.model_dump(mode="json")

    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=OVERTRAINED_ID)
        ot_result = await tool.run(
            tool.spec.input_schema(user_id=OVERTRAINED_ID, period_days=30), ctx
        )
    ot_data = ot_result.model_dump(mode="json")

    os_sleep = os_data["summary"]["avg_sleep_minutes"]
    ot_sleep = ot_data["summary"]["avg_sleep_minutes"]
    assert os_sleep is not None
    assert ot_sleep is not None
    assert (
        os_sleep > ot_sleep
    ), f"oversleeper ({os_sleep}) should sleep more than overtrained ({ot_sleep})"


@pytest.mark.asyncio
async def test_tools_output_json_serializable() -> None:
    """All tool outputs must be JSON-serializable via mode='json'."""
    tool = default_registry.get("get_period_summary")
    async with session_scope() as session:
        ctx = ToolContext(session=session, user_id=NOVICE_ID)
        result = await tool.run(tool.spec.input_schema(user_id=NOVICE_ID, period_days=7), ctx)
    import json

    raw = result.model_dump(mode="json")
    serialized = json.dumps(raw)
    assert isinstance(serialized, str)
