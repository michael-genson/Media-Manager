import os
import pathlib
from typing import TypeVar

from pydantic import BaseSettings, validator
from pydantic.fields import ModelField

T = TypeVar("T")

APP_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
CONFIG_DIR = "/data"
STATIC_DIR = os.path.join(APP_DIR, "static")

DEFAULT_SECRET_KEY = "X-UNSAFE-KEY"


class AppSecrets(BaseSettings):
    db_secret_key: str = DEFAULT_SECRET_KEY  # TODO: warn if using
    db_algorithm: str = "HS256"


class AppSettings(BaseSettings):
    app_title = "MediaManager"
    app_version = "0.2.1"

    db_file: str = "/data/media_manager.db"
    default_user_email: str = "changeme@email.com"
    default_user_password: str = "password"

    monitored_libraries: list[str] | None = None  # TODO: migrate this to app config
    """A non-empty list of library names (case-insensitive), or `None`"""

    uvicorn_workers: int = 1

    @validator("monitored_libraries")
    def monitored_libraries_case_insensitive(cls, v: list[str] | None) -> list[str] | None:
        return [elem.lower() for elem in v] if v else None

    @property
    def db_url(self):
        return f"sqlite+pysqlite:///{self.db_file}"


class ExpiredMediaSettings(BaseSettings):  # TODO: migrate this to its own database config
    expired_media_min_age: int = 120
    """How old media must be before it can be considered expired, in days"""
    expired_media_last_watched_threshold: int = 90
    """The threshold of when media is considered expired, in days"""

    @validator("expired_media_min_age", "expired_media_last_watched_threshold")
    def assert_non_negative_value(cls, v: int, field: ModelField) -> int:
        if v < 0:
            raise ValueError(f"{field.name} must be an integer greater than or equal to 0")

        return v


class _AppConfigDefaults(BaseSettings):
    """Defaults for new applications"""

    ### Media ###
    ombi_url: str = ""
    ombi_api_key: str = ""

    qbittorrent_url: str = ""
    qbittorrent_username: str = ""
    qbittorrent_password: str = ""

    tautulli_url: str = ""
    tautulli_api_key: str = ""

    radarr_url: str = ""
    radarr_api_key: str = ""

    sonarr_url: str = ""
    sonarr_api_key: str = ""

    ### SMTP ###
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_sender: str = ""
    smtp_username: str = ""
    smtp_password: str = ""
