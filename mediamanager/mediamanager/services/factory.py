from ..app import secrets
from ..models.tautulli import LibraryType
from . import data_exporter, media_managers, ombi, qbittorrent, smtp, tautulli, users


class ServiceFactory:
    def __init__(self) -> None:
        self._users: users.UserService | None = None

        self._ombi: ombi.OmbiService | None = None
        self._qbittorrent: qbittorrent.QBTService | None = None
        self._radarr: media_managers.RadarrService | None = None
        self._sonarr: media_managers.SonarrService | None = None
        self._tautulli: tautulli.TautulliService | None = None

        self._data_exporter: data_exporter.DataExporter | None = None
        self._smtp: smtp.SMTPService | None = None

    @property
    def users(self):
        if not self._users:
            self._users = users.UserService()

        return self._users

    @property
    def ombi(self):
        if not self._ombi:
            self._ombi = ombi.OmbiService(secrets.ombi_url, secrets.ombi_api_key)

        return self._ombi

    @property
    def qbittorrent(self):
        if not self._qbittorrent:
            self._qbittorrent = qbittorrent.QBTService(
                secrets.qbittorrent_url, secrets.qbittorrent_username, secrets.qbittorrent_password
            )

        return self._qbittorrent

    @property
    def radarr(self):
        if not self._radarr:
            self._radarr = media_managers.RadarrService(secrets.radarr_url, secrets.radarr_api_key)

        return self._radarr

    @property
    def sonarr(self):
        if not self._sonarr:
            self._sonarr = media_managers.SonarrService(secrets.sonarr_url, secrets.sonarr_api_key)

        return self._sonarr

    @property
    def tautulli(self):
        if not self._tautulli:
            self._tautulli = tautulli.TautulliService(secrets.tautulli_url, secrets.tautulli_api_key)

        return self._tautulli

    @property
    def data_exporter(self):
        if not self._data_exporter:
            self._data_exporter = data_exporter.DataExporter()

        return self._data_exporter

    @property
    def smtp(self):
        if not self._smtp:
            self._smtp = smtp.SMTPService(
                secrets.smtp_server, secrets.smtp_port, secrets.smtp_username, secrets.smtp_password
            )

        return self._smtp

    def get_media_manager_service(self, library_type: LibraryType) -> media_managers.MediaManagerServiceBase | None:
        if library_type is LibraryType.movie:
            return self.radarr
        elif library_type is LibraryType.show:
            return self.sonarr
        else:
            return None
