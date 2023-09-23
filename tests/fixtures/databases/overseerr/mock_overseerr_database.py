from ...clients.mock_http_client import HTTPMethod
from .._base import BaseMockDatabase


class OverseerrMockDatabase(BaseMockDatabase):
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
        if "/user/" in url and method == HTTPMethod.GET:
            data = self._get(self.USERS, url.rsplit("/", maxsplit=1)[-1])
            if data is None:
                return self._404()
            else:
                return self._200(data)
        else:
            return self._404()
