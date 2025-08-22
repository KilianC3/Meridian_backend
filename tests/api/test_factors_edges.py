from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.risk.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.risk.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.risk.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.risk.db.fetch_all", new_callable=MagicMock)
def test_list_factors(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "factor_id": 1,
            "name": "Oil Prices",
            "series_id": None,
            "note": None,
            "evidence_density": 0.0,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/factors")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()


@patch("app.api.routers.risk.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.risk.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.risk.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.risk.db.fetch_all", new_callable=MagicMock)
def test_list_edges(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "edge_id": 1,
            "src_factor": 1,
            "dst_factor": 2,
            "sign": 1,
            "lag_days": 30,
            "beta": 0.8,
            "p_value": 0.05,
            "transfer_entropy": 0.1,
            "method": "corr",
            "regime": None,
            "confidence": 0.9,
            "sample_start": None,
            "sample_end": None,
            "evidence_count": 1,
            "evidence_density": 0.0,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/edges")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()


@patch("app.api.routers.risk.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.risk.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.risk.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.risk.db.fetch_all", new_callable=MagicMock)
def test_list_risk_snapshots(
    fetch_all: MagicMock,
    fetch_one: MagicMock,
    cache_set: AsyncMock,
    cache_get: AsyncMock,
) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "factor_id": 1,
            "ts": "2024-01-01T00:00:00Z",
            "node_vol": 0.1,
            "node_shock_sigma": 0.1,
            "impact_pct": 0.0,
            "systemic_contrib": 0.0,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get("/v1/risk_snapshots")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()


@patch("app.api.routers.risk.db.fetch_all", new_callable=MagicMock)
def test_simulate_shock(fetch_all: MagicMock) -> None:
    fetch_all.return_value = [
        {
            "src_factor": 1,
            "dst_factor": 2,
            "beta": 0.5,
            "lag_days": 0,
            "confidence": 1.0,
        }
    ]
    resp = client.get(
        "/v1/simulate_shock", params={"factor_id": 1, "shock_size": 1.0, "horizon": 1}
    )
    assert resp.status_code == 200
    assert resp.json()["factor_id"] == 1
    # Decay of 0.7 applied to downstream shock
    assert resp.json()["impacts"] == {"1": 1.0, "2": 0.35}
