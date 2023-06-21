from ...clients.mock_http_client import HTTPMethod
from .._base import BaseMockDatabase


class OmbiMockDatabase(BaseMockDatabase):
    USERS = "users"

    def route(
        self,
        method: HTTPMethod,
        url: str,
        *args,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        **kwargs,
    ):
        if url.endswith("/Identity/Users") and method == HTTPMethod.GET:
            return self._200(self._get_all(self.USERS))
        else:
            return self._404()
