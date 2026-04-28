"""get_daily_metrics — fetch daily metrics for a single date."""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel

from app.data.dto import DailyMetricsDTO
from app.data.repositories.daily_metrics import DailyMetricsRepo
from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import default_registry


class GetDailyMetricsInput(BaseModel):
    user_id: uuid.UUID
    iso_date: date


class GetDailyMetricsOutput(BaseModel):
    metrics: DailyMetricsDTO | None = None


class GetDailyMetricsTool:
    spec = ToolSpec(
        name="get_daily_metrics",
        description="Получить дневные метрики здоровья пользователя за конкретную дату: шаги, калории, пульс, HRV, восстановление, сон.",
        input_schema=GetDailyMetricsInput,
        output_schema=GetDailyMetricsOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = GetDailyMetricsInput.model_validate(params.model_dump())
        repo = DailyMetricsRepo(ctx.session)
        metrics = await repo.get(inp.user_id, inp.iso_date)
        return GetDailyMetricsOutput(metrics=metrics)


default_registry.register(GetDailyMetricsTool())
