"""Seed config_active from environment on first start — see spec 15.1."""

import logging
from typing import Any

from app.config import Settings
from app.data.repositories import ConfigRepo

logger = logging.getLogger(__name__)


def seed_payload(settings: Settings) -> dict[str, Any]:
    """Subset of settings persisted to config_active on first boot."""
    return {
        "llm.backend": settings.llm_backend,
        "llm.base_url": settings.llm_base_url,
        "llm.model": settings.llm_model,
        "embeddings.backend": settings.embeddings_backend,
        "embeddings.base_url": settings.embeddings_base_url,
        "embeddings.model": settings.embeddings_model,
        "embeddings.dim": settings.embeddings_dim,
        "pipeline.session_ttl_hours": settings.session_ttl_hours,
        "pipeline.context_history_pairs": settings.context_history_pairs,
        "logging.retention_days": settings.log_retention_days,
        "alerts.webhook_url": settings.alerts_webhook_url,
    }


async def seed_config_if_empty(repo: ConfigRepo, settings: Settings) -> bool:
    """Write seed values only if config_active is empty. Returns True if seeded."""
    if not await repo.is_empty():
        return False
    payload = seed_payload(settings)
    await repo.upsert_many(payload, updated_by="seed")
    await repo.record_history(
        changes=[{"key": k, "old_value": None, "new_value": v} for k, v in payload.items()],
        changed_by="seed",
        comment="initial seed from .env",
    )
    logger.info("seeded config_active with %d keys", len(payload))
    return True
