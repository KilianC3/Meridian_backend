from __future__ import annotations

import asyncio

from fastapi import APIRouter

from app.db import mongo, pg
from app.db import redis as redis_db

router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.get("/status")  # type: ignore[misc]
async def datasource_status() -> dict[str, bool]:
    pg_ok, mongo_ok, redis_ok = await asyncio.gather(
        pg.ping(), mongo.ping(), redis_db.ping()
    )
    return {"postgres": pg_ok, "mongo": mongo_ok, "redis": redis_ok}
