import pytest
from fastapi.testclient import TestClient


def test_get_expired_media(api_client: TestClient):
    pass


def test_get_ignore_list(api_client: TestClient):
    # TODO: implement in-memory json and mock service for testing
    pass


@pytest.mark.skip("Not Implemented")
def test_get_ignore_list_expired_items(api_client: TestClient):
    pass


def test_add_ignored_media(api_client: TestClient):
    pass


def test_delete_ignored_media(api_client: TestClient):
    pass
