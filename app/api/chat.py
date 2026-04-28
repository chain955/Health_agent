"""Production chat API — `/api/chat/...`. Skeleton for PR 1; pipeline lands in PR 5."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import require_chat_api_key

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/ping")
async def ping(_: Annotated[str, Depends(require_chat_api_key)]) -> dict[str, str]:
    return {"status": "ok", "scope": "chat"}
