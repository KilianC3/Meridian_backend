from __future__ import annotations

from typing import Any, Iterable, Iterator

from ingestion.transforms import markets

from .base import BaseAdapter


class FREDAdapter(BaseAdapter):
    """Adapter for FRED rates and FX series."""

    name = "fred"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        return markets.transform([item])
