"""Adapter for UN Comtrade trade flow data."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from ingestion.transforms import logistics

from .base import BaseAdapter


class ComtradeAdapter(BaseAdapter):
    name = "un_comtrade"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        return logistics.transform([item])
