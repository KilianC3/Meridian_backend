from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.trade.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.trade.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.trade.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.trade.db.fetch_all", new_callable=MagicMock)
def test_get_trade_flows(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "reporter_iso2": "US",
            "partner_iso2": "CN",
            "hs_code": "01",
            "flow": "import",
            "period": "202401",
            "value_usd": 100.0,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/logistics/trade",
        params={"reporter": "US", "partner": "CN", "hs": "01", "flow": "import"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["data"][0]["hs_code"] == "01"
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()
