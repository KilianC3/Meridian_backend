from __future__ import annotations

from datetime import datetime

from ingestion.adapters import adapter_factory
from ingestion.registry import load_registry
from ingestion.scheduler import backfill as backfill_mod


def test_adapter_factory_instantiates_and_wraps_transform():
    registry = load_registry()
    cfg = registry["datasets"]["rates.fred.us10y"]
    adapter = adapter_factory("rates.fred.us10y", cfg)

    # The adapter should be of the class defined in the registry
    from ingestion.adapters.fred import FREDAdapter

    assert isinstance(adapter, FREDAdapter)

    # Transform wrapper should accept a single item and yield rows
    rows = list(
        adapter.transform(
            {
                "series": "DGS10",
                "date": "2024-01-01",
                "value": 4.5,
                "unit": "%",
            }
        )
    )
    assert rows and rows[0]["series_id"] == "us_10y_yield"


def test_backfill_invokes_adapter(monkeypatch):
    calls: dict[str, object] = {}

    class DummyAdapter:
        def __init__(self):
            self.cursor_seen = None

        def run(self, conn, upsert_fn, table, keys, cursor=None):
            self.cursor_seen = cursor
            calls["table"] = table
            calls["keys"] = keys
            upsert_fn(conn, table, [], keys)

    def fake_factory(dataset_id, cfg):
        return DummyAdapter()

    def fake_bulk(conn, table, rows, keys):
        calls["bulk"] = True
        return 0

    monkeypatch.setattr(backfill_mod, "adapter_factory", fake_factory)
    monkeypatch.setattr(backfill_mod, "bulk_upsert", fake_bulk)
    monkeypatch.setattr(backfill_mod, "get_conn", lambda: object())
    monkeypatch.setattr(backfill_mod, "release_conn", lambda conn: None)
    monkeypatch.setattr(
        backfill_mod,
        "load_registry",
        lambda: {
            "datasets": {
                "dummy": {
                    "name": "Dummy",
                    "cadence": "daily",
                    "adapter": "dummy",
                    "target_table": "metrics_ts",
                    "conflict_keys": ["series_id", "ts"],
                    "enabled": True,
                }
            }
        },
    )

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    backfill_mod.backfill("dummy", start, end)

    assert calls["table"] == "metrics_ts"
    assert calls["keys"] == ["series_id", "ts"]
    assert calls.get("bulk")
