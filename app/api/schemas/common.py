from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TimeWindow(BaseModel):
    start: datetime | None = None
    end: datetime | None = None


class Page(BaseModel):
    limit: int = Field(100, ge=1, le=5000)
    offset: int = Field(0, ge=0)


class ErrorResp(BaseModel):
    code: int
    message: str
