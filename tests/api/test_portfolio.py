from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers() -> dict[str, str]:
    resp = client.post(
        "/auth/login", data={"username": "admin@example.com", "password": "password"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@patch("app.api.routers.portfolio.db.fetch_all", new_callable=MagicMock)
def test_list_portfolios(fetch_all: MagicMock) -> None:
    fetch_all.return_value = [
        {"id": "p1", "name": "Test", "created_at": "2024-01-01T00:00:00"}
    ]
    resp = client.get("/v1/portfolio", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["data"][0]["name"] == "Test"
    fetch_all.assert_called_once()


@patch("app.api.routers.portfolio.db.fetch_one", new_callable=MagicMock)
def test_create_portfolio(fetch_one: MagicMock) -> None:
    fetch_one.return_value = {
        "id": "p1",
        "name": "P1",
        "created_at": "2024-01-01T00:00:00",
    }
    resp = client.post("/v1/portfolio", json={"name": "P1"}, headers=auth_headers())
    assert resp.status_code == 201
    assert resp.json()["name"] == "P1"
    fetch_one.assert_called_once()


@patch("app.api.routers.portfolio.db.fetch_one", new_callable=MagicMock)
def test_upsert_holdings(fetch_one: MagicMock) -> None:
    fetch_one.side_effect = [
        None,
        {
            "portfolio_id": "11111111-1111-1111-1111-111111111111",
            "symbol": "AAPL",
            "weight": 0.5,
            "shares": None,
            "as_of": "2024-01-01",
        },
    ]
    resp = client.put(
        "/v1/portfolio/11111111-1111-1111-1111-111111111111/holdings",
        json={
            "holdings": [
                {
                    "symbol": "AAPL",
                    "weight": 0.5,
                    "shares": None,
                    "as_of": "2024-01-01",
                }
            ]
        },
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    assert fetch_one.call_count == 2
