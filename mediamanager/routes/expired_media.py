import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query, status

from .. import security
from ..app import expired_media_settings, schedules
from ..models.app.api import GenericCollection
from ..models.app.email import ExpiredMediaEmail, ExpiredMediaEmailFailure
from ..models.expired_media.expired_media import ExpiredMedia
from ..models.expired_media.ignored_items import (
    ExpiredMediaIgnoredItem,
    ExpiredMediaIgnoredItemIn,
)
from ..models.manage_media.ombi import OmbiUser
from ..models.manage_media.tautulli import TautulliMedia
from ..scheduler import cron, scheduler
from ..services.expired_media import ExpiredMediaIgnoreListManager
from ..services.factory import ServiceFactory
from ..settings import app_settings

_ignore_list_manager = ExpiredMediaIgnoreListManager()
settings = app_settings.AppSettings()

router = APIRouter(
    prefix="/api/expired-media", tags=["Expired Media"], dependencies=[Depends(security.get_current_user)]
)


async def _get_expired_media(svcs: ServiceFactory, media: TautulliMedia) -> ExpiredMedia:
    try:
        media_manager_service = svcs.get_media_manager_service(media.library.section_type)
        if not media_manager_service:
            return ExpiredMedia(media=media)

        db_id = media.media_detail.get_guid(media_manager_service.guid_name)
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
    except HTTPException:
        # the media is the only required data, so we ignore http errors such as connection issues and timeouts
        return ExpiredMedia(media=media)


@router.get("", response_model=list[ExpiredMedia])
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
        ignored_items = _ignore_list_manager.get_all()
    except HTTPException:
        ignored_items = None

    tautulli_expired_media = await svcs.tautulli.get_all_expired_media(
        expired_media_settings.expired_media_min_age,
        expired_media_settings.expired_media_last_watched_threshold,
        settings.monitored_libraries,
        [item.rating_key for item in ignored_items] if ignored_items else None,
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
    admins = svcs.users.get_all_users(is_default_user=False)  # TODO: filter this to only admins

    try:
        expired_media = await get_expired_media(max_results=-1, ignore_http_errors=True)
        if not expired_media:
            return

        csv_file = svcs.data_exporter.create_csv([media for media in expired_media])
        msgs = [
            ExpiredMediaEmail().message(svcs.app_config.config.smtp_sender, admin.email, len(expired_media), csv_file)
            for admin in admins
        ]

        await svcs.smtp.send_all(msgs)

    except Exception:
        msgs = [ExpiredMediaEmailFailure().message(svcs.app_config.config.smtp_sender, admin.email) for admin in admins]

        await svcs.smtp.send_all(msgs)
        raise


@router.post("/notify", status_code=status.HTTP_204_NO_CONTENT)
async def send_notification_of_expired_media(background_tasks: BackgroundTasks) -> None:
    background_tasks.add_task(_send_notification_of_expired_media)


@router.get("/ignore-list", response_model=GenericCollection[ExpiredMediaIgnoredItem])
async def get_ignore_list() -> GenericCollection[ExpiredMediaIgnoredItem]:
    return GenericCollection(items=_ignore_list_manager.get_all())


@router.post(
    "/ignore-list/bulk", status_code=status.HTTP_201_CREATED, response_model=GenericCollection[ExpiredMediaIgnoredItem]
)
async def add_ignored_media_bulk(media: list[ExpiredMediaIgnoredItemIn]) -> GenericCollection[ExpiredMediaIgnoredItem]:
    return GenericCollection(items=await _ignore_list_manager.add(media))


@router.post("/ignore-list", status_code=status.HTTP_201_CREATED, response_model=ExpiredMediaIgnoredItem)
async def add_ignored_media(media: ExpiredMediaIgnoredItemIn = Depends()) -> ExpiredMediaIgnoredItem:
    return (await add_ignored_media_bulk([media])).items[0]


@router.delete(
    "/ignore-list/bulk", status_code=status.HTTP_200_OK, response_model=GenericCollection[ExpiredMediaIgnoredItem]
)
async def delete_ignored_media_bulk(rating_keys: list[str]) -> GenericCollection[ExpiredMediaIgnoredItem]:
    return GenericCollection(items=_ignore_list_manager.delete(rating_keys))


@router.delete("/ignore-list/{ratingKey}", status_code=status.HTTP_200_OK, response_model=ExpiredMediaIgnoredItem)
async def delete_ignored_media(rating_key: str = Path(..., alias="ratingKey")) -> ExpiredMediaIgnoredItem:
    return (await delete_ignored_media_bulk([rating_key])).items[0]
