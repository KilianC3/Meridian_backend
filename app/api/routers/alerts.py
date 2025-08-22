from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["alerts"])


@router.api_route("/alerts", methods=["GET", "POST", "PUT", "DELETE"])  # type: ignore[misc]
async def alerts_not_implemented() -> None:
    """Placeholder endpoint returning 501 until alerts are supported."""
    raise HTTPException(status_code=501, detail="alerts API not implemented")
