from __future__ import annotations

from typing import Any, Callable, Dict

from apscheduler.schedulers.background import BackgroundScheduler


def schedule_jobs(
    registry: Dict[str, Any],
    adapter_factory: Callable[[str, Dict[str, Any]], Any],
    upsert_fn: Callable[[Any, str, Any, list[str]], int],
) -> BackgroundScheduler:
    """Register cron-like jobs from the dataset registry."""

    scheduler = BackgroundScheduler(timezone="UTC")
    cadence_map = {"15m": 900, "hourly": 3600, "daily": 86400, "monthly": 30 * 86400}

    for dataset_id, cfg in registry.get("datasets", {}).items():
        if not cfg.get("enabled"):
            continue
        interval = cadence_map.get(cfg["cadence"], 3600)
        adapter = adapter_factory(dataset_id, cfg)
        scheduler.add_job(
            adapter.run,
            "interval",
            seconds=interval,
            kwargs={
                "upsert_fn": upsert_fn,
                "target_table": cfg["target_table"],
                "conflict_keys": cfg["conflict_keys"],
            },
            id=dataset_id,
            replace_existing=True,
        )

    scheduler.start()
    return scheduler
