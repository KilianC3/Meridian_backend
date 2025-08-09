from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> auth_service.User:
    try:
        payload = auth_service.decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    return auth_service.get_user(payload.get("sub"))


def require_roles(*roles: str) -> Callable[[auth_service.User], auth_service.User]:
    def checker(
        user: auth_service.User = Depends(get_current_user),
    ) -> auth_service.User:
        if roles and not set(roles).intersection(user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="insufficient roles"
            )
        return user

    return checker
