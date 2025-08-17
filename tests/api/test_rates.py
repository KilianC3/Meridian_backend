from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.rates.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.rates.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.rates.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.rates.db.fetch_all", new_callable=MagicMock)
def test_get_rates_series(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [{"ts": "2024-01-01", "value": 4.0, "unit": "percent"}]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/rates",
        params={"series": "us_10y_yield"},
    )
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    assert resp.json()["data"][0]["value"] == 4.0
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
