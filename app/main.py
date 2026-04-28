"""FastAPI entrypoint — wires routers, lifespan, settings."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.admin.router import router as admin_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.config import get_settings
from app.core.redis import close_redis
from app.core.seed import seed_config_if_empty
from app.data.db import dispose_engine, session_scope
from app.data.repositories import ConfigRepo
from app.testchat.router import router as testchat_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("starting health-assistant %s in %s mode", __version__, settings.app_env)
    try:
        async with session_scope() as session:
            seeded = await seed_config_if_empty(ConfigRepo(session), settings)
            if seeded:
                logger.info("seeded config_active from .env")
    except Exception as exc:
        logger.warning("config seed skipped: %s", exc)
    yield
    await close_redis()
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Health Assistant",
        version=__version__,
        description="Offline AI agent for fitness analytics — see health_assistant_spec.md",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(admin_router)
    app.include_router(testchat_router)

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {
            "service": "health-assistant",
            "version": __version__,
            "env": settings.app_env,
            "docs": "/api/docs",
        }

    return app


app = create_app()
