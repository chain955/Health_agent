"""Tool base classes and context — see spec section 5."""

from __future__ import annotations

import uuid
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class ToolContext(BaseModel):
    """Per-request context passed to every tool invocation."""

    class Config:
        arbitrary_types_allowed = True

    session: AsyncSession
    user_id: uuid.UUID
    metadata: dict[str, Any] = {}


class ToolSpec(BaseModel):
    """Declarative description of a tool (name, description, schemas)."""

    name: str
    description: str
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]

    class Config:
        arbitrary_types_allowed = True


@runtime_checkable
class Tool(Protocol):
    spec: ToolSpec

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel: ...
