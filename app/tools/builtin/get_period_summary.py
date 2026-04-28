"""get_period_summary — aggregated stats over a period (SQL-level)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from pydantic import BaseModel, Field

from app.data.repositories.daily_metrics import DailyMetricsRepo
from app.data.repositories.workout import WorkoutRepo
from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import default_registry


class GetPeriodSummaryInput(BaseModel):
    user_id: uuid.UUID
    period_days: int = Field(default=7, ge=1, le=365)


class PeriodSummaryDTO(BaseModel):
    avg_recovery: float | None = None
    avg_resting_hr: float | None = None
    avg_hrv: float | None = None
    total_workouts: int = 0
    total_distance_meters: int = 0
    total_duration_seconds: int = 0
    avg_sleep_minutes: float | None = None


class GetPeriodSummaryOutput(BaseModel):
    summary: PeriodSummaryDTO


class GetPeriodSummaryTool:
    spec = ToolSpec(
        name="get_period_summary",
        description="Получить сводную статистику пользователя за период: среднее восстановление, средний пульс покоя, средний HRV, общее количество тренировок, общая дистанция и длительность, средний сон.",
        input_schema=GetPeriodSummaryInput,
        output_schema=GetPeriodSummaryOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = GetPeriodSummaryInput.model_validate(params.model_dump())
        now = datetime.now(tz=UTC)
        end_date = date.today()
        start_date = end_date - timedelta(days=inp.period_days - 1)
        since_dt = now - timedelta(days=inp.period_days)

        metrics_repo = DailyMetricsRepo(ctx.session)
        workout_repo = WorkoutRepo(ctx.session)

        metrics_agg = await metrics_repo.summary(inp.user_id, start_date, end_date)
        workout_agg = await workout_repo.summary(inp.user_id, since_dt)

        summary = PeriodSummaryDTO(
            avg_recovery=metrics_agg["avg_recovery"],
            avg_resting_hr=metrics_agg["avg_resting_hr"],
            avg_hrv=metrics_agg["avg_hrv"],
            total_workouts=workout_agg["total_workouts"],
            total_distance_meters=workout_agg["total_distance_meters"],
            total_duration_seconds=workout_agg["total_duration_seconds"],
            avg_sleep_minutes=metrics_agg["avg_sleep_minutes"],
        )
        return GetPeriodSummaryOutput(summary=summary)


default_registry.register(GetPeriodSummaryTool())
