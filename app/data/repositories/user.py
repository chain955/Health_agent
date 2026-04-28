"""Repository for users."""

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.dto import UserDTO
from app.data.models import User


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: uuid.UUID) -> UserDTO | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        row = result.scalar_one_or_none()
        return UserDTO.model_validate(row) if row else None

    async def get_all(self) -> list[UserDTO]:
        result = await self.session.execute(select(User).order_by(User.created_at))
        return [UserDTO.model_validate(u) for u in result.scalars().all()]

    async def upsert_many(self, users: list[UserDTO]) -> None:
        if not users:
            return
        rows = [u.model_dump() for u in users]
        stmt = pg_insert(User).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "first_name": stmt.excluded.first_name,
                "last_name": stmt.excluded.last_name,
                "bio": stmt.excluded.bio,
                "role": stmt.excluded.role,
                "age": stmt.excluded.age,
                "gender": stmt.excluded.gender,
                "sports": stmt.excluded.sports,
                "height_cm": stmt.excluded.height_cm,
                "language": stmt.excluded.language,
                "weight_kg": stmt.excluded.weight_kg,
                "activities": stmt.excluded.activities,
                "unit_system": stmt.excluded.unit_system,
            },
        )
        await self.session.execute(stmt)

    async def count(self) -> int:
        result = await self.session.execute(select(User.id))
        return len(result.scalars().all())
