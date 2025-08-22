from __future__ import annotations

import time

from app.core.db import close_pool, get_conn, init_pool, release_conn
from ingestion.adapters import adapter_factory
from ingestion.loaders.postgres import bulk_upsert
from ingestion.registry import load_registry
from ingestion.scheduler.jobs import schedule_jobs


def main() -> None:
    init_pool()
    registry = load_registry()
    schedule_jobs(registry, adapter_factory, bulk_upsert, get_conn, release_conn)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        pass
    finally:
        close_pool()


if __name__ == "__main__":  # pragma: no cover
    main()
