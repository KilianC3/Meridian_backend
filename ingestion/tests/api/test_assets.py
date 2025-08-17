from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.assets.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.assets.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.assets.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.assets.db.fetch_all", new_callable=MagicMock)
def test_get_asset_prices(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [{"ts": "2024-01-01", "close": 100.0}]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/assets/prices", params={"symbol": "AAPL"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()


@patch("app.api.routers.assets.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.assets.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.assets.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.assets.db.fetch_all", new_callable=MagicMock)
def test_get_index_prices(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [{"ts": "2024-01-01", "value": 4000.0}]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/assets/indices", params={"index_symbol": "SPX"})
    assert resp.status_code == 200
    assert resp.json()["data"][0]["value"] == 4000.0
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()


@patch("app.api.routers.assets.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.assets.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.assets.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.assets.db.fetch_all", new_callable=MagicMock)
def test_get_fundamentals(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [{"ts": "2024-01-01", "value": 10.0, "unit": "USD"}]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/assets/fundamentals",
        params={"cik": "0000320193", "fact": "Assets"},
    )
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()


@patch("app.api.routers.assets.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.assets.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.assets.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.assets.db.fetch_all", new_callable=MagicMock)
def test_get_earnings_events(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {"cik": "0000320193", "ticker": "AAPL", "ts": "2024-01-01", "headline": "Q1"}
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/assets/earnings",
        params={"cik": "0000320193"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"][0]["ticker"] == "AAPL"
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
