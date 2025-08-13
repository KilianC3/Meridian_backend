from __future__ import annotations

import hashlib
from typing import Any, Iterable, Iterator


def _classify_statement(title: str, url: str) -> str:
    t = f"{title} {url}".lower()
    if "minutes" in t:
        return "minutes"
    if "speech" in t:
        return "speech"
    if "statement" in t:
        return "statement"
    return "decision"


def _cb_name(source: str) -> str:
    return {"fed": "Fed", "ecb": "ECB", "boe": "BoE"}.get(source, source)


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Map policy-related records to ``cb_statements`` or ``policy_events``."""

    for rec in records:
        source = str(rec.get("source", ""))
        if source in {"fed", "ecb", "boe"}:
            url = rec.get("url", "")
            title = rec.get("title", "")
            yield {
                "statement_id": hashlib.md5(url.encode()).hexdigest(),
                "central_bank": _cb_name(source),
                "published_at": rec.get("published_at"),
                "type": _classify_statement(title, url),
                "title": title,
                "url": url,
                "text_excerpt": rec.get("summary"),
                "hawkish_dovish_score": None,
                "next_meeting_date": None,
                "raw": rec,
            }
            continue

        # policy events
        jurisdiction = {"federal_register": "US", "eurlex": "EU", "uk": "UK"}.get(
            source
        )
        if jurisdiction:
            src_id = str(rec.get("id"))
            yield {
                "event_id": f"{source}:{src_id}",
                "jurisdiction": jurisdiction,
                "source": source,
                "source_id": src_id,
                "published_at": rec.get("published_at"),
                "title": rec.get("title"),
                "summary": rec.get("summary"),
                "url": rec.get("url"),
                "topics": None,
                "affected_countries": None,
                "affected_sectors": None,
                "affected_entities": None,
                "severity": None,
                "raw": rec,
            }
