from __future__ import annotations

from typing import Any, Iterable, Iterator

from ingestion.transforms import macro

from .base import BaseAdapter


class WorldBankAdapter(BaseAdapter):
    """Adapter for World Bank macroeconomic indicators."""

    name = "worldbank"

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)

    def fetch(self, cursor: Any | None = None) -> Iterator[dict[str, Any]]:
        yield from self.records

    def transform(self, item: dict[str, Any]):
        return macro.transform([item])
