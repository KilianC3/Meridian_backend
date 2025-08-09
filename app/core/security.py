from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, cast

from jose import JWTError, jwt
from passlib.hash import argon2

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def hash_password(password: str) -> str:
    return cast(str, argon2.hash(password))


def verify_password(password: str, hashed: str) -> bool:
    return cast(bool, argon2.verify(password, hashed))


def create_access_token(
    data: Dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return cast(str, jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM))


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return cast(
            Dict[str, Any],
            jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM]),
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
