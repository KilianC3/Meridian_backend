from __future__ import annotations

import pytest

from app.services import auth_service


def test_authenticate_success() -> None:
    access, refresh = auth_service.authenticate("admin@example.com", "password")
    assert isinstance(access, str)
    assert isinstance(refresh, str)


def test_authenticate_failure() -> None:
    with pytest.raises(Exception):
        auth_service.authenticate("admin@example.com", "wrong")
