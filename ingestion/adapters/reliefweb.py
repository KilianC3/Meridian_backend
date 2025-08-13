"""Adapter for ReliefWeb API producing geo events."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from ingestion.transforms import geopolitics

from .base import BaseAdapter


class ReliefWebAdapter(BaseAdapter):
    name = "reliefweb"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        return geopolitics.transform([item])

