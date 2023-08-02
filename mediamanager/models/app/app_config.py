from .._base import APIBase


class AppConfig(APIBase):
    ombi_url: str | None = None
    ombi_api_key: str | None = None

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
