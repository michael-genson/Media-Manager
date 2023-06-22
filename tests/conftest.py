import os
from .utils.generators import random_string, random_url, random_email


def load_env() -> None:
    env_vars: dict[str, str] = {
        "app_api_key": random_string(),
        "admin_email": random_email(),
        "ombi_url": random_url(),
        "ombi_api_key": random_string(),
        "tautulli_url": random_url(),
        "tautulli_api_key": random_string(),
        "radarr_url": random_url(),
        "radarr_api_key": random_string(),
        "sonarr_url": random_url(),
        "sonarr_api_key": random_string(),
        "smtp_port": str(587),
        "smtp_sender": random_url(),
        "smtp_username": random_email(),
        "smtp_password": random_string(),
    }
    for k, v in env_vars.items():
        os.environ[k.upper()] = v


load_env()

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from mediamanager.mediamanager.services.smtp import SMTPService
from mediamanager.mediamanager.app import app
from .fixtures import *


def do_nothing(*args, **kwargs):
    return None


@pytest.fixture(scope="session", autouse=True)
def mock_services():
    mp = MonkeyPatch()
    mp.setattr(SMTPService, "send", do_nothing)
    yield


@pytest.fixture(scope="session")
def api_client():
    yield TestClient(app)
