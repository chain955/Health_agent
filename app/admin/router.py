"""Admin API skeleton — `/admin/api/...`. Full surface lands in PR 8."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.core.auth import require_admin
from app.core.health import overall_health
from app.data.db import session_scope
from app.data.repositories import ConfigRepo

router = APIRouter(prefix="/admin/api", tags=["admin"])


@router.get("/ping")
async def ping(_: Annotated[str, Depends(require_admin)]) -> dict[str, str]:
    return {"status": "ok", "scope": "admin"}


@router.get("/health")
async def health(_: Annotated[str, Depends(require_admin)]) -> dict[str, object]:
    return await overall_health()


@router.get("/config")
async def get_config(_: Annotated[str, Depends(require_admin)]) -> dict[str, Any]:
    async with session_scope() as session:
        repo = ConfigRepo(session)
        return await repo.get_all()
