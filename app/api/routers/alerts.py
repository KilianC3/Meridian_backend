from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.alerts import AlertDeliveryCreate, AlertRuleCreate
from app.core import db
from app.core.security import get_current_user
from app.services import auth_service

router = APIRouter(tags=["alerts"])


@router.get("/alerts/rules")
async def list_rules(user: auth_service.User = Depends(get_current_user)):
    sql = (
        "SELECT id, name, rule_json, enabled, cooldown_s, created_at FROM alert_rules "
        "WHERE user_id = (SELECT id FROM users WHERE email = %(email)s)"
    )
    rows = await run_in_threadpool(db.fetch_all, sql, {"email": user.email})
    return {"data": rows}


@router.post("/alerts/rules", status_code=status.HTTP_201_CREATED)
async def create_rule(
    req: AlertRuleCreate, user: auth_service.User = Depends(get_current_user)
):
    sql = (
        "INSERT INTO alert_rules "
        "(id, user_id, name, rule_json, enabled, cooldown_s, created_at) "
        "VALUES ("
        "%(id)s, (SELECT id FROM users WHERE email=%(email)s), "
        "%(name)s, %(rule_json)s, TRUE, %(cooldown)s, NOW()"
        ") RETURNING id, name, rule_json, enabled, cooldown_s, created_at"
    )
    rid = uuid.uuid4()
    params = {
        "id": rid,
        "email": user.email,
        "name": req.name,
        "rule_json": req.rule_json,
        "cooldown": req.cooldown_s,
    }
    row = await run_in_threadpool(db.fetch_one, sql, params)
    return row


@router.post("/alerts/rules/{rule_id}/enable")
async def enable_rule(
    rule_id: uuid.UUID, user: auth_service.User = Depends(get_current_user)
):
    sql = (
        "UPDATE alert_rules SET enabled = TRUE WHERE id = %(id)s "
        "AND user_id = (SELECT id FROM users WHERE email=%(email)s) "
        "RETURNING id, name, rule_json, enabled, cooldown_s, created_at"
    )
    row = await run_in_threadpool(
        db.fetch_one, sql, {"id": str(rule_id), "email": user.email}
    )
    return row


@router.post("/alerts/rules/{rule_id}/disable")
async def disable_rule(
    rule_id: uuid.UUID, user: auth_service.User = Depends(get_current_user)
):
    sql = (
        "UPDATE alert_rules SET enabled = FALSE WHERE id = %(id)s "
        "AND user_id = (SELECT id FROM users WHERE email=%(email)s) "
        "RETURNING id, name, rule_json, enabled, cooldown_s, created_at"
    )
    row = await run_in_threadpool(
        db.fetch_one, sql, {"id": str(rule_id), "email": user.email}
    )
    return row


@router.get("/alerts/deliveries")
async def list_deliveries(
    rule_id: uuid.UUID | None = None,
    user: auth_service.User = Depends(get_current_user),
):
    sql = (
        "SELECT d.id, d.rule_id, d.kind, d.target, d.secret, d.active "
        "FROM alert_deliveries d JOIN alert_rules r ON d.rule_id = r.id "
        "WHERE r.user_id = (SELECT id FROM users WHERE email=%(email)s)"
    )
    params: dict[str, object] = {"email": user.email}
    if rule_id is not None:
        sql += " AND d.rule_id = %(rule_id)s"
        params["rule_id"] = str(rule_id)
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    return {"data": rows}


@router.post("/alerts/deliveries", status_code=status.HTTP_201_CREATED)
async def create_delivery(
    req: AlertDeliveryCreate, user: auth_service.User = Depends(get_current_user)
):
    sql = (
        "INSERT INTO alert_deliveries (id, rule_id, kind, target, secret, active) "
        "SELECT %(id)s, r.id, %(kind)s, %(target)s, %(secret)s, TRUE "
        "FROM alert_rules r JOIN users u ON r.user_id = u.id "
        "WHERE r.id = %(rule_id)s AND u.email = %(email)s "
        "RETURNING id, rule_id, kind, target, secret, active"
    )
    did = uuid.uuid4()
    params = {
        "id": did,
        "rule_id": str(req.rule_id),
        "kind": req.kind.value,
        "target": req.target,
        "secret": req.secret,
        "email": user.email,
    }
    row = await run_in_threadpool(db.fetch_one, sql, params)
    return row


@router.get("/alerts/events")
async def list_events(
    rule_id: uuid.UUID | None = None,
    from_ts: datetime | None = None,
    user: auth_service.User = Depends(get_current_user),
):
    sql = (
        "SELECT e.id, e.rule_id, e.fired_at, e.payload_json, "
        "e.dedupe_key, e.delivered, e.attempts, e.last_error "
        "FROM alert_events e JOIN alert_rules r ON e.rule_id = r.id "
        "WHERE r.user_id = (SELECT id FROM users WHERE email=%(email)s)"
    )
    params: dict[str, object] = {"email": user.email}
    if rule_id is not None:
        sql += " AND e.rule_id = %(rule_id)s"
        params["rule_id"] = str(rule_id)
    if from_ts is not None:
        sql += " AND e.fired_at >= %(from_ts)s"
        params["from_ts"] = from_ts
    rows = await run_in_threadpool(db.fetch_all, sql, params)
    return {"data": rows}
