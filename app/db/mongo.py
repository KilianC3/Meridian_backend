from __future__ import annotations

import asyncio
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client: AsyncIOMotorClient[Any] | None = None


async def init_client() -> AsyncIOMotorClient[Any]:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongo_dsn, maxPoolSize=10)
    return client


async def ping() -> bool:
    for _ in range(3):
        try:
            cl = await init_client()
            await cl.admin.command("ping")
            return True
        except Exception:
            await asyncio.sleep(0.1)
    return False


async def save_document(doc: dict[str, Any]) -> str:
    """Store a document in MongoDB and return its ID."""
    cl = await init_client()
    result = await cl.meridian.documents.insert_one(doc)
    return str(result.inserted_id)
