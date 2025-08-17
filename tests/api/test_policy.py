from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.policy.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.policy.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.policy.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.policy.db.fetch_all", new_callable=MagicMock)
def test_get_policy_events(fetch_all: MagicMock, fetch_one: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "event_id": 1,
            "jurisdiction": "US",
            "source": "ofac",
            "published_at": "2024-01-01",
            "title": "Sanctions Update",
            "summary": "Details",
            "url": "http://example.com",
            "topics": ["sanctions"],
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/policy", params={"jurisdiction": "US"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
