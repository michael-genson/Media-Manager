import asyncio
from datetime import UTC, datetime
from typing import Awaitable

from httpx import HTTPError

from ..clients.tautulli import TautulliClient
from ..models.tautulli import (
    OrderDirection,
    TautulliLibrary,
    TautulliMedia,
    TautulliMediaDetail,
    TautulliMediaSummary,
)


class TautulliService:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._client = self._get_client(base_url, api_key)
        self._all_libraries: list[TautulliLibrary] | None = None
        """Internal cache for all libraries"""
        self._media_detail_by_rating_key: dict[str, TautulliMediaDetail] = {}
        """Internal cache for media details by rating key"""

    @classmethod
    def _get_client(cls, *args, **kwargs) -> TautulliClient:
        return TautulliClient(*args, **kwargs)

    @classmethod
    def _is_expired(self, min_age: int, last_watched_threshold: int, summary: TautulliMediaSummary) -> bool:
        """Checks if a media item is expired"""

        current_time = datetime.now(tz=UTC)
        media_age = current_time - summary.added_at
        if media_age.days < min_age:
            return False

        if summary.last_played:
            return (current_time - summary.last_played).days >= last_watched_threshold
        else:
            # the media has never been watched, so we compare against its age instead
            return media_age.days >= last_watched_threshold

    async def get_media_detail(self, rating_key: str, ignore_http_errors: bool = False) -> TautulliMediaDetail | None:
        try:
            if rating_key not in self._media_detail_by_rating_key:
                self._media_detail_by_rating_key[rating_key] = await self._client.get_library_media_detail(rating_key)
        except HTTPError:
            if ignore_http_errors:
                return None
            else:
                raise

        return self._media_detail_by_rating_key[rating_key]

    async def _get_expired_media(
        self, library: TautulliLibrary, summary: TautulliMediaSummary, ignore_http_errors: bool = False
    ) -> TautulliMedia | None:
        detail = await self.get_media_detail(summary.rating_key, ignore_http_errors)
        if not detail:
            return None

        return TautulliMedia(library=library, media_summary=summary, media_detail=detail)

    async def get_all_expired_media(
        self,
        min_age: int,
        last_watched_threshold: int,
        monitored_libraries: list[str] | None = None,
        ignored_rating_keys: list[str] | None = None,
        max_results: int = 100,
        ignore_http_errors: bool = False,
    ) -> list[TautulliMedia]:
        """
        Fetch all expired media.

        :param int min_age: The minimum age in days to consider media for expiration
        :param int last_watched_threshold: The number of days since media was last watched to be considered expired
        :param list[str] | None monitored_libraries: Optional list of library names to consider for expired media
        :param list[str] | None ignored_rating_keys: Optional `rating_key` list to ignore
        :param int max_results: The maximum number of media items to return. Set to -1 to bypass
        :param bool ignore_http_errors: If set, HTTP errors will be skipped over when fetching media details
        """
        if monitored_libraries:
            monitored_libraries = [_.lower() for _ in monitored_libraries]

        if not self._all_libraries:
            self._all_libraries = await self._client.get_libraries()

        expired_media_futures: list[Awaitable[TautulliMedia | None]] = []
        for library in self._all_libraries:
            if not library.is_active:
                continue
            if not library.count:
                continue
            if monitored_libraries and library.section_name.lower() not in monitored_libraries:
                continue

            media_summaries = await self._client.get_library_media_summaries(
                section_id=library.section_id,
                order_column="last_played",
                order_dir=OrderDirection.ascending,
                length=library.count,
            )

            for summary in media_summaries:
                if ignored_rating_keys and summary.rating_key in ignored_rating_keys:
                    continue
                if not self._is_expired(min_age, last_watched_threshold, summary):
                    continue

                expired_media_futures.append(self._get_expired_media(library, summary, ignore_http_errors))
                if max_results > 0 and len(expired_media_futures) >= max_results:
                    break

        return [expired_media for expired_media in await asyncio.gather(*expired_media_futures) if expired_media]
