from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


async def init_engine() -> AsyncEngine:
    global engine, SessionLocal
    if engine is None:
        engine = create_async_engine(settings.postgres_dsn, pool_pre_ping=True)
        SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    return engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if SessionLocal is None:
        await init_engine()
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session


async def ping() -> bool:
    for _ in range(3):
        try:
            eng = await init_engine()
            async with eng.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            await asyncio.sleep(0.1)
    return False


def run_migrations() -> None:
    cfg = Config(str(Path(__file__).parent / "migrations" / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", settings.postgres_dsn)
    command.upgrade(cfg, "head")
