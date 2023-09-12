from ..models.manage_media.ombi import OmbiUser
from ._base import BaseHTTPClient


class OmbiClient(BaseHTTPClient):
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = self._parse_base_url(base_url)
        self._all_users: list[OmbiUser] | None = None
        """Internal cache for all users"""

        return super().__init__(base_params={"ApiKey": api_key})

    def _url(self, endpoint: str, version: int = 1) -> str:
        if not endpoint or endpoint == "/":
            raise ValueError("endpoint must not be empty")
        if endpoint[0] == "/":
            endpoint = endpoint[1:]

        return f"{self.base_url}/api/v{version}/{endpoint}"

    async def get_all_users(self) -> list[OmbiUser]:
        if self._all_users is None:
            async with self.client as client:
                r = await client.get(self._url("/Identity/Users"))
                data = self.parse_response_json(r)

            self._all_users = [OmbiUser.parse_obj(user) for user in data]

        return self._all_users
