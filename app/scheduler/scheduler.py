from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start() -> None:
    scheduler.start()


def shutdown() -> None:
    scheduler.shutdown()
