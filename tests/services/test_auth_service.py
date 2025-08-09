from __future__ import annotations

import pytest

from app.services import auth_service


def test_authenticate_success() -> None:
    token = auth_service.authenticate("admin@example.com", "password")
    assert isinstance(token, str)


def test_authenticate_failure() -> None:
    with pytest.raises(Exception):
        auth_service.authenticate("admin@example.com", "wrong")
