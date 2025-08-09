from __future__ import annotations

import asyncio
import json
import time
from typing import Any, cast

from fastapi import APIRouter, Response, status
from prometheus_client import REGISTRY, exposition

from app.core.config import settings
from app.db import mongo, pg
from app.db import redis as redis_db

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


async def _ping_with_latency(func: Any) -> tuple[bool, float]:
    start = time.perf_counter()
    try:
        await asyncio.wait_for(func(), timeout=0.2)
        success = True
    except Exception:
        success = False
    latency = (time.perf_counter() - start) * 1000
    return success, latency


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness(response: Response) -> dict[str, Any]:
    cache = await redis_db.init_client()
    cached: str | None = await cache.get("readiness")
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cast(dict[str, Any], json.loads(cached))

    pg_ok, pg_latency = await _ping_with_latency(pg.ping)
    mongo_ok, mongo_latency = await _ping_with_latency(mongo.ping)
    redis_ok, redis_latency = await _ping_with_latency(redis_db.ping)

    status_ok = pg_ok and mongo_ok and redis_ok
    if not status_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    payload = {
        "status": "ok" if status_ok else "error",
        "postgres": {"ok": pg_ok, "latency_ms": pg_latency},
        "mongo": {"ok": mongo_ok, "latency_ms": mongo_latency},
        "redis": {"ok": redis_ok, "latency_ms": redis_latency},
    }
    await cache.setex("readiness", 5, json.dumps(payload))
    return payload


@router.get("/version")
async def version() -> dict[str, str]:
    return {"version": settings.version}


@router.get("/metrics")
async def metrics() -> Response:
    data = exposition.generate_latest(REGISTRY)
    return Response(content=data, media_type="text/plain")
