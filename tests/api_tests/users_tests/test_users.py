from fastapi.testclient import TestClient

from mediamanager.models.users.users import Token, User
from mediamanager.routes import users
from mediamanager.services.factory import ServiceFactory
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


def test_create_user(api_client: TestClient, auth_headers: dict):
    email = random_email()
    password = random_string()

    r = api_client.post(
        users.router.url_path_for("create_user"), json={"email": email, "password": password}, headers=auth_headers
    )
    r.raise_for_status()

    created_user = User.parse_obj(r.json())
    assert created_user.email == email

    r = api_client.get(users.router.url_path_for("get_user_by_email", email=created_user.email), headers=auth_headers)
    r.raise_for_status()
    data = r.json()

    assert created_user == User.parse_obj(data)
    assert created_user.is_default_user is False


def test_create_existing_user(api_client: TestClient, user: User, auth_headers: dict):
    r = api_client.post(
        users.router.url_path_for("create_user"),
        json={"email": user.email, "password": random_string()},
        headers=auth_headers,
    )
    assert r.status_code == 409


def test_delete_user(api_client: TestClient, auth_headers: dict):
    user = User.parse_obj(
        api_client.post(
            users.router.url_path_for("create_user"),
            json={"email": random_email(), "password": random_string()},
            headers=auth_headers,
        ).json()
    )

    api_client.delete(users.router.url_path_for("delete_user", id=user.id), headers=auth_headers)
    r = api_client.get(users.router.url_path_for("get_user", id=user.id), headers=auth_headers)
    assert r.status_code == 404

    # the deleted user shouldn't be able to authenticate
    auth_headers["Authorization"] = f"Bearer {user.create_token()}"
    r = api_client.get(users.router.url_path_for("get_all_users"), headers=auth_headers)
    assert r.status_code == 401


def test_replace_default_users(api_client: TestClient, svcs: ServiceFactory, auth_headers: dict):
    default_users = [
        svcs.users.create_user(random_email(), random_string(), is_default_user=True) for _ in range(random_int(3, 10))
    ]

    email = random_email()
    password = random_string()

    # only default users can use this route
    r = api_client.post(
        users.default_user_router.url_path_for("replace_default_user"),
        data={"username": email, "password": password},
        headers=auth_headers,
    )
    assert r.status_code == 401

    r = api_client.post(
        users.default_user_router.url_path_for("replace_default_user"),
        data={"username": email, "password": password},
        headers={"Authorization": f"Bearer {default_users[0].create_token()}"},
    )
    r.raise_for_status()

    created_user_token = Token.parse_obj(r.json())
    created_user = svcs.users.get_authenticated_user_from_token(created_user_token.access_token)
    assert created_user.email == email

    r = api_client.get(
        users.router.url_path_for("get_user_by_email", email=created_user.email),
        headers={"Authorization": f"Bearer {created_user.create_token()}"},
    )
    r.raise_for_status()

    assert created_user == User.parse_obj(r.json())
    assert created_user.is_default_user is False

    all_users = svcs.users.get_all_users()
    assert created_user in all_users
    for user in default_users:
        assert user not in all_users
