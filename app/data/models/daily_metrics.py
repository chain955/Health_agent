"""Daily metrics ORM — raw external API response per day (Appendix A)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.data.db import Base


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = (UniqueConstraint("user_id", "iso_date", name="uq_daily_metrics_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    iso_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calories_kcal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    water_liters: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    hr_avg_bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hr_max_bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recovery_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resting_heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hrv_rmssd_milli: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    spo2_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    skin_temp_celsius: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)

    sleep_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sleep_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nap: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    sleep_score_state: Mapped[str | None] = mapped_column(String, nullable=True)
    sleep_total_in_bed_time_milli: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sleep_total_awake_time_milli: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sleep_total_no_data_time_milli: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sleep_total_light_sleep_time_milli: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    sleep_total_slow_wave_sleep_time_milli: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    sleep_total_rem_sleep_time_milli: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sleep_cycle_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_disturbance_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_needed_baseline_milli: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sleep_needed_from_sleep_debt_milli: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    sleep_needed_from_recent_strain_milli: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    sleep_needed_from_recent_nap_milli: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    sleep_respiratory_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    sleep_performance_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    sleep_consistency_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    sleep_efficiency_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )

    sources_json: Mapped[str | None] = mapped_column(String, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    raw_payload: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
