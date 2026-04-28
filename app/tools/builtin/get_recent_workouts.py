"""get_recent_workouts — list recent workouts for a user."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from app.data.dto import WorkoutDTO
from app.data.repositories.workout import WorkoutRepo
from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import default_registry


class GetRecentWorkoutsInput(BaseModel):
    user_id: uuid.UUID
    days: int = Field(default=7, ge=1, le=365)
    sport_type: str | None = None
    limit: int = Field(default=20, ge=1, le=100)


class GetRecentWorkoutsOutput(BaseModel):
    workouts: list[WorkoutDTO]


class GetRecentWorkoutsTool:
    spec = ToolSpec(
        name="get_recent_workouts",
        description="Получить список последних тренировок пользователя за указанный период. Можно фильтровать по виду спорта.",
        input_schema=GetRecentWorkoutsInput,
        output_schema=GetRecentWorkoutsOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = GetRecentWorkoutsInput.model_validate(params.model_dump())
        repo = WorkoutRepo(ctx.session)
        since = datetime.now(tz=UTC) - timedelta(days=inp.days)
        workouts = await repo.get_by_user(
            user_id=inp.user_id,
            since=since,
            sport_type=inp.sport_type,
            limit=inp.limit,
        )
        return GetRecentWorkoutsOutput(workouts=workouts)


default_registry.register(GetRecentWorkoutsTool())
