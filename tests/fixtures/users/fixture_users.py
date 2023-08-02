from datetime import timedelta

import pytest

from mediamanager.models.users.users import User
from mediamanager.services.factory import ServiceFactory
from tests.utils.generators import random_email, random_string


@pytest.fixture()
def user(svcs: ServiceFactory) -> User:
    return svcs.users.create_user(random_email(), random_string())


@pytest.fixture()
def user_token(user: User) -> str:
    return user.create_token(timedelta(days=365 * 1000))


@pytest.fixture()
def auth_headers(user_token: str) -> dict:
    return {"Authorization": f"Bearer {user_token}"}
