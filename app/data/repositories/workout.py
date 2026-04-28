"""Repository for workouts."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.dto import WorkoutDTO
from app.data.models import Workout


class WorkoutRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, workout_id: uuid.UUID) -> WorkoutDTO | None:
        result = await self.session.execute(select(Workout).where(Workout.id == workout_id))
        row = result.scalar_one_or_none()
        return WorkoutDTO.model_validate(row) if row else None

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        since: datetime | None = None,
        until: datetime | None = None,
        sport_type: str | None = None,
        limit: int = 100,
    ) -> list[WorkoutDTO]:
        stmt = select(Workout).where(Workout.user_id == user_id)
        if since is not None:
            stmt = stmt.where(Workout.start_time >= since)
        if until is not None:
            stmt = stmt.where(Workout.start_time < until)
        if sport_type is not None:
            stmt = stmt.where(Workout.sport_type == sport_type)
        stmt = stmt.order_by(Workout.start_time.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return [WorkoutDTO.model_validate(w) for w in result.scalars().all()]

    async def upsert_many(self, workouts: list[WorkoutDTO]) -> None:
        if not workouts:
            return
        rows = [w.model_dump() for w in workouts]
        stmt = pg_insert(Workout).values(rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        await self.session.execute(stmt)

    async def summary(self, user_id: uuid.UUID, since: datetime) -> dict[str, Any]:
        """SQL-level aggregation of workouts since a given timestamp."""
        stmt = select(
            func.count(Workout.id).label("total_workouts"),
            func.coalesce(func.sum(Workout.distance_meters), 0).label("total_distance_meters"),
            func.coalesce(func.sum(Workout.duration_seconds), 0).label("total_duration_seconds"),
        ).where(
            Workout.user_id == user_id,
            Workout.start_time >= since,
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return {
            "total_workouts": int(row.total_workouts),
            "total_distance_meters": int(row.total_distance_meters),
            "total_duration_seconds": int(row.total_duration_seconds),
        }

    async def delete_by_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(delete(Workout).where(Workout.user_id == user_id))
