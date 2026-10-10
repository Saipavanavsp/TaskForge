from fastapi import APIRouter, Response, status
from app.db.session import check_db_connection
from app.services.redis_service import redis_service

router = APIRouter(prefix="/healthz", tags=["Health Checks"])


@router.get("/liveness")
async def liveness():
    """Liveness probe: verifies that the web service process is alive."""
    return {"status": "ok", "probe": "liveness"}


@router.get("/readiness")
async def readiness(response: Response):
    """Readiness probe: verifies PostgreSQL DB connection and Redis ping."""
    db_ok = await check_db_connection()
    redis_ok = await redis_service.ping()

    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    response.status_code = status_code

    return {
        "status": "ready" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "unreachable",
        "redis": "connected" if redis_ok else "unreachable_or_fallback"
    }
