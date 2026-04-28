from app.config import Settings


def test_database_url_uses_asyncpg() -> None:
    s = Settings(
        postgres_user="u",
        postgres_password="p",
        postgres_host="h",
        postgres_port=5432,
        postgres_db="d",
    )
    assert s.database_url == "postgresql+asyncpg://u:p@h:5432/d"
    assert s.database_url_sync == "postgresql+psycopg://u:p@h:5432/d"


def test_redis_url() -> None:
    s = Settings(redis_host="r", redis_port=6379, redis_db=2)
    assert s.redis_url == "redis://r:6379/2"


def test_defaults_use_mock_backends() -> None:
    s = Settings()
    assert s.llm_backend == "mock"
    assert s.embeddings_backend == "mock"
    assert s.embeddings_dim == 768
