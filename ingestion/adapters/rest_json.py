from __future__ import annotations

from typing import Any, Iterator, Mapping

import requests  # type: ignore[import-untyped]
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .base import BaseAdapter


class RESTJsonAdapter(BaseAdapter):
    """Adapter for REST/JSON APIs with retry and backoff."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        headers: Mapping[str, str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = dict(headers or {})

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception(
            lambda e: isinstance(e, requests.HTTPError)
            and e.response is not None
            and (e.response.status_code == 429 or e.response.status_code >= 500)
        ),
        reraise=True,
    )
    def get(
        self,
        url: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        hdrs = self.headers.copy()
        if headers:
            hdrs.update(headers)
        resp = requests.get(url, params=params, headers=hdrs, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def fetch(self, cursor: Any | None = None) -> Iterator[Any]:
        path = cursor or ""
        url = f"{self.base_url}/{str(path).lstrip('/')}"
        yield self.get(url, params=None)

    def transform(self, item: Any) -> list[dict[str, Any]]:
        return [item] if isinstance(item, dict) else []
