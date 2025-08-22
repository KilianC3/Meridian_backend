from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, cast

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.db import mongo, pg
from app.db import redis as redis_db
from ingestion.registry import load_registry


def _cadence_seconds(cadence: str) -> int:
    return {
        "15m": 900,
        "hourly": 3600,
        "daily": 86400,
        "monthly": 30 * 86400,
    }.get(cadence, 3600)


router = APIRouter()


@router.get("/healthz")  # type: ignore[misc]
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


async def _ping_with_latency(func: Any) -> tuple[bool, float]:
    start = time.perf_counter()
    try:
        await asyncio.wait_for(func(), timeout=settings.ping_timeout)
        success = True
    except Exception:
        success = False
    latency = (time.perf_counter() - start) * 1000
    return success, latency


@router.get("/readiness", status_code=status.HTTP_200_OK)  # type: ignore[misc]
async def readiness(response: Response) -> dict[str, Any]:
    cache = await redis_db.init_client()
    cached: str | None = await cache.get("readiness")
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cast(dict[str, Any], json.loads(cached))

    pg_task = _ping_with_latency(pg.ping)
    mongo_task = _ping_with_latency(mongo.ping)
    redis_task = _ping_with_latency(redis_db.ping)
    pg_res, mongo_res, redis_res = await asyncio.gather(pg_task, mongo_task, redis_task)
    pg_ok, pg_latency = pg_res
    mongo_ok, mongo_latency = mongo_res
    redis_ok, redis_latency = redis_res

    registry = load_registry()
    datasets_status: dict[str, Any] = {}
    now = datetime.now(timezone.utc).timestamp()
    for ds_id, cfg in registry.get("datasets", {}).items():
        if not cfg.get("enabled"):
            continue
        cadence_sec = _cadence_seconds(cfg["cadence"])
        last = await cache.get(f"ingest:{ds_id}:ts")
        ok = False
        last_run = None
        if last is not None:
            last_run = float(last)
            ok = now - last_run <= cadence_sec * 2
        datasets_status[ds_id] = {"ok": ok, "last_run": last_run}

    status_ok = (
        pg_ok
        and mongo_ok
        and redis_ok
        and all(d["ok"] for d in datasets_status.values())
    )
    if not status_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    payload = {
        "status": "ok" if status_ok else "error",
        "postgres": {"ok": pg_ok, "latency_ms": pg_latency},
        "mongo": {"ok": mongo_ok, "latency_ms": mongo_latency},
        "redis": {"ok": redis_ok, "latency_ms": redis_latency},
        "datasets": datasets_status,
    }
    await cache.setex("readiness", settings.readiness_cache_ttl, json.dumps(payload))
    return payload


@router.get("/version")  # type: ignore[misc]
async def version() -> dict[str, str]:
    return {
        "version": settings.version,
        "git_sha": settings.git_sha,
        "build_time": settings.build_time,
    }
