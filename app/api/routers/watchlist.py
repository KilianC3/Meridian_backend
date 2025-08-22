from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["watchlist"])


@router.api_route("/watchlist", methods=["GET", "POST", "PUT", "DELETE"])  # type: ignore[misc]
async def watchlist_not_implemented() -> None:
    """Placeholder endpoint returning 501 until watchlists are supported."""
    raise HTTPException(status_code=501, detail="watchlist API not implemented")
