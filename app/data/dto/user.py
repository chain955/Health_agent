"""User DTO."""

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    bio: str | None = None
    role: str = "athlete"
    age: int | None = None
    gender: str | None = None
    sports: list[str] = []
    height_cm: int | None = None
    language: str = "ru"
    weight_kg: Decimal | None = None
    activities: list[str] = []
    unit_system: str = "metric"
