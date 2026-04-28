"""Repository for daily_metrics."""

import uuid
from datetime import date

from sqlalchemy import delete, select
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

    async def delete_by_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(delete(DailyMetrics).where(DailyMetrics.user_id == user_id))
