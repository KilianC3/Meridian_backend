from __future__ import annotations

import os
from importlib import reload
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self.store[key] = self.store.get(key, 0) + 1
        return self.store[key]

    async def expire(self, key: str, ttl: int) -> None:  # noqa: ARG002
        return None


@patch("app.api.deps.redis.init_client", new_callable=AsyncMock)
def test_rate_limiting(redis_client: AsyncMock) -> None:
    redis_client.return_value = FakeRedis()
    for _ in range(5):
        resp = client.get("/healthz")
        assert resp.status_code == 200
    resp = client.get("/healthz")
    assert resp.status_code == 429
    data = resp.json()
    assert data["detail"]["message"] == "Too Many Requests"


@patch("app.api.deps.redis.init_client", new_callable=AsyncMock)
def test_security_headers(redis_client: AsyncMock) -> None:
    redis_client.return_value = FakeRedis()
    resp = client.get("/healthz")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["referrer-policy"] == "same-origin"


@patch.dict(os.environ, {"CORS_ORIGINS": "[\"https://allowed.com\"]"})
def test_cors_allowlist() -> None:
    import app.core.config as config
    reload(config)
    import app.main as main
    reload(main)
    with patch(
        "app.api.deps.redis.init_client", new_callable=AsyncMock
    ) as redis_client:
        redis_client.return_value = FakeRedis()
        test_client = TestClient(main.app)
        preflight = test_client.options(
            "/healthz",
            headers={
                "Origin": "https://allowed.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert preflight.headers["access-control-allow-origin"] == "https://allowed.com"
        preflight = test_client.options(
            "/healthz",
            headers={
                "Origin": "https://evil.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in preflight.headers
