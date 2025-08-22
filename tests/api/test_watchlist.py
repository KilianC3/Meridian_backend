from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_watchlist_disabled() -> None:
    resp = client.get("/v1/watchlist")
    assert resp.status_code == 404
