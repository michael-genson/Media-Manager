import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query, status
from httpx import HTTPError

from .. import security
from ..app import expired_media_settings, schedules, secrets, settings
from ..models.email import ExpiredMediaEmail, ExpiredMediaEmailFailure
from ..models.expired_media import (
    ExpiredMedia,
    ExpiredMediaIgnoredItemIn,
    ExpiredMediaIgnoredItems,
)
from ..models.ombi import OmbiUser
from ..models.tautulli import LibraryType, TautulliMedia
from ..scheduler import cron, scheduler
from ..services.expired_media import ExpiredMediaIgnoreListManager
from ..services.factory import ServiceFactory

_ignore_list_manager = ExpiredMediaIgnoreListManager()
router = APIRouter(
    prefix="/api/expired-media", tags=["Expired Media"], dependencies=[Depends(security.require_api_key)]
)


async def _get_expired_media(svcs: ServiceFactory, media: TautulliMedia) -> ExpiredMedia:
    try:
        if media.library.section_type is LibraryType.movie:
            media_manager_service = svcs.radarr
            db_id = media.media_detail.tmdb_guid
        elif media.library.section_type is LibraryType.show:
            media_manager_service = svcs.sonarr
            db_id = media.media_detail.tvdb_guid
        else:
            return ExpiredMedia(media=media)

        if not db_id:
            return ExpiredMedia(media=media)

        # if there are tags, one of them should be an Ombi username
        tags = await media_manager_service.get_tags_from_media(db_id)
        user: OmbiUser | None = None
        for tag in tags:
            user = await svcs.ombi.get_user_by_username(tag.label)
            if user:
                break

        media_url = await media_manager_service.get_url_for_media(db_id)
        return ExpiredMedia(media=media, media_url=media_url, user=user)
    except HTTPError:
        # the media is the only required data, so we ignore http errors such as connection issues and timeouts
        return ExpiredMedia(media=media)


@router.get("/", response_model=list[ExpiredMedia])
async def get_expired_media(
    max_results: int = Query(
        100, alias="maxResults", description="The maximum number of media items to return. Set to -1 to bypass"
    ),
    ignore_http_errors: bool = Query(
        False,
        alias="ignoreHttpErrors",
        description="If set, HTTP errors will be skipped over when fetching media details",
    ),
) -> list[ExpiredMedia]:
    """Fetch expired media from Tautulli, and Ombi user data, when available"""

    svcs = ServiceFactory()
    try:
        ignored_items = await _ignore_list_manager.load()
    except HTTPException:
        ignored_items = None

    tautulli_expired_media = await svcs.tautulli.get_all_expired_media(
        expired_media_settings.expired_media_min_age,
        expired_media_settings.expired_media_last_watched_threshold,
        settings.monitored_libraries,
        [item.rating_key for item in ignored_items.items] if ignored_items else None,
        max_results,
        ignore_http_errors,
    )

    expired_media: list[ExpiredMedia] = await asyncio.gather(
        *[_get_expired_media(svcs, media) for media in tautulli_expired_media]
    )
    return sorted(expired_media, key=lambda x: x.media.media_summary.added_at)


@scheduler.task(cron(schedules.scheduler_expired_media))
async def _send_notification_of_expired_media() -> None:
    svcs = ServiceFactory()

    try:
        expired_media = await get_expired_media(max_results=-1, ignore_http_errors=True)
        if not expired_media:
            return

        csv_file = svcs.data_exporter.create_csv([media for media in expired_media])
        msg = ExpiredMediaEmail().message(secrets.smtp_sender, settings.admin_email, len(expired_media), csv_file)
        svcs.smtp.send(msg)

    except Exception:
        msg = ExpiredMediaEmailFailure().message(secrets.smtp_sender, settings.admin_email)
        svcs.smtp.send(msg)
        raise


@router.post("/notify", status_code=status.HTTP_204_NO_CONTENT)
async def send_notification_of_expired_media(background_tasks: BackgroundTasks) -> None:
    background_tasks.add_task(_send_notification_of_expired_media)


@router.get("/ignore-list", response_model=ExpiredMediaIgnoredItems)
async def get_ignore_list() -> ExpiredMediaIgnoredItems:
    return await _ignore_list_manager.load()


@router.post("/ignore-list/bulk", status_code=status.HTTP_201_CREATED)
async def add_ignored_media_bulk(media: list[ExpiredMediaIgnoredItemIn]) -> None:
    await _ignore_list_manager.add(media)


@router.post("/ignore-list", status_code=status.HTTP_201_CREATED)
async def add_ignored_media(media: ExpiredMediaIgnoredItemIn = Depends()) -> None:
    return await add_ignored_media_bulk([media])


@router.delete("/ignore-list/bulk", status_code=status.HTTP_200_OK)
async def delete_ignored_media_bulk(rating_keys: list[str]) -> None:
    await _ignore_list_manager.delete(rating_keys)


@router.delete("/ignore-list/{ratingKey}", status_code=status.HTTP_200_OK)
async def delete_ignored_media(rating_key: str = Path(..., alias="ratingKey")) -> None:
    return await delete_ignored_media_bulk([rating_key])
