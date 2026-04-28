"""Integration tests for user_data tables and seed generator (live DB required)."""

import os
import uuid
from datetime import date, datetime, timedelta

import pytest

from app.data.db import session_scope
from app.data.repositories import DailyMetricsRepo, UserRepo, WorkoutRepo

pytestmark = pytest.mark.skipif(
    os.environ.get("POSTGRES_HOST") in {None, ""},
    reason="needs live postgres / redis (run via CI services or docker compose)",
)


@pytest.fixture(autouse=True)
async def _reset_engine_per_test() -> None:
    """Pytest-asyncio gives each test its own event loop; ensure the cached
    AsyncEngine doesn't leak across loops."""
    from app.data.db import dispose_engine

    await dispose_engine()
    yield
    await dispose_engine()


@pytest.mark.asyncio
async def test_seed_demo_persists_four_personas() -> None:
    from app.generators.seed_demo import run_seed

    counts = await run_seed(days=14, reset=True)
    assert counts["users"] == 4
    assert counts["daily_metrics"] == 4 * 14
    assert counts["workouts"] >= 4  # at least one per persona over 14 days

    async with session_scope() as session:
        users = await UserRepo(session).get_all()
        assert {u.first_name for u in users} == {"Анна", "Дмитрий", "Мария", "Игорь"}


@pytest.mark.asyncio
async def test_workout_repo_filters_by_sport_and_date() -> None:
    from app.generators.seed_demo import run_seed

    await run_seed(days=14, reset=True)
    advanced_id = uuid.UUID("22222222-2222-2222-2222-222222222222")

    async with session_scope() as session:
        repo = WorkoutRepo(session)
        all_w = await repo.get_by_user(advanced_id, limit=500)
        running_only = await repo.get_by_user(advanced_id, sport_type="running", limit=500)
        assert all_w
        assert all(w.sport_type == "running" for w in running_only)
        assert len(running_only) <= len(all_w)

        recent_window_start = datetime(2026, 4, 20, tzinfo=all_w[0].start_time.tzinfo)
        recent = await repo.get_by_user(advanced_id, since=recent_window_start, limit=500)
        assert all(w.start_time >= recent_window_start for w in recent)


@pytest.mark.asyncio
async def test_daily_metrics_repo_get_range() -> None:
    from app.generators.seed_demo import run_seed

    await run_seed(days=14, reset=True)
    novice_id = uuid.UUID("11111111-1111-1111-1111-111111111111")

    async with session_scope() as session:
        repo = DailyMetricsRepo(session)
        end = date(2026, 4, 28)
        start = end - timedelta(days=6)
        days = await repo.get_range(novice_id, start, end)
        assert len(days) == 7
        assert days[0].iso_date == start
        assert days[-1].iso_date == end


@pytest.mark.asyncio
async def test_run_seed_is_idempotent_without_reset() -> None:
    from app.generators.seed_demo import run_seed

    first = await run_seed(days=10, reset=True)
    second = await run_seed(days=10, reset=False)
    assert first == second

    async with session_scope() as session:
        users = await UserRepo(session).get_all()
        assert len(users) == 4
