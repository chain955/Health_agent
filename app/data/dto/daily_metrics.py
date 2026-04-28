"""Daily metrics DTO."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DailyMetricsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    iso_date: date

    steps: int | None = None
    calories_kcal: int | None = None
    water_liters: Decimal | None = None
    hr_avg_bpm: int | None = None
    hr_max_bpm: int | None = None
    recovery_score: int | None = None
    resting_heart_rate: int | None = None
    hrv_rmssd_milli: Decimal | None = None
    spo2_percentage: Decimal | None = None
    skin_temp_celsius: Decimal | None = None

    sleep_start: datetime | None = None
    sleep_end: datetime | None = None
    timezone_offset: int | None = None
    nap: bool | None = None
    sleep_score_state: str | None = None
    sleep_total_in_bed_time_milli: int | None = None
    sleep_total_awake_time_milli: int | None = None
    sleep_total_no_data_time_milli: int | None = None
    sleep_total_light_sleep_time_milli: int | None = None
    sleep_total_slow_wave_sleep_time_milli: int | None = None
    sleep_total_rem_sleep_time_milli: int | None = None
    sleep_cycle_count: int | None = None
    sleep_disturbance_count: int | None = None
    sleep_needed_baseline_milli: int | None = None
    sleep_needed_from_sleep_debt_milli: int | None = None
    sleep_needed_from_recent_strain_milli: int | None = None
    sleep_needed_from_recent_nap_milli: int | None = None
    sleep_respiratory_rate: Decimal | None = None
    sleep_performance_percentage: Decimal | None = None
    sleep_consistency_percentage: Decimal | None = None
    sleep_efficiency_percentage: Decimal | None = None

    sources_json: str | None = None
    version: int = 1
