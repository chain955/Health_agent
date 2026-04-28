from app.config import Settings
from app.core.seed import seed_payload


def test_seed_payload_contains_expected_keys() -> None:
    s = Settings()
    payload = seed_payload(s)
    expected = {
        "llm.backend",
        "llm.base_url",
        "llm.model",
        "embeddings.backend",
        "embeddings.base_url",
        "embeddings.model",
        "embeddings.dim",
        "pipeline.session_ttl_hours",
        "pipeline.context_history_pairs",
        "logging.retention_days",
        "alerts.webhook_url",
    }
    assert expected.issubset(payload.keys())
    assert payload["embeddings.dim"] == 768
