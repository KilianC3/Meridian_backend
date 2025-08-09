from __future__ import annotations

import asyncio

from app.db import mongo, pg
from app.db import redis as redis_db


async def status() -> dict[str, bool]:
    pg_ok, mongo_ok, redis_ok = await asyncio.gather(
        pg.ping(), mongo.ping(), redis_db.ping()
    )
    return {"postgres": pg_ok, "mongo": mongo_ok, "redis": redis_ok}
