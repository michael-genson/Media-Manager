from abc import abstractproperty, abstractmethod

from mediamanager.mediamanager.models.media_managers import (
    BaseMediaManagerMedia,
    MediaManagerTag,
    RadarrMedia,
    SonarrMedia,
)

from tests.fixtures.clients.mock_http_client import HTTPMethod
from tests.utils.generators import random_string
from .._base import BaseMockDatabase


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
                if record["db_id"] == db_id:
                    return self._200([record])

            return self._200([])
        elif "/tag/" in url and method == HTTPMethod.GET:
            tag_id = url.rsplit("/", maxsplit=1)[-1]
            return self._200(self._get(self.TAGS, tag_id))
        else:
            return self._404()

    @abstractmethod
    def create_media(self, db_id: str, tag_ids: list[str] | None = None) -> BaseMediaManagerMedia:
        ...

    def create_tag(self, label: str) -> MediaManagerTag:
        tag = MediaManagerTag(id=random_string(), label=label)
        self._insert(self.TAGS, tag.id, tag.dict())
        return tag


class RadarrMockDatabase(MediaManagerMockDatabaseBase):
    @property
    def _base_endpoint(self) -> str:
        return "movie"

    @property
    def _media_param(self) -> str:
        return "tmdbId"

    def create_media(self, db_id: str, tag_ids: list[str] | None = None) -> RadarrMedia:
        if tag_ids is None:
            tag_ids = []

        media = RadarrMedia(
            id=random_string(),
            title=random_string(),
            tags=tag_ids,
            path=random_string(),
            root_folder_path=random_string(),
            db_id=db_id,
        )
        self._insert(self.MEDIA, media.id, media.dict())
        return media


class SonarrMockDatabase(MediaManagerMockDatabaseBase):
    @property
    def _base_endpoint(self) -> str:
        return "series"

    @property
    def _media_param(self) -> str:
        return "tvdbId"

    def create_media(self, db_id: str, tag_ids: list[str] | None = None) -> SonarrMedia:
        if tag_ids is None:
            tag_ids = []

        media = SonarrMedia(
            id=random_string(),
            title=random_string(),
            tags=tag_ids,
            path=random_string(),
            root_folder_path=random_string(),
            db_id=db_id,
        )
        self._insert(self.MEDIA, media.id, media.dict())
        return media
