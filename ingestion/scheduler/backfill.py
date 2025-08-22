from __future__ import annotations

from datetime import datetime

from app.core.db import get_conn, release_conn
from ingestion.adapters import adapter_factory
from ingestion.loaders.postgres import bulk_upsert
from ingestion.registry import load_registry


def backfill(dataset: str, start: datetime, end: datetime) -> None:
    """Run a windowed backfill for ``dataset``.

    Parameters
    ----------
    dataset:
        Dataset identifier present in ``datasets.yaml``.
    start, end:
        Inclusive time window to backfill.  The ``start`` value is passed as the
        cursor argument to the adapter and both ``start`` and ``end`` are set as
        attributes on the adapter instance for those that need the bounds.
    """

    registry = load_registry()
    cfg = registry.get("datasets", {}).get(dataset)
    if cfg is None:  # pragma: no cover - defensive
        raise KeyError(f"Unknown dataset: {dataset}")

    conn = get_conn()
    try:
        adapter = adapter_factory(dataset, cfg)
        setattr(adapter, "start", start)
        setattr(adapter, "end", end)
        adapter.run(
            conn,
            bulk_upsert,
            cfg["target_table"],
            cfg["conflict_keys"],
            cursor=start,
        )
    finally:
        release_conn(conn)
