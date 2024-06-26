import os
import pathlib
import secrets
from typing import TypeVar

from pydantic import BaseSettings, validator
from pydantic.fields import ModelField

T = TypeVar("T")

APP_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
CONFIG_DIR = "/data"
STATIC_DIR = os.path.join(APP_DIR, "static")


class AppSecrets:
    def __init__(self) -> None:
        self._db_secret_key: str | None = None
        self.db_algorithm: str = "HS256"

    @property
    def db_secret_key(self) -> str:
        if self._db_secret_key is None:
            fp = pathlib.Path(os.path.join(CONFIG_DIR, ".secret"))
            fp.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(fp) as f:
                    self._db_secret_key = f.read()
            except FileNotFoundError:
                with open(fp, "w") as f:
                    new_secret = secrets.token_hex(32)
                    f.write(new_secret)
                self._db_secret_key = new_secret

        return self._db_secret_key

    @validator("_db_secret_key", pre=True, always=True)
    def ignore_environment(cls, _) -> None:
        return None


class AppSettings(BaseSettings):
    app_title = "MediaManager"
    app_version = "0.3.5"
    debug = False

    db_file: str = os.path.join(CONFIG_DIR, "media_manager.db")
    default_user_email: str = "changeme@example.com"
    default_user_password: str = "password"

    uvicorn_workers: int = 1

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

    overseerr_url: str = ""
    overseerr_api_key: str = ""

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
