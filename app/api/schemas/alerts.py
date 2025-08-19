from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AlertRuleCreate(BaseModel):
    name: str
    rule_json: dict[str, Any]
    cooldown_s: int = 0


class AlertRule(AlertRuleCreate):
    id: uuid.UUID
    enabled: bool = True
    created_at: datetime


class AlertDeliveryKind(str, Enum):
    email = "email"
    webhook = "webhook"


class AlertDeliveryCreate(BaseModel):
    rule_id: uuid.UUID
    kind: AlertDeliveryKind
    target: str
    secret: str | None = None


class AlertDelivery(AlertDeliveryCreate):
    id: uuid.UUID
    active: bool = True


class AlertEvent(BaseModel):
    id: uuid.UUID
    rule_id: uuid.UUID
    fired_at: datetime
    payload_json: dict[str, Any]
    dedupe_key: str
    delivered: bool
    attempts: int
    last_error: str | None = None


class AlertEventsResponse(BaseModel):
    data: list[AlertEvent] = Field(default_factory=list)


class AlertRulesResponse(BaseModel):
    data: list[AlertRule] = Field(default_factory=list)


class AlertDeliveriesResponse(BaseModel):
    data: list[AlertDelivery] = Field(default_factory=list)
