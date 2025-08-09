from __future__ import annotations

from typing import Callable, Dict

JOB_REGISTRY: Dict[str, Callable[[], None]] = {}


def register_job(name: str, func: Callable[[], None]) -> None:
    JOB_REGISTRY[name] = func


def list_jobs() -> Dict[str, Callable[[], None]]:
    return JOB_REGISTRY
