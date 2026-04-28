"""Workout ORM (spec section 6 + Appendix A)."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.data.db import Base


class Workout(Base):
    __tablename__ = "workouts"
    __table_args__ = (
        Index("ix_workouts_user_start", "user_id", "start_time"),
        Index("ix_workouts_user_sport", "user_id", "sport_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    sport_type: Mapped[str] = mapped_column(String, nullable=False)
    distance_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    avg_speed: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_speed: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    elevation_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_platform: Mapped[str] = mapped_column(String, nullable=False)
    raw_title: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
