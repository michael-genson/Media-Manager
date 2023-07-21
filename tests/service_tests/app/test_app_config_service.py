from mediamanager.db.db_setup import session_context
from mediamanager.db.models.app.app_config import AppConfig as AppConfigDB
from mediamanager.models.app.app_config import AppConfig
from mediamanager.services.factory import ServiceFactory
from tests.utils.generators import random_int, random_url


def test_get_config(svcs: ServiceFactory):
    for _ in range(random_int(3, 10)):
        # fetching the config should never result in more than one config existing
        config = svcs.app_config.config

        with session_context() as session:
            configs = session.query(AppConfigDB).all()
            assert len(configs) == 1
            assert AppConfig.from_orm(configs[0]) == config


def test_patch_config(svcs: ServiceFactory):
    new_url = random_url()
    svcs.app_config.patch_config(radarr_url=new_url)

    assert svcs.app_config.config.radarr_url == new_url
    with session_context() as session:
        configs = session.query(AppConfigDB).all()
        assert len(configs) == 1
        assert configs[0].radarr_url == new_url


def test_update_config(svcs: ServiceFactory):
    original_config = svcs.app_config.config

    new_url = random_url()
    new_config = AppConfig(**original_config.dict())
    new_config.radarr_url = new_url

    svcs.app_config.update_config(new_config)
    assert svcs.app_config.config.radarr_url == new_url
    with session_context() as session:
        configs = session.query(AppConfigDB).all()
        assert len(configs) == 1
        assert configs[0].radarr_url == new_url
