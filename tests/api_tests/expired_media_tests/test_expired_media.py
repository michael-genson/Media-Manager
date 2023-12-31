import random
from collections import defaultdict
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time

from mediamanager.app import expired_media_settings
from mediamanager.models.expired_media.expired_media import ExpiredMedia
from mediamanager.models.manage_media.overseerr import OverseerrUser
from mediamanager.models.manage_media.tautulli import (
    LibraryType,
    TautulliLibrary,
    TautulliMedia,
    TautulliMediaDetail,
    TautulliMediaSummary,
)
from mediamanager.routes import expired_media as expired_media_routes
from mediamanager.services.factory import ServiceFactory
from tests.fixtures.databases.media_managers.mock_media_manager_database import RadarrMockDatabase
from tests.fixtures.databases.tautulli.mock_tautulli_database import TautulliMockDatabase
from tests.utils.generators import random_datetime, random_int, random_string


@pytest.mark.parametrize(
    "recently_added, recently_watched",
    [
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_get_expired_media(
    api_client: TestClient,
    auth_headers: dict,
    recently_added: bool,
    recently_watched: bool,
    tautulli_db: TautulliMockDatabase,
    tautulli_libraries: dict[LibraryType, TautulliLibrary],
    tautulli_movies: list[TautulliMedia],
    tautulli_shows: list[TautulliMedia],
):
    mock_current_dt = datetime.now() + timedelta(days=random_int(365 * 10, 365 * 20))

    # add media that was added and/or watched recently
    non_expired_media: defaultdict[LibraryType, list[TautulliMedia]] = defaultdict(list)
    if recently_added or recently_watched:
        for library in tautulli_libraries.values():
            media_count = random_int(1, 5)
            library.count += media_count
            for _ in range(media_count):
                recently_added_or_watched_time = random_datetime(
                    mock_current_dt - timedelta(days=(expired_media_settings.expired_media_last_watched_threshold - 1)),
                    mock_current_dt,
                )
                summary = TautulliMediaSummary(
                    section_id=library.section_id,
                    rating_key=random_string(),
                    media_type=library.section_type,
                    title=random_string(),
                    added_at=recently_added_or_watched_time if recently_added else random_datetime(),
                    last_played=recently_added_or_watched_time if recently_watched else random_datetime(),
                )
                detail = TautulliMediaDetail(
                    section_id=library.section_id,
                    rating_key=summary.rating_key,
                    media_type=LibraryType.movie,
                    title=summary.title,
                    guids=[f"tmdb://{random_int(1000, 10000)}", f"tvdb://{random_int(1000, 10000)}"],
                )

                media = TautulliMedia(library=library, media_summary=summary, media_detail=detail)
                tautulli_db.insert_media(media)
                non_expired_media[library.section_type].append(media)

    # fetch media and confirm only the new media is returned
    with freeze_time(mock_current_dt.isoformat()):
        response = api_client.get(
            expired_media_routes.router.url_path_for("get_expired_media"),
            headers=auth_headers,
        )

    response.raise_for_status()
    expired_media = [ExpiredMedia.parse_obj(data) for data in response.json()]

    non_expired_rating_keys = set()
    for library_value in non_expired_media.values():
        for media in library_value:
            non_expired_rating_keys.add(media.media_summary.rating_key)

    # compare the original media against the expired media
    expired_rating_keys = set(_.media.media_summary.rating_key for _ in expired_media)
    for media in tautulli_movies + tautulli_shows:
        assert media.media_summary.rating_key in expired_rating_keys

    # compare the non-expired media against the expired media
    for non_expired_key in non_expired_rating_keys:
        assert non_expired_key not in expired_rating_keys


@pytest.mark.parametrize("add_user", [False, True])
def test_get_expired_media_with_media(
    add_user: bool,
    api_client: TestClient,
    auth_headers: dict,
    tautulli_movies: list[TautulliMedia],
    overseerr_users: list[OverseerrUser],
    radarr_db: RadarrMockDatabase,
):
    tag_ids: list[str] = []
    user: OverseerrUser | None = None
    if add_user:
        user = random.choice(overseerr_users)
        tag = radarr_db.create_tag(f"{user.id} - {user.username or user.name}")
        tag_ids.append(tag.id)

    movie = random.choice(tautulli_movies)
    radarr_db.create_media(movie.media_detail.get_guid("tmdb"), tag_ids)  # type: ignore

    with freeze_time(datetime.now() + timedelta(days=random_int(365 * 10, 365 * 20))):
        response = api_client.get(
            expired_media_routes.router.url_path_for("get_expired_media"),
            headers=auth_headers,
        )

    response.raise_for_status()
    expired_media = [ExpiredMedia.parse_obj(data) for data in response.json()]

    found = False
    for expired_movie in expired_media:
        if expired_movie.media.media_summary.rating_key != movie.media_summary.rating_key:
            continue

        found = True
        assert expired_movie.media_url  # url is only populated if radarr media is found
        if add_user:
            assert user
            assert expired_movie.user == user
        break
    assert found


def test_get_expired_media_monitored_libraries(
    api_client: TestClient,
    auth_headers: dict,
    tautulli_movies: list[TautulliMedia],
    tautulli_shows: list[TautulliMedia],
    svcs: ServiceFactory,
):
    # fetch only movies, not shows
    movie_library_ids = {movie.library.section_id for movie in tautulli_movies}
    show_library_ids = {show.library.section_id for show in tautulli_shows}
    assert movie_library_ids
    assert show_library_ids
    assert movie_library_ids != show_library_ids

    svcs.app_config.patch_config(monitored_library_ids=list(movie_library_ids))
    with freeze_time(datetime.now() + timedelta(days=random_int(365 * 10, 365 * 20))):
        response = api_client.get(
            expired_media_routes.router.url_path_for("get_expired_media"),
            headers=auth_headers,
        )

    response.raise_for_status()
    expired_media = [ExpiredMedia.parse_obj(data) for data in response.json()]
    fetched_library_ids = {media.media.library.section_id for media in expired_media}
    assert fetched_library_ids

    for id in movie_library_ids:
        assert id in fetched_library_ids
    for id in show_library_ids:
        assert id not in fetched_library_ids
