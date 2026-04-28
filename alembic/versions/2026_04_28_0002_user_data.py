"""user_data: users + workouts + daily_metrics

Revision ID: 0002_user_data
Revises: 0001_initial
Create Date: 2026-04-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_user_data"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("bio", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False, server_default="athlete"),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column(
            "sports", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        sa.Column("height_cm", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(), nullable=False, server_default="ru"),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "activities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("unit_system", sa.String(), nullable=False, server_default="metric"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "workouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("sport_type", sa.String(), nullable=False),
        sa.Column("distance_meters", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("avg_speed", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_speed", sa.Numeric(5, 2), nullable=True),
        sa.Column("elevation_meters", sa.Integer(), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=True),
        sa.Column("avg_heart_rate", sa.Integer(), nullable=True),
        sa.Column("max_heart_rate", sa.Integer(), nullable=True),
        sa.Column("source_platform", sa.String(), nullable=False),
        sa.Column("raw_title", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_workouts_user_start", "workouts", ["user_id", "start_time"])
    op.create_index("ix_workouts_user_sport", "workouts", ["user_id", "sport_type"])

    op.create_table(
        "daily_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("iso_date", sa.Date(), nullable=False),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("calories_kcal", sa.Integer(), nullable=True),
        sa.Column("water_liters", sa.Numeric(4, 2), nullable=True),
        sa.Column("hr_avg_bpm", sa.Integer(), nullable=True),
        sa.Column("hr_max_bpm", sa.Integer(), nullable=True),
        sa.Column("recovery_score", sa.Integer(), nullable=True),
        sa.Column("resting_heart_rate", sa.Integer(), nullable=True),
        sa.Column("hrv_rmssd_milli", sa.Numeric(8, 4), nullable=True),
        sa.Column("spo2_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("skin_temp_celsius", sa.Numeric(4, 2), nullable=True),
        sa.Column("sleep_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sleep_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone_offset", sa.Integer(), nullable=True),
        sa.Column("nap", sa.Boolean(), nullable=True),
        sa.Column("sleep_score_state", sa.String(), nullable=True),
        sa.Column("sleep_total_in_bed_time_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_total_awake_time_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_total_no_data_time_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_total_light_sleep_time_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_total_slow_wave_sleep_time_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_total_rem_sleep_time_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_cycle_count", sa.Integer(), nullable=True),
        sa.Column("sleep_disturbance_count", sa.Integer(), nullable=True),
        sa.Column("sleep_needed_baseline_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_needed_from_sleep_debt_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_needed_from_recent_strain_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_needed_from_recent_nap_milli", sa.BigInteger(), nullable=True),
        sa.Column("sleep_respiratory_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("sleep_performance_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("sleep_consistency_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("sleep_efficiency_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("sources_json", sa.String(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "iso_date", name="uq_daily_metrics_user_date"),
    )
    op.create_index("ix_daily_metrics_user_id", "daily_metrics", ["user_id"])
    op.create_index("ix_daily_metrics_iso_date", "daily_metrics", ["iso_date"])


def downgrade() -> None:
    op.drop_index("ix_daily_metrics_iso_date", table_name="daily_metrics")
    op.drop_index("ix_daily_metrics_user_id", table_name="daily_metrics")
    op.drop_table("daily_metrics")
    op.drop_index("ix_workouts_user_sport", table_name="workouts")
    op.drop_index("ix_workouts_user_start", table_name="workouts")
    op.drop_table("workouts")
    op.drop_table("users")
