"""Test chat API skeleton — `/testchat/api/...`. Full surface lands in PR 9."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import require_admin

router = APIRouter(prefix="/testchat/api", tags=["testchat"])


@router.get("/ping")
async def ping(_: Annotated[str, Depends(require_admin)]) -> dict[str, str]:
    return {"status": "ok", "scope": "testchat"}
