"""Repository for config_active / config_history."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.models.config import ConfigActive, ConfigHistory


class ConfigRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, key: str) -> Any | None:
        result = await self.session.execute(
            select(ConfigActive.value).where(ConfigActive.key == key)
        )
        row = result.scalar_one_or_none()
        return row

    async def get_all(self) -> dict[str, Any]:
        result = await self.session.execute(select(ConfigActive.key, ConfigActive.value))
        out: dict[str, Any] = {}
        for row in result.all():
            key, value = row
            out[str(key)] = value
        return out

    async def is_empty(self) -> bool:
        result = await self.session.execute(select(ConfigActive.key).limit(1))
        return result.first() is None

    async def upsert_many(self, items: dict[str, Any], updated_by: str = "system") -> None:
        if not items:
            return
        rows = [{"key": k, "value": v, "updated_by": updated_by} for k, v in items.items()]
        stmt = pg_insert(ConfigActive).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["key"],
            set_={"value": stmt.excluded.value, "updated_by": stmt.excluded.updated_by},
        )
        await self.session.execute(stmt)

    async def record_history(
        self,
        changes: list[dict[str, Any]],
        changed_by: str,
        comment: str | None = None,
    ) -> None:
        entry = ConfigHistory(changes=changes, changed_by=changed_by, comment=comment)
        self.session.add(entry)
