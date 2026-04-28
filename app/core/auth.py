"""Authorization dependencies for the three API prefixes — see spec 1.1."""

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import Settings, get_settings

basic_security = HTTPBasic()


def require_chat_api_key(
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> str:
    """API-key in `Authorization: Bearer <key>` for /api/chat (production chat)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    if not secrets.compare_digest(token, settings.chat_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid api key",
        )
    return token


def require_admin(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
    settings: Settings = Depends(get_settings),
) -> str:
    """Basic auth from .env — used for /admin/api and /testchat/api."""
    valid_user = secrets.compare_digest(credentials.username, settings.admin_login)
    valid_pass = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
