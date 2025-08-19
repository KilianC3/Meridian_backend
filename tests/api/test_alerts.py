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


@patch("app.api.routers.alerts.db.fetch_all", new_callable=MagicMock)
def test_list_rules(fetch_all: MagicMock) -> None:
    fetch_all.return_value = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "R1",
            "rule_json": {},
            "enabled": True,
            "cooldown_s": 0,
            "created_at": "2024-01-01T00:00:00",
        }
    ]
    resp = client.get("/v1/alerts/rules", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["data"][0]["name"] == "R1"
    fetch_all.assert_called_once()


@patch("app.api.routers.alerts.db.fetch_one", new_callable=MagicMock)
def test_create_rule(fetch_one: MagicMock) -> None:
    fetch_one.return_value = {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "R1",
        "rule_json": {},
        "enabled": True,
        "cooldown_s": 0,
        "created_at": "2024-01-01T00:00:00",
    }
    resp = client.post(
        "/v1/alerts/rules",
        json={"name": "R1", "rule_json": {}, "cooldown_s": 0},
        headers=auth_headers(),
    )
    assert resp.status_code == 201
    assert resp.json()["id"] == "11111111-1111-1111-1111-111111111111"
    fetch_one.assert_called_once()


@patch("app.api.routers.alerts.db.fetch_one", new_callable=MagicMock)
def test_enable_rule(fetch_one: MagicMock) -> None:
    fetch_one.return_value = {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "R1",
        "rule_json": {},
        "enabled": True,
        "cooldown_s": 0,
        "created_at": "2024-01-01T00:00:00",
    }
    resp = client.post(
        "/v1/alerts/rules/11111111-1111-1111-1111-111111111111/enable",
        headers=auth_headers(),
    )
    assert resp.status_code == 200
    fetch_one.assert_called_once()


@patch("app.api.routers.alerts.db.fetch_one", new_callable=MagicMock)
def test_create_delivery(fetch_one: MagicMock) -> None:
    fetch_one.return_value = {
        "id": "22222222-2222-2222-2222-222222222222",
        "rule_id": "11111111-1111-1111-1111-111111111111",
        "kind": "email",
        "target": "user@example.com",
        "secret": None,
        "active": True,
    }
    resp = client.post(
        "/v1/alerts/deliveries",
        json={
            "rule_id": "11111111-1111-1111-1111-111111111111",
            "kind": "email",
            "target": "user@example.com",
            "secret": None,
        },
        headers=auth_headers(),
    )
    assert resp.status_code == 201
    fetch_one.assert_called_once()


@patch("app.api.routers.alerts.db.fetch_all", new_callable=MagicMock)
def test_list_events(fetch_all: MagicMock) -> None:
    fetch_all.return_value = [
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "rule_id": "11111111-1111-1111-1111-111111111111",
            "fired_at": "2024-01-01T00:00:00",
            "payload_json": {},
            "dedupe_key": "k",
            "delivered": False,
            "attempts": 0,
            "last_error": None,
        }
    ]
    resp = client.get("/v1/alerts/events", headers=auth_headers())
    assert resp.status_code == 200
    assert resp.json()["data"][0]["id"] == "33333333-3333-3333-3333-333333333333"
    fetch_all.assert_called_once()
