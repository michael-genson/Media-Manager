import json

from abc import ABC, abstractmethod
from collections import defaultdict
from fastapi import status
from typing import Any
from fastapi.encoders import jsonable_encoder

from httpx import Request, Response

from ..clients.mock_http_client import HTTPMethod


class BaseMockDatabase(ABC):
    def __init__(self) -> None:
        self.db: defaultdict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    def _dummy_request(self) -> Request:
        return Request("", "")

    def _200(self, payload: dict | list | None = None) -> Response:
        content = json.dumps(jsonable_encoder(payload)) or ""
        return Response(status.HTTP_200_OK, content=content.encode(), request=self._dummy_request())

    def _404(self) -> Response:
        return Response(status.HTTP_404_NOT_FOUND, request=self._dummy_request())

    def _get_all(self, db_key: str) -> list[dict[str, Any]]:
        return list(self.db[db_key].values())

    def _get(self, db_key: str, pk: str) -> dict[str, Any] | None:
        return self.db[db_key].get(pk)

    def _insert(self, db_key: str, pk: str, data: dict[str, Any]) -> None:
        self.db[db_key][pk] = data

    def _delete(self, db_key: str, pk: str) -> dict[str, Any] | None:
        return self.db[db_key].pop(pk, None)

    @abstractmethod
    def route(
        self,
        method: HTTPMethod,
        url: str,
        *args,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        **kwargs,
    ) -> Response:
        ...
