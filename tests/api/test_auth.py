from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_auth_flow() -> None:
    resp = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "password"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_resp = client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "admin@example.com"
    assert "admin" in me_data["roles"]

    ref_resp = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert ref_resp.status_code == 200
    assert "access_token" in ref_resp.json()


def test_invalid_login() -> None:
    resp = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "bad"},
    )
    assert resp.status_code == 401
