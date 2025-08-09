from __future__ import annotations

from fastapi import HTTPException


def problem(status_code: int, title: str, detail: str) -> HTTPException:
    return HTTPException(
        status_code=status_code, detail={"title": title, "detail": detail}
    )
