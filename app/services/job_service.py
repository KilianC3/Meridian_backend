from __future__ import annotations

from typing import Awaitable, Callable, Dict, List

from app.scheduler.jobs import datasource_check, heartbeat

JobFunc = Callable[[], Awaitable[None]]

REGISTRY: Dict[str, JobFunc] = {
    "heartbeat": heartbeat.run,
    "datasource_check": datasource_check.run,
}


def get(name: str) -> JobFunc:
    return REGISTRY[name]


def list_jobs() -> List[str]:
    return list(REGISTRY.keys())
