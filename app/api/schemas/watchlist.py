from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WatchlistType(str, Enum):
    country = "country"
    port = "port"
    chokepoint = "chokepoint"
    hs = "hs"
    company = "company"


class WatchlistCreate(BaseModel):
    name: str
    type: WatchlistType


class Watchlist(WatchlistCreate):
    id: uuid.UUID


class WatchlistItem(BaseModel):
    ref_id: str
    label: str | None = None
    meta: dict[str, Any] | None = None


class WatchlistItemsUpsert(BaseModel):
    items: list[WatchlistItem] = Field(default_factory=list)
