from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.api.routers.ports.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.ports.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.ports.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.ports.db.fetch_all", new_callable=MagicMock)
def test_get_port_series(fetch_all: MagicMock, fetch_one: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "port_id": "LA",
            "vessel_class": "container",
            "ts": "2024-01-01T00:00:00",
            "congestion": 1.0,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/logistics/ports/series",
        params={"port_id": "LA", "vessel_class": "container"},
    )
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()


@patch("app.api.routers.ports.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.ports.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.ports.db.fetch_all", new_callable=MagicMock)
def test_get_port_snapshot(fetch_all: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "port_id": "LA",
            "vessel_class": "container",
            "ts": "2024-01-01T00:00:00",
            "congestion": 1.0,
        }
    ]
    resp = client.get(
        "/v1/logistics/ports/snapshot",
        params={"port_id": "LA", "vessel_class": "container"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"][0]["port_id"] == "LA"
    fetch_all.assert_called_once()


@patch("app.api.routers.chokepoints.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.chokepoints.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.chokepoints.db.fetch_one", new_callable=MagicMock)
@patch("app.api.routers.chokepoints.db.fetch_all", new_callable=MagicMock)
def test_get_chokepoint_series(fetch_all: MagicMock, fetch_one: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "chokepoint_id": "pc",
            "vessel_class": "tanker",
            "ts": "2024-01-01T00:00:00",
            "delay_hours": 5.0,
        }
    ]
    fetch_one.return_value = {"count": 1}
    resp = client.get(
        "/v1/logistics/chokepoints/series",
        params={"chokepoint_id": "pc", "vessel_class": "tanker"},
    )
    assert resp.status_code == 200
    assert resp.json()["count"] == 1
    fetch_all.assert_called_once()
    fetch_one.assert_called_once()


@patch("app.api.routers.chokepoints.cache.cache_get", new_callable=AsyncMock)
@patch("app.api.routers.chokepoints.cache.cache_set", new_callable=AsyncMock)
@patch("app.api.routers.chokepoints.db.fetch_all", new_callable=MagicMock)
def test_get_chokepoint_snapshot(fetch_all: MagicMock, cache_set: AsyncMock, cache_get: AsyncMock) -> None:
    cache_get.return_value = None
    fetch_all.return_value = [
        {
            "chokepoint_id": "pc",
            "vessel_class": "tanker",
            "ts": "2024-01-01T00:00:00",
            "delay_hours": 5.0,
        }
    ]
    resp = client.get(
        "/v1/logistics/chokepoints/snapshot",
        params={"chokepoint_id": "pc", "vessel_class": "tanker"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"][0]["chokepoint_id"] == "pc"
    fetch_all.assert_called_once()
