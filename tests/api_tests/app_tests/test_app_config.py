from fastapi.testclient import TestClient

from mediamanager.models.app.app_config import AppConfig
from mediamanager.routes import app_config
from mediamanager.services.factory import ServiceFactory
from tests.utils.generators import random_int, random_string, random_url


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


def test_update_app_config_monitored_libraries(api_client: TestClient, auth_headers: dict):
    monitored_library_ids = [random_string() for _ in range(random_int(3, 5))]

    r = api_client.get(app_config.router.url_path_for("get_app_config"), headers=auth_headers)
    r.raise_for_status()
    original_config = AppConfig.parse_obj(r.json())

    # set monitored library ids
    updated_config = AppConfig(**original_config.dict())
    updated_config.monitored_library_ids = monitored_library_ids
    r = api_client.put(
        app_config.router.url_path_for("update_app_config"), json=updated_config.dict(), headers=auth_headers
    )
    r.raise_for_status()

    r = api_client.get(app_config.router.url_path_for("get_app_config"), headers=auth_headers)
    r.raise_for_status()
    fetched_config_data: dict = r.json()
    assert fetched_config_data["monitoredLibraryIds"] == monitored_library_ids

    # clear monitored library ids
    updated_config.monitored_library_ids = []
    r = api_client.put(
        app_config.router.url_path_for("update_app_config"), json=updated_config.dict(), headers=auth_headers
    )
    r.raise_for_status()

    r = api_client.get(app_config.router.url_path_for("get_app_config"), headers=auth_headers)
    r.raise_for_status()
    fetched_config_data = r.json()
    assert fetched_config_data.get("monitoredLibraryIds") is None
