from __future__ import annotations

import redis.asyncio as aioredis

from app.core.config import settings

client: aioredis.Redis | None = None


async def init_client() -> aioredis.Redis:
    global client
    if client is None:
        client = aioredis.from_url(settings.redis_dsn, decode_responses=True)  # type: ignore[no-untyped-call]
    return client


async def ping() -> bool:
    try:
        cl = await init_client()
        await cl.ping()
        return True
    except Exception:
        return False
