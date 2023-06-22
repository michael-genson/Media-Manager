from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..databases._base import BaseMockDatabase


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class MockHTTPClient:
    def __init__(self, db: BaseMockDatabase) -> None:
        self.db = db
        self._enabled: bool = False

    def _assert_enabled(self) -> None:
        if not self._enabled:
            raise Exception('Client must be used in "async with"')

    async def __aenter__(self, *args, **kwargs):
        self._enabled = True
        return self

    async def __aexit__(self, *args, **kwargs):
        self._enabled = False

    async def get(self, *args, **kwargs):
        self._assert_enabled()
        return self.db.route(HTTPMethod.GET, *args, **kwargs)

    async def post(self, *args, **kwargs):
        self._assert_enabled()
        return self.db.route(HTTPMethod.POST, *args, **kwargs)

    async def delete(self, *args, **kwargs):
        self._assert_enabled()
        return self.db.route(HTTPMethod.DELETE, *args, **kwargs)
