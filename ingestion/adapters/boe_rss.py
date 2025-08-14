"""Adapter for Bank of England RSS feed."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from ingestion.transforms import policy

from .base import BaseAdapter


class BoERSSAdapter(BaseAdapter):
    name = "boe_rss"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        return policy.transform([item])
