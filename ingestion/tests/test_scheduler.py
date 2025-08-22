from __future__ import annotations

from ingestion.scheduler import jobs


def test_schedule_jobs_runs_and_caches(monkeypatch):
    registry = {
        "datasets": {
            "dummy": {
                "cadence": "daily",
                "adapter": "dummy",
                "target_table": "metrics_ts",
                "conflict_keys": ["series_id", "ts"],
                "enabled": True,
            }
        }
    }

    class DummyAdapter:
        def run(self, conn, upsert_fn, table, keys, cursor=None):
            rows = [{"series_id": "x", "ts": 1, "value": 1.0}]
            upsert_fn(conn, table, rows, keys)

    def fake_factory(dataset_id, cfg):
        return DummyAdapter()

    calls = {}

    def fake_bulk(conn, table, rows, keys):
        calls["table"] = table
        calls["rows"] = rows
        calls["keys"] = keys
        return 0

    class FakeConn:
        pass

    def fake_get_conn():
        return FakeConn()

    def fake_release_conn(conn):
        return None

    class FakeRedis:
        def __init__(self):
            self.store: dict[str, str] = {}

        def setex(self, key: str, ttl: int, value: str) -> None:  # noqa: ARG002
            self.store[key] = value

        def get(self, key: str) -> str | None:
            return self.store.get(key)

    fr = FakeRedis()
    monkeypatch.setattr(jobs.redis.Redis, "from_url", lambda *a, **k: fr)

    scheduler = jobs.schedule_jobs(
        registry, fake_factory, fake_bulk, fake_get_conn, fake_release_conn
    )
    job = scheduler.get_job("dummy")
    assert job is not None
    job.func()
    assert "ingest:dummy:ts" in fr.store
    assert calls["rows"] == [{"series_id": "x", "ts": 1, "value": 1.0}]
    assert calls["keys"] == ["series_id", "ts"]
    metric = jobs.INGEST_SUCCESS.labels("dummy")
    assert metric._value.get() == 1.0
    scheduler.shutdown()


def test_schedule_jobs_respects_cadence(monkeypatch):
    registry = {
        "datasets": {
            "dummy": {
                "cadence": "hourly",
                "adapter": "dummy",
                "target_table": "metrics_ts",
                "conflict_keys": ["series_id", "ts"],
                "enabled": True,
            }
        }
    }

    class DummyAdapter:
        def run(self, conn, upsert_fn, table, keys, cursor=None):
            pass

    def fake_factory(dataset_id, cfg):
        return DummyAdapter()

    def fake_bulk(conn, table, rows, keys):
        return 0

    monkeypatch.setattr(jobs.redis.Redis, "from_url", lambda *a, **k: None)

    scheduler = jobs.schedule_jobs(
        registry, fake_factory, fake_bulk, lambda: None, lambda conn: None
    )
    job = scheduler.get_job("dummy")
    assert job is not None
    # Interval trigger should match hourly cadence (3600 seconds)
    assert int(job.trigger.interval.total_seconds()) == 3600
    scheduler.shutdown()
