from __future__ import annotations

import hashlib
import math
from datetime import datetime
from typing import Any, Iterable, Iterator


def _parse_ts(val: str) -> str:
    if len(val) == 8:  # YYYYMMDD
        return datetime.strptime(val, "%Y%m%d").date().isoformat()
    return val


def transform(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """Map geopolitical feeds into ``geo_events`` or ``geo_mentions`` rows."""

    for rec in records:
        source = rec.get("source")

        if source == "gdelt_events":
            mentions = rec.get("NumMentions", 0)
            sources = rec.get("NumSources", 0)
            articles = rec.get("NumArticles", 0)
            actor_roles = [
                code
                for code in [
                    rec.get("Actor1Type1Code"),
                    rec.get("Actor1Type2Code"),
                    rec.get("Actor2Type1Code"),
                    rec.get("Actor2Type2Code"),
                ]
                if code
            ]
            yield {
                "event_id": rec.get("GLOBALEVENTID"),
                "source": "gdelt_events",
                "source_id": rec.get("GLOBALEVENTID"),
                "ts": _parse_ts(str(rec.get("DATEADDED") or rec.get("SQLDATE"))),
                "event_type": rec.get("EventType"),
                "country": rec.get("ActionGeo_CountryCode"),
                "lat": rec.get("ActionGeo_Lat"),
                "lon": rec.get("ActionGeo_Long"),
                "actor1": rec.get("Actor1Name"),
                "actor2": rec.get("Actor2Name"),
                "actor_roles": actor_roles or None,
                "goldstein": rec.get("GoldsteinScale"),
                "people_impacted": None,
                "importance": math.log1p(mentions + sources + articles),
                "url": None,
                "raw": rec,
            }
            continue

        if source == "gdelt_mentions":
            gid = str(rec.get("GLOBALEVENTID"))
            mid = str(rec.get("MentionIdentifier"))
            mention_id = hashlib.md5(f"{gid}:{mid}".encode()).hexdigest()
            yield {
                "mention_id": mention_id,
                "source": "gdelt_mentions",
                "source_id": mention_id,
                "event_source_id": gid,
                "url": rec.get("MentionURL"),
                "published_at": _parse_ts(str(rec.get("MentionTimeDate"))),
                "language": rec.get("MentionDocLanguage"),
                "source_country": rec.get("MentionDocCountryCode"),
                "snippet": rec.get("MentionText"),
                "raw": rec,
            }
            continue

        if source == "reliefweb":
            people = rec.get("people_impacted")
            yield {
                "event_id": f"reliefweb:{rec.get('id')}",
                "source": "reliefweb",
                "source_id": str(rec.get("id")),
                "ts": rec.get("date"),
                "event_type": rec.get("type"),
                "country": rec.get("country"),
                "lat": rec.get("lat"),
                "lon": rec.get("lon"),
                "actor1": None,
                "actor2": None,
                "actor_roles": None,
                "goldstein": None,
                "people_impacted": people,
                "importance": math.log1p(people) if people else None,
                "url": rec.get("url"),
                "raw": rec,
            }
