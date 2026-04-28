"""Workout DTO."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WorkoutDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    sport_type: str
    distance_meters: int | None = None
    duration_seconds: int
    start_time: datetime
    end_time: datetime
    avg_speed: Decimal | None = None
    max_speed: Decimal | None = None
    elevation_meters: int | None = None
    calories: int | None = None
    avg_heart_rate: int | None = None
    max_heart_rate: int | None = None
    source_platform: str
    raw_title: str | None = None
