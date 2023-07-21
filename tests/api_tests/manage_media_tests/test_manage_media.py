import random

from fastapi.testclient import TestClient

from mediamanager.models.tautulli import TautulliMedia
from mediamanager.routes import manage_media
from tests.fixtures.databases.media_managers.mock_media_manager_database import RadarrMockDatabase
from tests.utils.generators import random_int, random_string


def test_remove_media(
    api_client: TestClient, auth_headers: dict, tautulli_movies: list[TautulliMedia], radarr_db: RadarrMockDatabase
):
    for movie in tautulli_movies:
        radarr_db.create_media(movie.media_detail.get_guid("tmdb"))  # type: ignore

    original_radarr_count = len(radarr_db._get_all(radarr_db.MEDIA))
    movie_to_remove = random.choice(tautulli_movies)
    response = api_client.delete(
        manage_media.router.url_path_for("remove_media", ratingKey=movie_to_remove.media_summary.rating_key),
        headers=auth_headers,
    )

    response.raise_for_status()

    # verify the movie was deleted
    all_radarr_movies = radarr_db._get_all(radarr_db.MEDIA)
    guid = movie_to_remove.media_detail.get_guid("tmdb")
    assert guid

    assert len(all_radarr_movies) == original_radarr_count - 1
    assert guid not in set(movie["db_id"] for movie in all_radarr_movies)

    # verify a 400 error is raised if the media can't be found
    response = api_client.delete(
        manage_media.router.url_path_for("remove_media", ratingKey=random_string()),
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_remove_media_bulk(
    api_client: TestClient, auth_headers: dict, tautulli_movies: list[TautulliMedia], radarr_db: RadarrMockDatabase
):
    for movie in tautulli_movies:
        radarr_db.create_media(movie.media_detail.get_guid("tmdb"))  # type: ignore

    original_radarr_count = len(radarr_db._get_all(radarr_db.MEDIA))
    movies_to_remove = random.sample(tautulli_movies, random_int(2, 5))
    response = api_client.post(
        manage_media.router.url_path_for("remove_media_bulk"),
        json=[movie.media_summary.rating_key for movie in movies_to_remove],
        headers=auth_headers,
    )

    response.raise_for_status()
    assert response.json() == {"failedItems": {}}

    # verify the movie was deleted
    all_radarr_movies = radarr_db._get_all(radarr_db.MEDIA)
    guids = set(movie.media_detail.get_guid("tmdb") for movie in movies_to_remove)
    assert len(guids) == len([guid for guid in guids if guid])

    all_radarr_guids = set(movie["db_id"] for movie in all_radarr_movies)
    assert len(all_radarr_guids) == original_radarr_count - len(guids)
    for guid in guids:
        assert guid not in all_radarr_guids

    # verify errors are returned in a list
    movie_to_remove = None
    for movie in tautulli_movies:
        if movie not in movies_to_remove:
            movie_to_remove = movie
            break

    assert movie_to_remove
    rating_keys = [movie_to_remove.media_summary.rating_key, random_string(), random_string()]
    _, invalid_key_1, invalid_key_2 = rating_keys
    response = api_client.post(
        manage_media.router.url_path_for("remove_media_bulk"),
        json=rating_keys,
        headers=auth_headers,
    )

    response.raise_for_status()
    failed_items: dict[str, dict] = response.json()["failedItems"]
    assert len(failed_items) == 2
    assert invalid_key_1 in failed_items
    assert invalid_key_2 in failed_items

    # verify the valid movie was deleted
    all_radarr_movies = radarr_db._get_all(radarr_db.MEDIA)
    all_radarr_guids = set(movie["db_id"] for movie in all_radarr_movies)
    assert len(all_radarr_guids) == original_radarr_count - len(guids) - 1
    assert movie_to_remove.media_detail.get_guid("tmdb") not in all_radarr_guids
