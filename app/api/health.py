"""Public health endpoint — no auth, for k8s/docker readiness probes."""

from fastapi import APIRouter

from app.core.health import overall_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, object]:
    return await overall_health()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
