from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.db import mongo, pg
from app.db import redis as redis_db


@pytest.mark.asyncio  # type: ignore[misc]
async def test_pg_init_and_ping(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeConn:
        async def execute(
            self, *args: object, **kwargs: object
        ) -> None:  # noqa: D401, ARG002
            return None

        async def __aenter__(self) -> "FakeConn":
            return self

        async def __aexit__(
            self, exc_type: object, exc: object, tb: object
        ) -> None:  # noqa: ARG002
            return None

    class FakeEngine:
        def connect(self) -> FakeConn:  # noqa: D401
            return FakeConn()

    fake_engine = FakeEngine()
    monkeypatch.setattr(pg, "create_async_engine", lambda *a, **k: fake_engine)
    pg.engine = None
    pg.SessionLocal = None
    eng = await pg.init_engine()
    assert eng is fake_engine
    assert await pg.ping()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_mongo_init_and_ping(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = AsyncMock()
    fake_client.admin.command.return_value = {"ok": 1}
    monkeypatch.setattr(mongo, "AsyncIOMotorClient", lambda *a, **k: fake_client)
    mongo.client = None
    cl = await mongo.init_client()
    assert cl is fake_client
    assert await mongo.ping()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_redis_init_and_ping(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = AsyncMock()
    fake_client.ping.return_value = True
    monkeypatch.setattr(redis_db.aioredis, "from_url", lambda *a, **k: fake_client)
    redis_db.client = None
    cl = await redis_db.init_client()
    assert cl is fake_client
    assert await redis_db.ping()


def test_timescale_extension_present() -> None:
    files = list(Path("app/db/migrations/versions").glob("*.py"))
    assert files
    content = "".join(f.read_text() for f in files)
    assert "CREATE EXTENSION IF NOT EXISTS timescaledb" in content
