from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.commodities.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.commodities.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.commodities.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.commodities.db.fetch_all", new_callable=MagicMock)
def test_get_commodity_prices(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [{"ts": "2024-01-01", "price": 75.0, "unit": "USD/bbl"}]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/commodities", params={"code": "WTI"})
    assert resp.status_code == 200
    assert resp.json() == {
        "data": [{"ts": "2024-01-01", "price": 75.0, "unit": "USD/bbl"}],
        "count": 1,
    }
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()


@patch("app.api.routers.commodities.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.commodities.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.commodities.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.commodities.db.fetch_all", new_callable=MagicMock)
def test_get_bdi_index(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [{"ts": "2024-01-01", "value": 1000.0, "source": "test"}]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/freight/bdi")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
