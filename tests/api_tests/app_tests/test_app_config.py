from fastapi.testclient import TestClient

from mediamanager.mediamanager.models.app.app_config import AppConfig
from mediamanager.mediamanager.routes import app_config
from mediamanager.mediamanager.services.factory import ServiceFactory
from tests.utils.generators import random_url


def test_get_app_config(api_client: TestClient, svcs: ServiceFactory, auth_headers: dict):
    r = api_client.get(app_config.router.url_path_for("get_app_config"), headers=auth_headers)
    r.raise_for_status()
    assert svcs.app_config.config == AppConfig.parse_obj(r.json())


def test_update_app_config(api_client: TestClient, auth_headers: dict):
    r = api_client.get(app_config.router.url_path_for("get_app_config"), headers=auth_headers)
    r.raise_for_status()
    original_config = AppConfig.parse_obj(r.json())

    updated_config = AppConfig(**original_config.dict())
    updated_config.radarr_url == random_url()
    r = api_client.put(
        app_config.router.url_path_for("update_app_config"), json=updated_config.dict(), headers=auth_headers
    )
    r.raise_for_status()
    assert updated_config == AppConfig.parse_obj(r.json())

    r = api_client.get(app_config.router.url_path_for("get_app_config"), headers=auth_headers)
    r.raise_for_status()
    fetched_config = AppConfig.parse_obj(r.json())
    assert fetched_config == updated_config
