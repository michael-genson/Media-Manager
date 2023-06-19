import asyncio
from abc import ABC, abstractmethod
from typing import Awaitable

from ..clients.media_managers import MediaManagerBaseClient, RadarrClient, SonarrClient
from ..models.media_managers import BaseMediaManagerMedia, MediaManagerTag


class MediaManagerServiceBase(ABC):
    def __init__(self, base_url: str, api_key: str) -> None:
        self._client = self._get_client(base_url, api_key)
        self._media_by_db_id: dict[str, BaseMediaManagerMedia | None] = {}
        self._tags_by_id: dict[str, MediaManagerTag | None] = {}
        """Internal cache for tags by id"""

    @classmethod
    @abstractmethod
    def _get_client(cls, *args, **kwargs) -> MediaManagerBaseClient:
        ...

    async def _get_tag(self, tag_id: str) -> MediaManagerTag | None:
        if tag_id not in self._tags_by_id:
            self._tags_by_id[tag_id] = await self._client.get_tag(tag_id)

        return self._tags_by_id[tag_id]

    async def get_tags_from_media(self, media_db_id: str) -> list[MediaManagerTag]:
        """
        Gets all tags for a particular media item

        :param str media_db_id: The database id of the media (e.g. TMDB movie id)
        """

        if media_db_id not in self._media_by_db_id:
            self._media_by_db_id[media_db_id] = await self._client.get_media(media_db_id)

        media = self._media_by_db_id[media_db_id]
        if not media or not media.tag_ids:
            return []

        tag_futures: list[Awaitable[MediaManagerTag | None]] = [self._get_tag(tag_id) for tag_id in media.tag_ids]
        return [tag for tag in await asyncio.gather(*tag_futures) if tag]

    async def get_url_for_media(self, media_db_id: str) -> str | None:
        if media_db_id not in self._media_by_db_id:
            self._media_by_db_id[media_db_id] = await self._client.get_media(media_db_id)

        media = self._media_by_db_id[media_db_id]
        return media.db_url if media else None


class RadarrService(MediaManagerServiceBase):
    @classmethod
    def _get_client(cls, *args, **kwargs) -> RadarrClient:
        return RadarrClient(*args, **kwargs)


class SonarrService(MediaManagerServiceBase):
    @classmethod
    def _get_client(cls, *args, **kwargs) -> SonarrClient:
        return SonarrClient(*args, **kwargs)
