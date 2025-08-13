from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterator

import feedparser

from .base import BaseAdapter


class RSSAdapter(BaseAdapter):
    """Poll an RSS/Atom feed and yield new entries."""

    def __init__(self, url: str):
        self.url = url

    def fetch(self, cursor: datetime | None = None) -> Iterator[Any]:
        feed = feedparser.parse(self.url)
        for entry in feed.entries:
            published = entry.get("published_parsed")
            if published is not None:
                year, month, day, hour, minute, second = published[:6]
                ts = datetime(
                    year, month, day, hour, minute, int(second), tzinfo=timezone.utc
                )
                if cursor and ts <= cursor:
                    continue
            yield entry

    def transform(self, item: Any) -> Iterator[dict[str, Any]]:
        return iter([item])
