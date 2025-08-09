from __future__ import annotations

import os

os.environ.setdefault("POSTGRES_DSN", "postgresql+asyncpg://user:pass@localhost/db")
os.environ.setdefault("MONGO_DSN", "mongodb://localhost:27017")
os.environ.setdefault("REDIS_DSN", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "secret")
