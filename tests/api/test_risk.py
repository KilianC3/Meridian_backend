from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.risk.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.risk.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.risk.db.fetch_all", new_callable=MagicMock)
def test_get_risk_score(
    fetch_all: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {"metric": "macro", "value": 0.2},
        {"metric": "market", "value": 0.3},
        {"metric": "commodity", "value": 0.4},
        {"metric": "geo", "value": 0.1},
        {"metric": "logistics", "value": 0.2},
    ]
    resp = client.get("/v1/risk", params={"country": "USA"})
    assert resp.status_code == 200
    assert resp.json() == {
        "country": "USA",
        "scores": {
            "macro": 0.2,
            "market": 0.3,
            "commodity": 0.4,
            "geo": 0.1,
            "logistics": 0.2,
        },
        "risk": 0.24,
    }
    fetch_all.assert_called_once()


@patch("app.api.routers.risk.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.risk.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.risk.db.fetch_all", new_callable=MagicMock)
def test_get_risk_score_defaults(
    fetch_all: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = []
    resp = client.get("/v1/risk", params={"country": "USA"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk"] == 0.0
    assert body["scores"] == {
        "macro": 0.0,
        "market": 0.0,
        "commodity": 0.0,
        "geo": 0.0,
        "logistics": 0.0,
    }
