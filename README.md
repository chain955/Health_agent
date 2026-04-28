# Health Assistant

Offline AI agent for fitness analytics. See `health_assistant_spec.md` for the
full technical spec.

This repo follows the spec section 22 incrementally, one PR per stage. PR 1
ships the project skeleton: docker stack, FastAPI app with three API prefixes,
LLM/embeddings client interfaces (mock), Alembic migrations with pgvector, and
config seed logic.

## Stack

- Python 3.11+
- FastAPI (async)
- PostgreSQL 16 with pgvector
- Redis
- Alembic
- Docker Compose (dev / prod presets)

LLM and embeddings backends (Ollama, vLLM, TEI, Infinity) live **outside** this
compose — see spec section 19.3. PR 1 talks to them through `LLMClient` /
`EmbeddingsClient` interfaces with a mock implementation; OpenAI-compatible and
Ollama clients land in PR 3.

## Quick start (dev)

```bash
make env-dev               # copy .env.example -> .env.dev
make dev                   # build + start agent, postgres, redis
make migrate               # alembic upgrade head (in another shell)
curl http://localhost:8000/health
```

The agent runs on `http://localhost:8000`. OpenAPI docs at `/api/docs`.

To apply code changes in dev: `make restart-agent` (no rebuild needed —
`./app` is mounted as a volume).

## API surface (PR 1 skeleton)

| Prefix | Auth | Purpose |
|---|---|---|
| `/api/chat/...` | `Authorization: Bearer <key>` (API-key from `.env`) | Production chat (mobile / partners) |
| `/admin/api/...` | Basic Auth (`ADMIN_LOGIN` / `ADMIN_PASSWORD`) | Admin UI |
| `/testchat/api/...` | Basic Auth | Test chat (dev only) |
| `/health`, `/healthz` | none | Probes |

PR 1 only ships `/ping` endpoints under the auth-protected prefixes; the full
chat / admin / testchat surfaces land in later PRs.

## Configuration

`.env` is the seed source on first start only. After the first boot, the
`config_active` table in Postgres is the source of truth — see spec 15.1.
Changes via the admin UI require an agent restart to take effect.

### LLM / Embeddings backend selection

Set `LLM_BACKEND` and `EMBEDDINGS_BACKEND` to choose the implementation:

| Value | Description |
|---|---|
| `mock` (default) | Deterministic mock — no network calls, safe for CI. |
| `ollama` | Ollama native API (`/api/chat`, `/api/embeddings`). |
| `vllm` / `tei` / `infinity` | Planned; currently falls back to mock. |

When using `ollama`, configure these variables (in `.env` or admin):

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama server address. |
| `OLLAMA_LLM_MODEL` | `llama3.1:8b` | Chat model name. |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text-v2-moe` | Embeddings model name. |
| `OLLAMA_TIMEOUT_SECONDS` | `30` | HTTP request timeout. |
| `EMBEDDINGS_DIM` | `768` | Vector dimensionality (shared across backends). |

Ollama must be running externally (not in this project's docker-compose).
See spec section 19.3 for network topology.

## Project layout

```
/app
  /api          FastAPI routers (chat, health)
  /pipeline     Context Builder, Intent, Router, Planner (later PRs)
  /tools        Tool registry and implementations (later PRs)
  /rag          Indexing, retrieval (later PRs)
  /llm          LLMClient, EmbeddingsClient + implementations
  /data         ORM models, repositories
  /memory       Sessions, history, summary (later PRs)
  /alerts       Proactive monitoring (later PRs)
  /safety       Blocked classifier (later PRs)
  /i18n         System prompts and templates by locale
  /admin        Admin API
  /testchat     Test chat API
  /generators   Deterministic test data (later PRs)
  /core         Health checks, auth, redis, seed
  /config       Settings (pydantic-settings)
/frontend       React + Vite SPA (later PRs)
/docker         Dockerfile
/alembic        Migrations
/tests          pytest unit + integration
```

## Development

```bash
pip install -e ".[dev]"
pre-commit install
ruff check .
mypy app
pytest
```

## License

Internal project — license TBD.
