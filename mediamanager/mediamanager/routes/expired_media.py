import asyncio
import json
from json import JSONDecodeError

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query, status
from httpx import HTTPError
from pydantic import ValidationError

from .. import security
from ..app import expired_media_settings, schedules, secrets, settings
from ..models.email import ExpiredMediaEmail, ExpiredMediaEmailFailure
from ..models.expired_media import (
    ExpiredMedia,
    ExpiredMediaIgnoredItem,
    ExpiredMediaIgnoredItemIn,
    ExpiredMediaIgnoredItems,
)
from ..models.ombi import OmbiUser
from ..models.tautulli import LibraryType, TautulliMedia
from ..scheduler import cron, scheduler
from ..services.factory import ServiceFactory

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
        ignored_items = remove_expired_ignored_items()
    except FileNotFoundError:
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


@scheduler.task(cron(schedules.expired_media))
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


def _load_expired_media(filepath: str) -> ExpiredMediaIgnoredItems:
    try:
        return ExpiredMediaIgnoredItems.parse_file(filepath)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="expired media ignore list not found on this server"
        )
    except (JSONDecodeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="expired media ignore list is in an invalid format",
        )


@router.get("/ignore-list", response_model=ExpiredMediaIgnoredItems)
async def get_ignore_list() -> ExpiredMediaIgnoredItems:
    return _load_expired_media(expired_media_settings.expired_media_ignore_filepath)


async def _process_expired_media_ignored_item(
    svcs: ServiceFactory, media: ExpiredMediaIgnoredItemIn
) -> ExpiredMediaIgnoredItem:
    if media.name:
        return ExpiredMediaIgnoredItem(**media.dict())

    detail = await svcs.tautulli.get_media_detail(media.rating_key)
    data = media.dict() | {"name": detail.title}
    return ExpiredMediaIgnoredItem(**data)


@router.post("/ignore-list/bulk", status_code=status.HTTP_201_CREATED)
async def add_ignored_media_bulk(media: list[ExpiredMediaIgnoredItemIn]) -> None:
    ignored_items = _load_expired_media(expired_media_settings.expired_media_ignore_filepath)
    existing_items = set(item.rating_key for item in ignored_items.items)

    svcs = ServiceFactory()
    items_to_add_futures = [
        _process_expired_media_ignored_item(svcs, new_media)
        for new_media in media
        if new_media.rating_key not in existing_items
    ]
    ignored_items.items.extend(await asyncio.gather(*items_to_add_futures))

    with open(expired_media_settings.expired_media_ignore_filepath, "w") as f:
        json.dump(ignored_items.dict(), f, indent=2)


@router.post("/ignore-list", status_code=status.HTTP_201_CREATED)
async def add_ignored_media(media: ExpiredMediaIgnoredItemIn = Depends()) -> None:
    return await add_ignored_media_bulk([media])


@router.delete("/ignore-list/bulk", status_code=status.HTTP_200_OK)
def delete_ignored_media_bulk(rating_keys: list[str]) -> None:
    ignored_items = _load_expired_media(expired_media_settings.expired_media_ignore_filepath)
    ignored_items.items[:] = [item for item in ignored_items.items if item.rating_key not in rating_keys]

    with open(expired_media_settings.expired_media_ignore_filepath, "w") as f:
        json.dump(ignored_items.dict(), f, indent=2)


@router.delete("/ignore-list/{ratingKey}", status_code=status.HTTP_200_OK)
def delete_ignored_media(rating_key: str = Path(..., alias="ratingKey")) -> None:
    return delete_ignored_media_bulk([rating_key])


@router.delete("/ignore-list/expired", response_model=ExpiredMediaIgnoredItems)
def remove_expired_ignored_items() -> ExpiredMediaIgnoredItems:
    """Removes all expired ignored items and returns the updated list"""

    ignored_items = _load_expired_media(expired_media_settings.expired_media_ignore_filepath)
    ignored_items.items[:] = [item for item in ignored_items.items if not item.is_expired]

    with open(expired_media_settings.expired_media_ignore_filepath, "w") as f:
        json.dump(ignored_items.dict(), f, indent=2)

    return ignored_items
