"""get_workout — fetch a single workout by ID."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.data.dto import WorkoutDTO
from app.data.repositories.workout import WorkoutRepo
from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import default_registry


class GetWorkoutInput(BaseModel):
    workout_id: uuid.UUID


class GetWorkoutOutput(BaseModel):
    workout: WorkoutDTO | None = None


class GetWorkoutTool:
    spec = ToolSpec(
        name="get_workout",
        description="Получить данные одной тренировки по её идентификатору: дистанция, длительность, пульс, скорость.",
        input_schema=GetWorkoutInput,
        output_schema=GetWorkoutOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = GetWorkoutInput.model_validate(params.model_dump())
        repo = WorkoutRepo(ctx.session)
        workout = await repo.get(inp.workout_id)
        return GetWorkoutOutput(workout=workout)


default_registry.register(GetWorkoutTool())
