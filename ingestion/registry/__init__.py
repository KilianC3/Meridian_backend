"""Dataset registry utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore[import-untyped]


def load_registry(path: str | Path | None = None) -> Dict[str, Any]:
    """Load the dataset registry from ``datasets.yaml``.

    Parameters
    ----------
    path:
        Optional path override.  By default ``datasets.yaml`` in this package
        is used.
    """

    if path is None:
        path = Path(__file__).with_name("datasets.yaml")

    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


__all__ = ["load_registry"]
