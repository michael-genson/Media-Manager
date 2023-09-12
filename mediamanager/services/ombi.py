from ..clients.ombi import OmbiClient
from ..models.manage_media.ombi import OmbiUser


class OmbiService:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._client = self._get_client(base_url, api_key)

    @classmethod
    def _get_client(cls, *args, **kwargs) -> OmbiClient:
        return OmbiClient(*args, **kwargs)

    async def get_user_by_username(self, username: str) -> OmbiUser | None:
        username = username.lower()

        all_users = await self._client.get_all_users()
        for user in all_users:
            if user.user_name.lower() == username:
                return user

        return None
