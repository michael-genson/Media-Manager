import os

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from mediamanager.settings import app_settings

# force app to use temp database
os.environ["db_file"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pytest_db.db")

# inject fake secret
mp = MonkeyPatch()
mp.setattr(app_settings.AppSecrets, "db_secret_key", "pytest-secret-key")

from mediamanager import app  # noqa:  E402
from mediamanager.db import db_setup, models as db_models  # noqa:  E402
from mediamanager.models.app.app_config import AppConfig  # noqa:  E402
from mediamanager.services.app_config import AppConfigService  # noqa:  E402
from mediamanager.services.smtp import SMTPService  # noqa:  E402


from .fixtures import *  # noqa:  E402, F403
from .utils.generators import random_email, random_string, random_url  # noqa:  E402

settings = app_settings.AppSettings()


def do_nothing(*args, **kwargs):
    return None


def override_app_config():
    svc = AppConfigService()
    svc._create_new_config()
    svc.update_config(
        AppConfig(
            ombi_url=random_string(),
            ombi_api_key=random_string(),
            qbittorrent_url=random_url(),
            qbittorrent_username=random_string(),
            qbittorrent_password=random_string(),
            tautulli_url=random_url(),
            tautulli_api_key=random_string(),
            radarr_url=random_url(),
            radarr_api_key=random_string(),
            sonarr_url=random_url(),
            sonarr_api_key=random_string(),
            smtp_port=587,
            smtp_sender=random_url(),
            smtp_username=random_email(),
            smtp_password=random_string(),
        )
    )


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    db_setup.init_db()
    override_app_config()

    yield

    # delete temp db
    os.unlink(settings.db_file)


@pytest.fixture(scope="function", autouse=True)
def clear_db():
    yield

    # empty db
    with db_setup.session_context() as session:
        meta = db_models.SqlAlchemyBase.metadata
        for table in reversed(meta.sorted_tables):
            session.execute(table.delete())
        session.commit()

    # re-create app config, since it's missing now
    override_app_config()


@pytest.fixture(scope="session", autouse=True)
def mock_services():
    mp.setattr(SMTPService, "send", do_nothing)
    yield


@pytest.fixture(scope="session")
def api_client():
    yield TestClient(app.app)
