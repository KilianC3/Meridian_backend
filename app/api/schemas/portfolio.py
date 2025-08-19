from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class PortfolioCreate(BaseModel):
    name: str


class Portfolio(PortfolioCreate):
    id: uuid.UUID
    created_at: datetime


class Holding(BaseModel):
    symbol: str
    weight: float | None = None
    shares: float | None = None
    as_of: date


class HoldingsUpsertRequest(BaseModel):
    holdings: list[Holding] = Field(default_factory=list)
