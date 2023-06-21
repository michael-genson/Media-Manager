from tests.utils.generators import random_int, random_string
from .mock_media_manager_database import RadarrMockDatabase, SonarrMockDatabase
from mediamanager.mediamanager.clients.media_managers import RadarrClient, SonarrClient
from mediamanager.mediamanager.models.media_managers import MediaManagerTag, RadarrMedia, SonarrMedia
import pytest

_mock_radarr_db = RadarrMockDatabase()
_mock_sonarr_db = SonarrMockDatabase()


def create_radarr_media(tmdb_id: str, tag_ids: list[str] | None = None) -> RadarrMedia:
    if tag_ids is None:
        tag_ids = []

    media = RadarrMedia(
        id=random_string(),
        title=random_string(),
        tags=tag_ids,
        path=random_string(),
        root_folder_path=random_string(),
        tmdb_id=tmdb_id,
    )
    _mock_radarr_db._insert(_mock_radarr_db.MEDIA, media.id, media.dict())
    return media


def create_radarr_tag(label: str) -> MediaManagerTag:
    tag = MediaManagerTag(id=random_string(), label=label)
    _mock_radarr_db._insert(_mock_radarr_db.TAGS, tag.id, tag.dict())
    return tag


def create_sonarr_media(tvdb_id: str, tag_ids: list[str] | None = None) -> SonarrMedia:
    if tag_ids is None:
        tag_ids = []

    media = SonarrMedia(
        id=random_string(),
        title=random_string(),
        tags=tag_ids,
        path=random_string(),
        root_folder_path=random_string(),
        tvdb_id=tvdb_id,
    )
    _mock_sonarr_db._insert(_mock_sonarr_db.MEDIA, media.id, media.dict())
    return media


def create_sonarr_tag(label: str) -> MediaManagerTag:
    tag = MediaManagerTag(id=random_string(), label=label)
    _mock_sonarr_db._insert(_mock_sonarr_db.TAGS, tag.id, tag.dict())
    return tag


@pytest.fixture
def radarr_media() -> list[RadarrMedia]:
    return [create_radarr_media(str(random_int(1000, 10000))) for _ in range(10)]


@pytest.fixture
def radarr_tags() -> list[MediaManagerTag]:
    return [create_radarr_tag(random_string()) for _ in range(10)]


@pytest.fixture
def sonarr_media() -> list[SonarrMedia]:
    return [create_sonarr_media(str(random_int(1000, 10000))) for _ in range(10)]


@pytest.fixture
def sonarr_tags() -> list[MediaManagerTag]:
    return [create_sonarr_tag(random_string()) for _ in range(10)]


### Setup and Teardown ###


@pytest.fixture(scope="session", autouse=True)
def mock_media_manager_databases():
    mp = pytest.MonkeyPatch()
    mp.setattr(RadarrClient, "client", _mock_radarr_db)
    mp.setattr(SonarrClient, "client", _mock_sonarr_db)
    yield


@pytest.fixture(autouse=True)
def clean_up_database():
    yield
    _mock_radarr_db.db.clear()
    _mock_sonarr_db.db.clear()
