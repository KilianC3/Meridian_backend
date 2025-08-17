from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.fx.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.fx.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.fx.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.fx.db.fetch_all", new_callable=MagicMock)
def test_get_fx_series(fetch_all: MagicMock, fetch_one: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {"ts": "2024-01-01", "value": 1.1, "unit": "USD/EUR"}
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/fx",
        params={"pair": "usd_eur"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"][0]["unit"] == "USD/EUR"
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
