import os
import pathlib
from typing import TypeVar

from pydantic import BaseSettings, validator
from pydantic.fields import ModelField

T = TypeVar("T")

APP_DIR = str(pathlib.Path(__file__).parent.parent.resolve())
CONFIG_DIR = "/config"
STATIC_DIR = os.path.join(APP_DIR, "static")


class AppSecrets(BaseSettings):
    app_api_key: str = ""  # required

    ### Media ###
    ombi_url: str = ""  # required
    ombi_api_key: str = ""  # required

    qbittorrent_url: str = ""
    qbittorrent_username: str = "admin"
    qbittorrent_password: str = "admin"

    tautulli_url: str = ""  # required
    tautulli_api_key: str = ""  # required

    radarr_url: str = ""
    radarr_api_key: str = ""

    sonarr_url: str = ""
    sonarr_api_key: str = ""

    ### SMTP ###
    smtp_server: str = "smtp`.`example.com"
    smtp_port: int = 587
    smtp_sender: str = "My SMTP User"
    smtp_username: str = "my-email@example.com"
    smtp_password: str = ""

    @validator("app_api_key", "ombi_url", "ombi_api_key", "tautulli_url", "tautulli_api_key")
    def assert_value(cls, v: T, field: ModelField) -> T:
        if not v:
            raise ValueError(f"{field.name} must not be empty")

        return v


class AppSettings(BaseSettings):
    app_title = "MediaManager"
    app_version = "0.1.1"

    admin_email: str = ""  # required
    """The admin email address to receive notifications"""
    monitored_libraries: list[str] | None = None
    """A non-empty list of library names (case-insensitive), or `None`"""

    uvicorn_workers: int = 1

    @validator("admin_email")
    def assert_value(cls, v: T, field: ModelField) -> T:
        if not v:
            raise ValueError(f"{field.name} must not be empty")

        return v

    @validator("monitored_libraries")
    def monitored_libraries_case_insensitive(cls, v: list[str] | None) -> list[str] | None:
        return [elem.lower() for elem in v] if v else None


class ExpiredMediaSettings(BaseSettings):
    expired_media_min_age: int = 120
    """How old media must be before it can be considered expired, in days"""
    expired_media_last_watched_threshold: int = 90
    """The threshold of when media is considered expired, in days"""
    expired_media_ignore_file: str = "expired_media_ignore.json"
    """The expiration blacklist JSON config filepath"""

    @validator("expired_media_min_age", "expired_media_last_watched_threshold")
    def assert_non_negative_value(cls, v: int, field: ModelField) -> int:
        if v < 0:
            raise ValueError(f"{field.name} must be an integer greater than or equal to 0")

        return v
