from __future__ import annotations

from fastapi import HTTPException
from pydantic import BaseModel


class ErrorModel(BaseModel):
    message: str
    detail: str | None = None


def problem(status_code: int, message: str, detail: str | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ErrorModel(message=message, detail=detail).model_dump(),
    )
