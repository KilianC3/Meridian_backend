from __future__ import annotations

import time
from typing import Any, Callable, Dict

import redis  # type: ignore[import-untyped]
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import Counter, Histogram

from app.core.config import settings

INGEST_SUCCESS = Counter(
    "ingestion_success_total", "Successful ingestion runs", ["dataset_id"]
)
INGEST_FAILURE = Counter(
    "ingestion_failure_total", "Failed ingestion runs", ["dataset_id"]
)
INGEST_LATENCY = Histogram(
    "ingestion_latency_seconds", "Ingestion job duration", ["dataset_id"]
)
INGEST_DELAY = Histogram(
    "ingestion_delay_seconds", "Delay since last successful ingestion", ["dataset_id"]
)


def _cadence_seconds(cadence: str) -> int:
    return {
        "15m": 900,
        "hourly": 3600,
        "daily": 86400,
        "monthly": 30 * 86400,
    }.get(cadence, 3600)


def schedule_jobs(
    registry: Dict[str, Any],
    adapter_factory: Callable[[str, Dict[str, Any]], Any],
    upsert_fn: Callable[[Any, str, Any, list[str]], int],
    get_conn: Callable[[], Any],
    release_conn: Callable[[Any], None],
) -> BackgroundScheduler:
    """Register cron-like jobs from the dataset registry."""

    scheduler = BackgroundScheduler(timezone="UTC")
    cache = redis.Redis.from_url(settings.redis_dsn, decode_responses=True)

    for dataset_id, cfg in registry.get("datasets", {}).items():
        if not cfg.get("enabled"):
            continue

        interval = _cadence_seconds(cfg["cadence"])

        def job(dataset_id=dataset_id, cfg=cfg, interval=interval):
            start = time.perf_counter()
            last_ts = cache.get(f"ingest:{dataset_id}:ts")
            if last_ts:
                delay = time.time() - float(last_ts)
                INGEST_DELAY.labels(dataset_id).observe(delay)
            conn = get_conn()
            try:
                adapter = adapter_factory(dataset_id, cfg)
                adapter.run(
                    conn,
                    upsert_fn,
                    cfg["target_table"],
                    cfg["conflict_keys"],
                )
                if cfg["target_table"] == "news_mentions":
                    from ingestion.metrics.news import update_density

                    update_density(conn)
                INGEST_SUCCESS.labels(dataset_id).inc()
                latency = time.perf_counter() - start
                INGEST_LATENCY.labels(dataset_id).observe(latency)
                cache.setex(f"ingest:{dataset_id}:ts", interval, str(int(time.time())))
            except Exception:
                INGEST_FAILURE.labels(dataset_id).inc()
                raise
            finally:
                release_conn(conn)

        scheduler.add_job(
            job,
            "interval",
            seconds=interval,
            id=dataset_id,
            replace_existing=True,
        )

    scheduler.start()
    return scheduler
