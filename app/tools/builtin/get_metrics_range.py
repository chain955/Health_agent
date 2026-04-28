"""get_metrics_range — fetch daily metrics for a date range."""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel

from app.data.dto import DailyMetricsDTO
from app.data.repositories.daily_metrics import DailyMetricsRepo
from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import default_registry


class GetMetricsRangeInput(BaseModel):
    user_id: uuid.UUID
    start: date
    end: date


class GetMetricsRangeOutput(BaseModel):
    metrics: list[DailyMetricsDTO]


class GetMetricsRangeTool:
    spec = ToolSpec(
        name="get_metrics_range",
        description="Получить дневные метрики здоровья пользователя за диапазон дат: шаги, калории, пульс, HRV, восстановление, сон за каждый день периода.",
        input_schema=GetMetricsRangeInput,
        output_schema=GetMetricsRangeOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = GetMetricsRangeInput.model_validate(params.model_dump())
        repo = DailyMetricsRepo(ctx.session)
        metrics = await repo.get_range(inp.user_id, inp.start, inp.end)
        return GetMetricsRangeOutput(metrics=metrics)


default_registry.register(GetMetricsRangeTool())
