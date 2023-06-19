from __future__ import annotations

from abc import ABC
from json import JSONDecodeError

from fastapi import HTTPException
from httpx import AsyncClient, AsyncHTTPTransport, HTTPError, Response


class BaseHTTPClient(ABC):
    """
    Low level HTTP client
    """

    def __init__(
        self,
        base_headers: dict[str, str] | None = None,
        base_params: dict[str, str] | None = None,
        timeout: int = 90,
        retries: int = 3,
    ) -> None:
        self._base_headers = base_headers or {}
        self._base_params = base_params or {}
        self._timeout = timeout
        self._retries = retries

    @classmethod
    def _parse_base_url(cls, base_url: str) -> str:
        if not base_url:
            raise ValueError("base_url must not be empty")
        if base_url[-1] == "/":
            base_url = base_url[:-1]
        if "http" not in base_url:
            base_url = "https://" + base_url

        return base_url

    @property
    def client(self, *args, **kwargs) -> AsyncClient:
        """The async httpx client. Should be used with an async context manager"""

        headers = self._base_headers | kwargs.pop("headers", {})
        params = self._base_params | kwargs.pop("params", {})
        timeout = kwargs.pop("timeout", None) or self._timeout
        retries = kwargs.pop("retries", None) or self._retries

        transport = AsyncHTTPTransport(retries=retries)
        return AsyncClient(transport=transport, headers=headers, params=params, timeout=timeout, *args, **kwargs)

    def parse_response_json(self, response: Response) -> dict | list:
        try:
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            try:
                detail = response.json()
            except JSONDecodeError:
                detail = str(response)
            except Exception:
                detail = None

            raise HTTPException(response.status_code, detail=detail) from e
