import asyncio

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from mediamanager.models.app.api import GenericCollection

from .. import security
from ..models.manage_media.tautulli import TautulliFailedDeletedMedia, TautulliLibrary
from ..services.factory import ServiceFactory

router = APIRouter(prefix="/api/manage-media", tags=["Manage Media"], dependencies=[Depends(security.get_current_user)])


class RemoveMediaException(Exception):
    """Base Remove Media Exception to store the rating key along with the cause"""

    def __init__(self, rating_key: str, *args, **kwargs) -> None:
        self.rating_key = rating_key
        super().__init__(*args, **kwargs)

    @property
    def detail(self) -> str:
        detail: str | None = None
        if isinstance(self.__cause__, ValueError):
            detail = str(self.__cause__)

        return detail or "unknown error"


async def _remove_media(svcs: ServiceFactory, rating_key: str) -> None:
    try:
        if not (tautulli_detail := await svcs.tautulli.get_media_detail(rating_key)):
            raise ValueError(f'Unable to find Tautulli Media with rating key "{rating_key}"')

        if not (media_manager_service := svcs.get_media_manager_service(tautulli_detail.media_type)):
            raise ValueError(f'Unsupported media type "{tautulli_detail.media_type.value}"')

        if not (db_id := tautulli_detail.get_guid(media_manager_service.guid_name)):
            raise ValueError(f"Missing {media_manager_service.guid_name} guid")

        if not (media := await media_manager_service.get_media_by_db_id(db_id)):
            raise ValueError(f"Unable to locate media in {media_manager_service.service_name}")

        # delete media from media manager, including files on disk
        # we don't do anything with Ombi since a job auto-updates media status
        return await media_manager_service.delete_media(media.id, delete_files=True)
    except Exception as e:
        raise RemoveMediaException(rating_key) from e


@router.get("/libraries", response_model=GenericCollection[TautulliLibrary])
async def get_all_libraries() -> GenericCollection[TautulliLibrary]:
    svcs = ServiceFactory()
    libraries = await svcs.tautulli.get_all_libraries()
    return GenericCollection(items=libraries)


@router.delete("/media/{ratingKey}", status_code=status.HTTP_200_OK)
async def remove_media(rating_key: str = Path(..., alias="ratingKey")) -> None:
    """Removes media from all systems"""

    svcs = ServiceFactory()
    try:
        return await _remove_media(svcs, rating_key)
    except RemoveMediaException as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Failed to remove media: {e.detail}") from e


@router.post("/media/remove-bulk", response_model=TautulliFailedDeletedMedia)
async def remove_media_bulk(rating_keys: list[str] = Body(..., alias="ratingKeys")) -> TautulliFailedDeletedMedia:
    """Removes media from all systems. If media is unable to be removed, it's returned in the response body"""

    svcs = ServiceFactory()
    results: list[RemoveMediaException | None] = await asyncio.gather(
        *[_remove_media(svcs, rating_key) for rating_key in rating_keys], return_exceptions=True
    )

    failures: list[RemoveMediaException] = [ex for ex in results if ex is not None]
    return TautulliFailedDeletedMedia(
        failed_items={
            failure.rating_key: await svcs.tautulli.get_media_detail(failure.rating_key, ignore_http_errors=True)
            for failure in failures
        }
    )
