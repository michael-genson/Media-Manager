import pytest

from mediamanager.clients.ombi import OmbiClient
from mediamanager.models.manage_media.ombi import OmbiUser
from tests.fixtures.clients.mock_http_client import MockHTTPClient
from tests.utils.generators import random_datetime, random_email, random_string

from .mock_ombi_database import OmbiMockDatabase

_mock_ombi_db = OmbiMockDatabase()


@pytest.fixture
def ombi_db() -> OmbiMockDatabase:
    return _mock_ombi_db


@pytest.fixture
def ombi_users() -> list[OmbiUser]:
    users: list[OmbiUser] = []
    for _ in range(10):
        user = OmbiUser(
            id=random_string(),
            user_name=random_string(),
            email_address=random_email(),
            alias=random_string(),
            last_logged_in=random_datetime(),
            has_logged_in=True,
        )

        _mock_ombi_db._insert(_mock_ombi_db.USERS, user.id, user.dict())
        users.append(user)

    return users


### Setup and Teardown ###


@pytest.fixture(scope="session", autouse=True)
def mock_ombi_database():
    mp = pytest.MonkeyPatch()
    mp.setattr(OmbiClient, "client", MockHTTPClient(_mock_ombi_db))
    yield


@pytest.fixture(autouse=True)
def clean_up_database():
    yield
    _mock_ombi_db.db.clear()
