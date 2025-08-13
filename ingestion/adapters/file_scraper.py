from __future__ import annotations

import csv
import hashlib
import io
from typing import Any, Iterator

import requests  # type: ignore[import-untyped]

from .base import BaseAdapter


class FileScraperAdapter(BaseAdapter):
    """Download HTML or CSV content and avoid duplicates via checksum."""

    def __init__(self) -> None:
        self._last_checksum: str | None = None

    def fetch(self, cursor: Any | None = None) -> Iterator[Any]:
        url = str(cursor)
        resp = requests.get(url)
        resp.raise_for_status()
        content = resp.content
        checksum = hashlib.sha256(content).hexdigest()
        if checksum == self._last_checksum:
            return iter(())
        self._last_checksum = checksum
        if url.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            return iter(reader)
        return iter([content.decode("utf-8")])

    def transform(self, item: Any) -> Iterator[dict[str, Any]]:
        return iter([item]) if isinstance(item, dict) else iter(())
