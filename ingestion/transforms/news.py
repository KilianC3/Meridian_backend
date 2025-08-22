from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Iterable, Iterator


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Map RSS items into ``news_mentions`` rows."""
    for rec in records:
        url = rec.get("link") or rec.get("url")
        mid = hashlib.md5((url or "").encode()).hexdigest()
        published = rec.get("published_at")
        if isinstance(published, datetime):
            published_at: str | None = published.isoformat()
        elif isinstance(published, str):
            published_at = published
        else:
            published_at = None
        yield {
            "mention_id": mid,
            "factor_id": rec.get("factor_id"),
            "source": rec.get("source", "rss"),
            "source_id": mid,
            "url": url,
            "title": rec.get("title"),
            "published_at": published_at,
            "snippet": rec.get("summary"),
            "raw": rec,
        }
