from ...clients.mock_http_client import HTTPMethod
from .._base import BaseMockDatabase
from abc import abstractproperty


class MediaManagerMockDatabaseBase(BaseMockDatabase):
    MEDIA = "media"
    TAGS = "tags"

    @abstractproperty
    def _base_endpoint(self) -> str:
        ...

    @abstractproperty
    def _media_param(self) -> str:
        ...

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
        if url.endswith(f"/{self._base_endpoint}") and method == HTTPMethod.GET:
            all_records = self._get_all(self.MEDIA)
            db_id: str = (params or {})[self._media_param]
            for record in all_records:
                if record[self._media_param] == db_id:
                    self._200([record])

            return self._200([])
        else:
            return self._404()


class RadarrMockDatabase(MediaManagerMockDatabaseBase):
    @property
    def _base_endpoint(self) -> str:
        return "movie"

    @property
    def _media_param(self) -> str:
        return "tmdbId"


class SonarrMockDatabase(MediaManagerMockDatabaseBase):
    @property
    def _base_endpoint(self) -> str:
        return "series"

    @property
    def _media_param(self) -> str:
        return "tvdbId"
