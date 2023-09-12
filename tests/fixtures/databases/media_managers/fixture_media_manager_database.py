import pytest

from mediamanager.clients.media_managers import RadarrClient, SonarrClient
from mediamanager.models.manage_media.media_managers import MediaManagerTag, RadarrMedia, SonarrMedia
from tests.fixtures.clients.mock_http_client import MockHTTPClient
from tests.utils.generators import random_int, random_string

from .mock_media_manager_database import RadarrMockDatabase, SonarrMockDatabase

_mock_radarr_db = RadarrMockDatabase()
_mock_sonarr_db = SonarrMockDatabase()


@pytest.fixture
def radarr_db() -> RadarrMockDatabase:
    return _mock_radarr_db


@pytest.fixture
def sonarr_db() -> SonarrMockDatabase:
    return _mock_sonarr_db


@pytest.fixture
def radarr_media() -> list[RadarrMedia]:
    return [_mock_radarr_db.create_media(str(random_int(1000, 10000))) for _ in range(10)]


@pytest.fixture
def radarr_tags() -> list[MediaManagerTag]:
    return [_mock_radarr_db.create_tag(random_string()) for _ in range(10)]


@pytest.fixture
def sonarr_media() -> list[SonarrMedia]:
    return [_mock_sonarr_db.create_media(str(random_int(1000, 10000))) for _ in range(10)]


@pytest.fixture
def sonarr_tags() -> list[MediaManagerTag]:
    return [_mock_sonarr_db.create_tag(random_string()) for _ in range(10)]


### Setup and Teardown ###


@pytest.fixture(scope="session", autouse=True)
def mock_media_manager_databases():
    mp = pytest.MonkeyPatch()
    mp.setattr(RadarrClient, "client", MockHTTPClient(_mock_radarr_db))
    mp.setattr(SonarrClient, "client", MockHTTPClient(_mock_sonarr_db))
    yield


@pytest.fixture(autouse=True)
def clean_up_database():
    yield
    _mock_radarr_db.db.clear()
    _mock_sonarr_db.db.clear()
