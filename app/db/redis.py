from __future__ import annotations

import asyncio

import redis.asyncio as aioredis  # type: ignore[import-untyped]

from app.core.config import settings

client: aioredis.Redis | None = None

__all__ = ["init_client", "ping", "client", "aioredis"]


async def init_client() -> aioredis.Redis:
    global client
    if client is None:
        client = aioredis.from_url(
            settings.redis_dsn, decode_responses=True, max_connections=10
        )
    return client


async def ping() -> bool:
    for _ in range(3):
        try:
            cl = await init_client()
            await cl.ping()
            return True
        except Exception:
            await asyncio.sleep(0.1)
    return False
