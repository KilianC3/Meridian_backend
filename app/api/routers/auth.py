from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import get_current_user
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")  # type: ignore[misc]
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    access, refresh = auth_service.authenticate(form_data.username, form_data.password)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


@router.post("/refresh")  # type: ignore[misc]
async def refresh(payload: dict[str, str]) -> dict[str, str]:
    access = auth_service.refresh(payload["refresh_token"])
    return {"access_token": access, "token_type": "bearer"}


@router.get("/me")  # type: ignore[misc]
async def me(
    user: auth_service.User = Depends(get_current_user),
) -> dict[str, str | list[str]]:
    return {"email": user.email, "roles": user.roles}
