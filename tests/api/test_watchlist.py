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


@patch("app.api.routers.watchlist.db.fetch_all", new_callable=MagicMock)
def test_list_watchlists(fetch_all: MagicMock) -> None:
    fetch_all.return_value = [{"id": "w1", "name": "WL", "type": "country"}]
    resp = client.get("/v1/watchlist", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["data"][0]["id"] == "w1"
    fetch_all.assert_called_once()


@patch("app.api.routers.watchlist.db.fetch_one", new_callable=MagicMock)
def test_create_watchlist(fetch_one: MagicMock) -> None:
    fetch_one.return_value = {
        "id": "w1",
        "name": "WL",
        "type": "country",
    }
    resp = client.post(
        "/v1/watchlist",
        json={"name": "WL", "type": "country"},
        headers=auth_headers(),
    )
    assert resp.status_code == 201
    assert resp.json()["id"] == "w1"
    fetch_one.assert_called_once()


@patch("app.api.routers.watchlist.db.fetch_one", new_callable=MagicMock)
def test_upsert_items(fetch_one: MagicMock) -> None:
    fetch_one.side_effect = [
        None,
        {
            "watchlist_id": "11111111-1111-1111-1111-111111111111",
            "ref_id": "US",
            "label": "United States",
            "meta": None,
        },
    ]
    resp = client.put(
        "/v1/watchlist/11111111-1111-1111-1111-111111111111/items",
        json={"items": [{"ref_id": "US", "label": "United States", "meta": None}]},
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    assert fetch_one.call_count == 2
