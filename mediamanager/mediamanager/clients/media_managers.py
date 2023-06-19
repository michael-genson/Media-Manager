from abc import abstractmethod

from httpx import HTTPStatusError

from ..models.media_managers import BaseMediaManagerMedia, MediaManagerTag, RadarrMedia, SonarrMedia
from ._base import BaseHTTPClient


class MediaManagerBaseClient(BaseHTTPClient):
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = self._parse_base_url(base_url)
        return super().__init__(base_headers={"X-Api-Key": api_key})

    def _url(self, endpoint: str, version: int = 3) -> str:
        if not endpoint or endpoint == "/":
            raise ValueError("endpoint must not be empty")
        if endpoint[0] == "/":
            endpoint = endpoint[1:]

        return f"{self.base_url}/api/v{version}/{endpoint}"

    async def get_tag(self, tag_id: str) -> MediaManagerTag | None:
        try:
            async with self.client as client:
                r = await client.get(self._url(f"/tag/{tag_id}"))
                data = self.parse_response_json(r)

        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

        return MediaManagerTag.parse_obj(data)

    @abstractmethod
    async def get_media(self, db_id: str) -> BaseMediaManagerMedia | None:
        ...


class RadarrClient(MediaManagerBaseClient):
    async def get_media(self, db_id: str) -> RadarrMedia | None:
        async with self.client as client:
            r = await client.get(self._url("/movie"), params={"tmdbId": db_id})
            data = self.parse_response_json(r)

        # there can only be exactly 0 or 1 responses
        if not data:
            return None

        return RadarrMedia.parse_obj(data[0])


class SonarrClient(MediaManagerBaseClient):
    async def get_media(self, db_id: str) -> SonarrMedia | None:
        async with self.client as client:
            r = await client.get(self._url("/series"), params={"tvdbId": db_id})
            data = self.parse_response_json(r)

        # there can only be exactly 0 or 1 responses
        if not data:
            return None

        return SonarrMedia.parse_obj(data[0])
