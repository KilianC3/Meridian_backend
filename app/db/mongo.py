from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client: AsyncIOMotorClient[Any] | None = None


async def init_client() -> AsyncIOMotorClient[Any]:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongo_dsn)
    return client


async def ping() -> bool:
    try:
        cl = await init_client()
        await cl.admin.command("ping")
        return True
    except Exception:
        return False
