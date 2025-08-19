from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.watchlist import WatchlistCreate, WatchlistItemsUpsert
from app.core import db
from app.core.security import get_current_user
from app.services import auth_service

router = APIRouter(tags=["watchlist"])


@router.get("/watchlist")
async def list_watchlists(
    user: auth_service.User = Depends(get_current_user),
):
    sql = (
        "SELECT id, name, type FROM watchlists "
        "WHERE user_id = (SELECT id FROM users WHERE email = %(email)s)"
    )
    rows = await run_in_threadpool(db.fetch_all, sql, {"email": user.email})
    return {"data": rows}


@router.post("/watchlist", status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    req: WatchlistCreate, user: auth_service.User = Depends(get_current_user)
):
    sql = (
        "INSERT INTO watchlists (id, user_id, name, type) "
        "VALUES (%(id)s, (SELECT id FROM users WHERE email=%(email)s), "
        "%(name)s, %(type)s) "
        "RETURNING id, name, type"
    )
    wid = uuid.uuid4()
    row = await run_in_threadpool(
        db.fetch_one,
        sql,
        {
            "id": wid,
            "email": user.email,
            "name": req.name,
            "type": req.type.value,
        },
    )
    return row


@router.delete(
    "/watchlist/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_watchlist(
    watchlist_id: uuid.UUID, user: auth_service.User = Depends(get_current_user)
) -> Response:
    sql = (
        "DELETE FROM watchlists WHERE id = %(id)s "
        "AND user_id = (SELECT id FROM users WHERE email=%(email)s)"
    )
    await run_in_threadpool(
        db.fetch_one, sql, {"id": str(watchlist_id), "email": user.email}
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/watchlist/{watchlist_id}/items")
async def upsert_items(
    watchlist_id: uuid.UUID,
    req: WatchlistItemsUpsert,
    user: auth_service.User = Depends(get_current_user),
):
    del_sql = "DELETE FROM watchlist_items WHERE watchlist_id=%(wid)s"
    await run_in_threadpool(db.fetch_one, del_sql, {"wid": str(watchlist_id)})
    insert_sql = (
        "INSERT INTO watchlist_items (watchlist_id, ref_id, label, meta) "
        "VALUES (%(wid)s, %(ref_id)s, %(label)s, %(meta)s) "
        "RETURNING watchlist_id, ref_id, label, meta"
    )
    rows = []
    for item in req.items:
        params = {
            "wid": str(watchlist_id),
            "ref_id": item.ref_id,
            "label": item.label,
            "meta": item.meta,
        }
        row = await run_in_threadpool(db.fetch_one, insert_sql, params)
        rows.append(row)
    return {"data": rows}
