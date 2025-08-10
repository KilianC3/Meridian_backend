from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, cast

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.hash import argon2

from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


class User:
    def __init__(self, email: str, password: str, roles: List[str]):
        self.email = email
        self.password_hash = hash_password(password)
        self.roles = roles


def hash_password(password: str) -> str:
    return cast(str, argon2.hash(password))


def verify_password(password: str, hashed: str) -> bool:
    return cast(bool, argon2.verify(password, hashed))


USERS: Dict[str, User] = {
    "admin@example.com": User("admin@example.com", "password", ["admin"])
}


def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return cast(str, jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM))


def create_access_token(data: Dict[str, Any]) -> str:
    return _create_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: Dict[str, Any]) -> str:
    return _create_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return cast(
            Dict[str, Any],
            jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM]),
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def authenticate(email: str, password: str) -> tuple[str, str]:
    user = USERS.get(email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    access = create_access_token({"sub": email, "roles": user.roles})
    refresh = create_refresh_token({"sub": email})
    return access, refresh


def refresh(refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    email = payload.get("sub")
    user = get_user(email)
    return create_access_token({"sub": email, "roles": user.roles})


def get_user(email: str | None) -> User:
    if not email or email not in USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return USERS[email]


def generate_api_key() -> tuple[str, str]:
    key = secrets.token_urlsafe(32)
    digest = hmac.new(
        settings.secret_key.encode(), key.encode(), hashlib.sha256
    ).hexdigest()
    return key, digest


def verify_api_key(key: str, digest: str) -> bool:
    expected = hmac.new(
        settings.secret_key.encode(), key.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, digest)
