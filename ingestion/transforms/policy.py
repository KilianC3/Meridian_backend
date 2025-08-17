from __future__ import annotations

import hashlib
from typing import Any, Iterable, Iterator


def _classify_statement(title: str, url: str) -> str:
    """Best-effort classification of central bank communications."""
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


def map_cb_statement(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Transform central-bank RSS records into ``cb_statements`` rows."""

    for rec in records:
        url = rec.get("url", "")
        title = rec.get("title", "")
        source = str(rec.get("source", ""))
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


def map_policy_event(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Generic mapper for regulatory or policy announcements."""

    for rec in records:
        source = str(rec.get("source", ""))
        jurisdiction = {"federal_register": "US", "eurlex": "EU", "uk": "UK"}.get(
            source
        )
        src_id = str(rec.get("id", "")) or hashlib.md5(str(rec).encode()).hexdigest()
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


def map_sanction_update(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Map sanction-list rows into ``policy_events`` entries."""

    for rec in records:
        name = str(rec.get("name", rec.get("entity", "unknown")))
        src = str(rec.get("source", "sanctions"))
        src_id = str(rec.get("id", hashlib.md5(name.encode()).hexdigest()))
        yield {
            "event_id": f"{src}:{src_id}",
            "jurisdiction": rec.get("jurisdiction"),
            "source": src,
            "source_id": src_id,
            "published_at": rec.get("published_at"),
            "title": name,
            "summary": rec.get("program") or rec.get("remarks"),
            "url": rec.get("url"),
            "topics": None,
            "affected_countries": rec.get("country"),
            "affected_sectors": None,
            "affected_entities": name,
            "severity": None,
            "raw": rec,
        }


def map_bis_entity(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Specialised mapper for BIS Entity List updates."""

    for rec in records:
        name = str(rec.get("name", ""))
        src_id = str(rec.get("id", hashlib.md5(name.encode()).hexdigest()))
        yield {
            "event_id": f"bis:{src_id}",
            "jurisdiction": "US",
            "source": "bis",
            "source_id": src_id,
            "published_at": rec.get("published_at"),
            "title": name,
            "summary": rec.get("summary"),
            "url": rec.get("url"),
            "topics": None,
            "affected_countries": rec.get("country"),
            "affected_sectors": None,
            "affected_entities": name,
            "severity": None,
            "raw": rec,
        }


# Backwards compatibility for older registry entries
def transform(
    records: Iterable[dict[str, Any]],
) -> Iterator[dict[str, Any]]:  # pragma: no cover
    """Legacy wrapper that auto-detects record type."""
    for rec in records:
        src = str(rec.get("source", ""))
        if src in {"fed", "ecb", "boe"}:
            yield from map_cb_statement([rec])
        else:
            yield from map_policy_event([rec])
