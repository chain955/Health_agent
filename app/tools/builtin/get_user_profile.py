"""get_user_profile — fetch user profile by user_id."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.data.dto import UserDTO
from app.data.repositories.user import UserRepo
from app.tools.base import ToolContext, ToolSpec
from app.tools.registry import default_registry


class GetUserProfileInput(BaseModel):
    user_id: uuid.UUID


class GetUserProfileOutput(BaseModel):
    user: UserDTO | None = None


class GetUserProfileTool:
    spec = ToolSpec(
        name="get_user_profile",
        description="Получить профиль пользователя: имя, возраст, пол, виды спорта, рост, вес, единицы измерения.",
        input_schema=GetUserProfileInput,
        output_schema=GetUserProfileOutput,
    )

    async def run(self, params: BaseModel, ctx: ToolContext) -> BaseModel:
        inp = GetUserProfileInput.model_validate(params.model_dump())
        repo = UserRepo(ctx.session)
        user = await repo.get(inp.user_id)
        return GetUserProfileOutput(user=user)


default_registry.register(GetUserProfileTool())
