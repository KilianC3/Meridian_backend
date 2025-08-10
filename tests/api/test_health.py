from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:  # noqa: ARG002
        self.store[key] = value


@patch("app.db.redis.init_client", new_callable=AsyncMock)
@patch("app.db.redis.ping", new_callable=AsyncMock, return_value=True)
@patch("app.api.routers.health.mongo.ping", new_callable=AsyncMock, return_value=True)
@patch("app.api.routers.health.pg.ping", new_callable=AsyncMock, return_value=True)
def test_readiness_ok(
    pg_ping: AsyncMock,
    mongo_ping: AsyncMock,
    redis_ping: AsyncMock,
    redis_client: AsyncMock,
) -> None:  # noqa: ARG001
    redis_client.return_value = FakeRedis()
    response = client.get("/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


@patch("app.db.redis.init_client", new_callable=AsyncMock)
@patch("app.db.redis.ping", side_effect=Exception("fail"))
@patch("app.api.routers.health.mongo.ping", new_callable=AsyncMock, return_value=True)
@patch("app.api.routers.health.pg.ping", new_callable=AsyncMock, return_value=True)
def test_readiness_unhealthy(
    pg_ping: AsyncMock,
    mongo_ping: AsyncMock,
    redis_ping: AsyncMock,
    redis_client: AsyncMock,
) -> None:  # noqa: ARG001
    redis_client.return_value = FakeRedis()
    response = client.get("/readiness")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["redis"]["ok"] is False
