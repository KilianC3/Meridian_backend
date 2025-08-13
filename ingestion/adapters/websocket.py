from __future__ import annotations

from typing import Any

from .base import BaseAdapter


class WebsocketAdapter(BaseAdapter):
    """Stub for websocket-based streaming clients."""

    def fetch(self, *args: Any, **kwargs: Any) -> Any:
        """Placeholder method for consuming a websocket."""
        raise NotImplementedError
