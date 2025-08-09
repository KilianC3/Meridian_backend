from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.security import decode_token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    token = auth_service.authenticate(form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme)) -> dict[str, str | list[str]]:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    user = auth_service.get_user(payload["sub"])
    return {"email": user.email, "roles": user.roles}
