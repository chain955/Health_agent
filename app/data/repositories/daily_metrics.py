"""Repository for daily_metrics."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.dto import DailyMetricsDTO
from app.data.models import DailyMetrics


class DailyMetricsRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: uuid.UUID, iso_date: date) -> DailyMetricsDTO | None:
        result = await self.session.execute(
            select(DailyMetrics).where(
                DailyMetrics.user_id == user_id, DailyMetrics.iso_date == iso_date
            )
        )
        row = result.scalar_one_or_none()
        return DailyMetricsDTO.model_validate(row) if row else None

    async def get_range(self, user_id: uuid.UUID, start: date, end: date) -> list[DailyMetricsDTO]:
        stmt = (
            select(DailyMetrics)
            .where(
                DailyMetrics.user_id == user_id,
                DailyMetrics.iso_date >= start,
                DailyMetrics.iso_date <= end,
            )
            .order_by(DailyMetrics.iso_date)
        )
        result = await self.session.execute(stmt)
        return [DailyMetricsDTO.model_validate(m) for m in result.scalars().all()]

    async def upsert_many(self, metrics: list[DailyMetricsDTO]) -> None:
        if not metrics:
            return
        rows = [m.model_dump() for m in metrics]
        stmt = pg_insert(DailyMetrics).values(rows)
        update_cols = {
            c.name: stmt.excluded[c.name]
            for c in DailyMetrics.__table__.columns
            if c.name not in {"id", "user_id", "iso_date", "created_at"}
        }
        stmt = stmt.on_conflict_do_update(constraint="uq_daily_metrics_user_date", set_=update_cols)
        await self.session.execute(stmt)

    async def summary(self, user_id: uuid.UUID, start: date, end: date) -> dict[str, Any]:
        """SQL-level aggregation of metrics for a date range."""
        stmt = select(
            func.avg(DailyMetrics.recovery_score).label("avg_recovery"),
            func.avg(DailyMetrics.resting_heart_rate).label("avg_resting_hr"),
            func.avg(DailyMetrics.hrv_rmssd_milli).label("avg_hrv"),
            func.avg(DailyMetrics.sleep_total_in_bed_time_milli).label("avg_sleep_milli"),
        ).where(
            DailyMetrics.user_id == user_id,
            DailyMetrics.iso_date >= start,
            DailyMetrics.iso_date <= end,
        )
        result = await self.session.execute(stmt)
        row = result.one()
        avg_sleep_milli = row.avg_sleep_milli
        avg_sleep_minutes: float | None = None
        if avg_sleep_milli is not None:
            avg_sleep_minutes = float(avg_sleep_milli) / 60_000.0
        return {
            "avg_recovery": float(row.avg_recovery) if row.avg_recovery is not None else None,
            "avg_resting_hr": float(row.avg_resting_hr) if row.avg_resting_hr is not None else None,
            "avg_hrv": float(row.avg_hrv) if row.avg_hrv is not None else None,
            "avg_sleep_minutes": avg_sleep_minutes,
        }

    async def delete_by_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(delete(DailyMetrics).where(DailyMetrics.user_id == user_id))
