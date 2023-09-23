import pytest

from mediamanager.clients.overseerr import OverseerrClient
from mediamanager.models.manage_media.overseerr import OverseerrUser
from tests.fixtures.clients.mock_http_client import MockHTTPClient
from tests.utils.generators import random_datetime, random_email, random_string

from .mock_overseerr_database import OverseerrMockDatabase

_mock_overseerr_db = OverseerrMockDatabase()


@pytest.fixture
def overseerr_db() -> OverseerrMockDatabase:
    return _mock_overseerr_db


@pytest.fixture
def overseerr_users() -> list[OverseerrUser]:
    users: list[OverseerrUser] = []
    for i in range(10):
        user = OverseerrUser(
            id=i,
            email=random_email(),
            username=random_string(),
            display_name=random_string(),
            plex_id=i,
            plex_username=random_string(),
            created_at=random_datetime(),
            updated_at=random_datetime(),
        )

        _mock_overseerr_db._insert(_mock_overseerr_db.USERS, str(user.id), user.dict())
        users.append(user)

    return users


### Setup and Teardown ###


@pytest.fixture(scope="session", autouse=True)
def mock_overseerr_database():
    mp = pytest.MonkeyPatch()
    mp.setattr(OverseerrClient, "client", MockHTTPClient(_mock_overseerr_db))
    yield


@pytest.fixture(autouse=True)
def clean_up_database():
    yield
    _mock_overseerr_db.db.clear()
