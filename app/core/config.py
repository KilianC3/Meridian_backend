from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field("meridian-backend", alias="APP_NAME")
    env: str = Field("development", alias="ENV")
    version: str = Field("0.1.0", alias="VERSION")
    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")
    mongo_dsn: str = Field(..., alias="MONGO_DSN")
    redis_dsn: str = Field(..., alias="REDIS_DSN")
    secret_key: str = Field(..., alias="SECRET_KEY")
    sentry_dsn: str | None = Field(None, alias="SENTRY_DSN")

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
