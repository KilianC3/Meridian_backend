"""Adapter for Yahoo Finance price data."""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from .base import BaseAdapter


class YFinanceAdapter(BaseAdapter):
    name = "yfinance"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        # passthrough to prices or indices tables
        return [item]

