from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.scheduler import scheduler as scheduler_module

client = TestClient(app)


def setup_module() -> None:  # pragma: no cover
    scheduler_module.get_scheduler()


def teardown_module() -> None:  # pragma: no cover
    pass


def test_job_crud_and_run() -> None:
    resp = client.post("/jobs/heartbeat")
    assert resp.status_code == 200

    list_resp = client.get("/jobs")
    assert list_resp.status_code == 200
    jobs = [j["id"] for j in list_resp.json()]
    assert "heartbeat" in jobs

    run_resp = client.post("/jobs/heartbeat/run")
    assert run_resp.status_code == 200

    del_resp = client.delete("/jobs/heartbeat")
    assert del_resp.status_code == 200

    list_resp2 = client.get("/jobs")
    assert "heartbeat" not in [j["id"] for j in list_resp2.json()]
