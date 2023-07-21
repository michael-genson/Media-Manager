from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from mediamanager.db.db_setup import session_context
from mediamanager.db.models.users.users import UserInDB
from mediamanager.models.users.exceptions import (
    InvalidTokenError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)
from mediamanager.models.users.users import User
from mediamanager.services.factory import ServiceFactory
from tests.utils.generators import random_email, random_int, random_string


def test_create_user(svcs: ServiceFactory):
    email = random_email()
    password = random_string()

    new_user = svcs.users.create_user(email, password)
    assert new_user.email == email

    with session_context() as session:
        fetched_users = session.query(UserInDB).filter_by(id=new_user.id).all()
        assert len(fetched_users) == 1
        fetched_user = User.from_orm(fetched_users[0])

    assert new_user == fetched_user


def test_create_user_clean_email(svcs: ServiceFactory):
    email = f" A{random_email()} "
    password = random_string()

    assert svcs.users.create_user(email, password).email == email.strip().lower()


def test_create_duplicate_user(svcs: ServiceFactory):
    email = f" A{random_email()} "
    svcs.users.create_user(email, random_string())

    with pytest.raises(UserAlreadyExistsError):
        svcs.users.create_user(email, random_string())


def test_get_user(svcs: ServiceFactory):
    email = random_email()
    password = random_string()

    new_user = svcs.users.create_user(email, password)
    fetched_user = svcs.users.get_authenticated_user(email, password)
    assert fetched_user == new_user


def test_get_user_clean_email(svcs: ServiceFactory):
    email = random_email()
    password = random_string()

    new_user = svcs.users.create_user(email, password)
    fetched_user = svcs.users.get_authenticated_user(f" {email.upper()} ", password)
    assert fetched_user == new_user


def test_get_invalid_user(svcs: ServiceFactory):
    email = random_email()
    svcs.users.create_user(email, random_string())

    assert svcs.users.get_private_user(random_email()) is None
    assert svcs.users.get_authenticated_user(random_email(), random_string()) is None
    assert svcs.users.get_authenticated_user(email, random_string()) is None


def test_delete_user(svcs: ServiceFactory):
    email = random_email()
    password = random_string()

    new_user = svcs.users.create_user(email, password)
    svcs.users.delete_user(new_user.id)
    assert svcs.users.get_private_user(email) is None
    assert svcs.users.get_authenticated_user(email, password) is None

    with session_context() as session:
        all_users = session.query(UserInDB).all()
        all_user_ids = [user.id for user in all_users]
        assert new_user.id not in all_user_ids


def test_get_user_from_token(svcs: ServiceFactory):
    new_user = svcs.users.create_user(random_email(), random_string())
    token = new_user.create_token()

    fetched_user = svcs.users.get_authenticated_user_from_token(token)
    assert fetched_user == new_user


def test_get_user_from_invalid_token(svcs: ServiceFactory):
    new_user = svcs.users.create_user(random_email(), random_string())

    with pytest.raises(InvalidTokenError):
        svcs.users.get_authenticated_user_from_token(random_string())

    token = new_user.create_token(timedelta(days=random_int(1, 10)))
    with freeze_time(datetime.utcnow() + timedelta(days=random_int(365 * 10, 365 * 20))):
        with pytest.raises(InvalidTokenError):
            svcs.users.get_authenticated_user_from_token(token)

    svcs.users.delete_user(new_user.id)
    with pytest.raises(UserDoesntExistError):
        svcs.users.get_authenticated_user_from_token(token)
