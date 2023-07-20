from fastapi.testclient import TestClient

from mediamanager.mediamanager.models.users.users import User
from mediamanager.mediamanager.routes import users
from mediamanager.mediamanager.services.factory import ServiceFactory
from tests.utils.generators import random_email, random_int, random_string


def test_get_all_users(api_client: TestClient, auth_headers: dict, svcs: ServiceFactory):
    new_users = [
        svcs.users.create_user(email=random_email(), password=random_string()) for _ in range(random_int(5, 10))
    ]

    r = api_client.get(users.router.url_path_for("get_all_users"), headers=auth_headers)
    r.raise_for_status()
    fetched_users = [User.parse_obj(user) for user in r.json()]

    for new_user in new_users:
        assert new_user in fetched_users


def test_get_user(api_client: TestClient, user: User, auth_headers: dict):
    r = api_client.get(users.router.url_path_for("get_user", id=user.id), headers=auth_headers)
    r.raise_for_status()
    data = r.json()

    assert user == User.parse_obj(data)


def test_get_invalid_user(api_client: TestClient, auth_headers: dict):
    r = api_client.get(users.router.url_path_for("get_user", id=random_string()), headers=auth_headers)
    assert r.status_code == 404


def test_get_user_by_email(api_client: TestClient, user: User, auth_headers: dict):
    r = api_client.get(users.router.url_path_for("get_user_by_email", email=user.email), headers=auth_headers)
    r.raise_for_status()
    data = r.json()

    assert user == User.parse_obj(data)


def test_get_user_by_email_sanitize(api_client: TestClient, user: User, auth_headers: dict):
    dirty_email = f" {user.email.upper()} "

    r = api_client.get(users.router.url_path_for("get_user_by_email", email=dirty_email), headers=auth_headers)
    r.raise_for_status()
    data = r.json()

    assert user == User.parse_obj(data)


def test_get_user_by_invalid_email(api_client: TestClient, auth_headers: dict):
    r = api_client.get(users.router.url_path_for("get_user_by_email", email=random_email()), headers=auth_headers)
    assert r.status_code == 404
