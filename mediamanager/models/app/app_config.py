import json
from logging import getLogger
from typing import Any

from pydantic import root_validator

from .api import APIBase

logger = getLogger("app_config")


class AppConfig(APIBase):
    monitored_library_ids: list[str] | None = None

    ombi_url: str | None = None
    ombi_api_key: str | None = None

    overseerr_url: str | None = None
    overseerr_api_key: str | None = None

    qbittorrent_url: str | None = None
    qbittorrent_username: str | None = None
    qbittorrent_password: str | None = None

    tautulli_url: str | None = None
    tautulli_api_key: str | None = None

    radarr_url: str | None = None
    radarr_api_key: str | None = None

    sonarr_url: str | None = None
    sonarr_api_key: str | None = None

    smtp_server: str | None = None
    smtp_port: int | None = None
    smtp_sender: str | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def populate_monitored_library_ids(cls, values: dict[str, Any]) -> dict[str, Any]:
        values = dict(values)  # pydantic implements a GetterDict which prevents setting values
        if not (monitored_library_ids_json := values.pop("monitored_library_ids_json", None)):
            return values

        try:
            values["monitored_library_ids"] = json.loads(monitored_library_ids_json) or None
        except json.JSONDecodeError:
            logger.warning("AppConfig contains invalid monitored_library_ids_json; ignoring")
            logger.warning(monitored_library_ids_json)
            values["monitored_library_ids"] = None

        return values
