from __future__ import annotations

from typing import Dict, List

from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password


class User:
    def __init__(self, email: str, password: str, roles: List[str]):
        self.email = email
        self.password_hash = hash_password(password)
        self.roles = roles


USERS: Dict[str, User] = {
    "admin@example.com": User("admin@example.com", "password", ["admin"])
}


def authenticate(email: str, password: str) -> str:
    user = USERS.get(email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )
    return create_access_token({"sub": email, "roles": user.roles})


def get_user(email: str) -> User:
    user = USERS.get(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return user
