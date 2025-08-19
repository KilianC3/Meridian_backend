from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.portfolio import HoldingsUpsertRequest, PortfolioCreate
from app.core import db
from app.core.security import get_current_user
from app.services import auth_service

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio")
async def list_portfolios(
    user: auth_service.User = Depends(get_current_user),
):
    sql = (
        "SELECT id, name, created_at FROM portfolios "
        "WHERE user_id = (SELECT id FROM users WHERE email = %(email)s)"
    )
    rows = await run_in_threadpool(db.fetch_all, sql, {"email": user.email})
    return {"data": rows}


@router.post("/portfolio", status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    req: PortfolioCreate, user: auth_service.User = Depends(get_current_user)
):
    sql = (
        "INSERT INTO portfolios (id, user_id, name, created_at) "
        "VALUES (%(id)s, (SELECT id FROM users WHERE email=%(email)s), "
        "%(name)s, NOW()) "
        "RETURNING id, name, created_at"
    )
    pid = uuid.uuid4()
    row = await run_in_threadpool(
        db.fetch_one,
        sql,
        {"id": pid, "email": user.email, "name": req.name},
    )
    return row


@router.delete(
    "/portfolio/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_portfolio(
    portfolio_id: uuid.UUID, user: auth_service.User = Depends(get_current_user)
) -> Response:
    sql = (
        "DELETE FROM portfolios WHERE id = %(id)s "
        "AND user_id = (SELECT id FROM users WHERE email=%(email)s)"
    )
    await run_in_threadpool(
        db.fetch_one, sql, {"id": str(portfolio_id), "email": user.email}
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/portfolio/{portfolio_id}/holdings")
async def upsert_holdings(
    portfolio_id: uuid.UUID,
    req: HoldingsUpsertRequest,
    user: auth_service.User = Depends(get_current_user),
):
    del_sql = "DELETE FROM portfolio_holdings WHERE portfolio_id=%(pid)s"
    await run_in_threadpool(db.fetch_one, del_sql, {"pid": str(portfolio_id)})
    insert_sql = (
        "INSERT INTO portfolio_holdings (portfolio_id, symbol, weight, shares, as_of) "
        "VALUES (%(pid)s, %(symbol)s, %(weight)s, %(shares)s, %(as_of)s) "
        "RETURNING portfolio_id, symbol, weight, shares, as_of"
    )
    rows = []
    for h in req.holdings:
        params = {
            "pid": str(portfolio_id),
            "symbol": h.symbol,
            "weight": h.weight,
            "shares": h.shares,
            "as_of": h.as_of,
        }
        row = await run_in_threadpool(db.fetch_one, insert_sql, params)
        rows.append(row)
    return {"data": rows}
