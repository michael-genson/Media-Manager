from ..clients.overseerr import OverseerrClient
from ..models.manage_media.media_managers import MediaManagerTag
from ..models.manage_media.overseerr import OverseerrUser


class OverseerrService:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._client = self._get_client(base_url, api_key)

    @classmethod
    def _get_client(cls, *args, **kwargs) -> OverseerrClient:
        return OverseerrClient(*args, **kwargs)

    @classmethod
    def get_user_id_from_tag(cls, tag: MediaManagerTag) -> int | None:
        user_id = tag.label.split(" ")[0]
        try:
            return int(user_id)
        except ValueError:
            return None

    async def get_user(self, user_id: int) -> OverseerrUser | None:
        return await self._client.get_user(user_id)
