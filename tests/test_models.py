from __future__ import annotations

import importlib
from types import ModuleType


def test_models_import() -> None:
    """Ensure SQLAlchemy models module imports without errors."""
    models: ModuleType = importlib.import_module("app.db.models")
    assert hasattr(models, "User")
    assert hasattr(models, "AlertRule")
