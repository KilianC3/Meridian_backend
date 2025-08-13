from __future__ import annotations

from datetime import datetime


def backfill(dataset: str, start: datetime, end: datetime) -> None:
    """Run a windowed backfill for ``dataset``."""
    raise NotImplementedError
