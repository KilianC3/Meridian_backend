from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.cb.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.cb.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.cb.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.cb.db.fetch_all", new_callable=MagicMock)
def test_get_cb_statements(fetch_all: MagicMock, fetch_one: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "statement_id": 1,
            "central_bank": "FED",
            "type": "decision",
            "published_at": "2024-01-01",
            "title": "Rate Decision",
            "url": "http://example.com",
            "hawkish_dovish_score": None,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/cb", params={"bank": "FED", "type": "decision"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
