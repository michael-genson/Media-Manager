from qbittorrent import Client  # type: ignore
from requests.exceptions import HTTPError

from ..models.manage_media.qbittorrent import QBTTorrent, QBTTorrentFilter


class QBTService:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._client = Client(base_url)
        self._client.login(username, password)

    def get_all_torrents(
        self, filter: QBTTorrentFilter | None = None, category: str | None = None, **additional_filters
    ) -> list[QBTTorrent]:
        """
        For additional filters,
        [see the documentation here](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#torrent-management)
        """
        if filter:
            additional_filters["filter"] = filter.value
        if category is not None:
            additional_filters["category"] = category

        torrents_data: list = self._client.torrents(**additional_filters)
        return [QBTTorrent.parse_obj(data) for data in torrents_data]

    def get_torrent(self, torrent_hash: str) -> QBTTorrent | None:
        try:
            response = self._client.get_torrent(torrent_hash)
            return QBTTorrent.parse_obj(response)
        except HTTPError as e:
            if e.response.status_code != 404:
                raise
            else:
                return None
