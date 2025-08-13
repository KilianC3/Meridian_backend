from __future__ import annotations

import asyncio

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio.lock import Lock  # type: ignore[import-untyped]

from app.core.config import settings
from app.db import redis as redis_db

scheduler: AsyncIOScheduler | None = None
lock: Lock | None = None


def get_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        jobstores = {"default": SQLAlchemyJobStore(url=settings.postgres_dsn)}
        scheduler = AsyncIOScheduler(jobstores=jobstores)
    return scheduler


def start() -> None:
    """Start scheduler with a Redis distributed lock."""
    global lock
    sched = get_scheduler()
    loop = asyncio.get_event_loop()

    async def acquire_lock() -> Lock | None:
        client = await redis_db.init_client()
        lk = client.lock("scheduler_lock", timeout=60)
        if await lk.acquire(blocking=False):
            return lk
        return None

    lock = loop.run_until_complete(acquire_lock())
    if lock is None:
        return
    sched.start()


def shutdown() -> None:
    """Shut down scheduler and release Redis lock."""
    global lock
    if scheduler:
        scheduler.shutdown()
    if lock:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(lock.release())
        lock = None
