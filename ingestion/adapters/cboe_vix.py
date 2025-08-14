"""Adapter for CBOE VIX CSV data."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from .base import BaseAdapter


class CBOEVixAdapter(BaseAdapter):
    name = "cboe_vix"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        return [item]
