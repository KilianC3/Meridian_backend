# flake8: noqa
"""Adapter utilities.

This module exposes :func:`adapter_factory` which dynamically imports and
instantiates adapter classes defined in the dataset registry.  It keeps the
scheduler decoupled from concrete adapter implementations.
"""

from __future__ import annotations

import importlib
from typing import Any, Dict


def _import_from_path(path: str) -> Any:
    """Import ``path`` and return the referenced attribute."""

    module_name, attr = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def adapter_factory(dataset_id: str, cfg: Dict[str, Any]):
    """Instantiate an adapter based on ``cfg``.

    Parameters
    ----------
    dataset_id:
        Identifier of the dataset to instantiate.
    cfg:
        Configuration dictionary for the dataset taken from the registry.  The
        ``adapter`` field should contain a dotted import path to the adapter
        class.  Any extra keys in ``cfg`` (apart from the standard registry
        fields) are forwarded as keyword arguments to the adapter constructor.
        If a ``transform`` path is supplied it will override the adapter's
        ``transform`` method after instantiation.
    """

    adapter_cls = _import_from_path(cfg["adapter"])

    # Filter out registry-specific keys, everything else becomes an adapter arg
    std_keys = {
        "name",
        "label",
        "cadence",
        "adapter",
        "transform",
        "target_table",
        "conflict_keys",
        "enabled",
    }
    kwargs = {k: v for k, v in cfg.items() if k not in std_keys}

    adapter = adapter_cls(**kwargs)
    setattr(adapter, "dataset_id", dataset_id)

    transform_path = cfg.get("transform")
    if transform_path:
        transform_fn = _import_from_path(transform_path)

        def _wrapper(item: Any, _fn=transform_fn):
            # Many transform helpers expect an iterable of records.  Wrap to
            # provide the single-record interface adapters use.
            return _fn([item])

        adapter.transform = _wrapper  # type: ignore[attr-defined]

    return adapter


__all__ = ["adapter_factory"]
