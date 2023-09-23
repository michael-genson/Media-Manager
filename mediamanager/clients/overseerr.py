from fastapi import HTTPException, status

from ..models.manage_media.overseerr import OverseerrUser
from ._base import BaseHTTPClient


class OverseerrClient(BaseHTTPClient):
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = self._parse_base_url(base_url)
        self._user_by_id: dict[int, OverseerrUser | None] = {}
        """Internal user cache"""

        return super().__init__(base_headers={"X-Api-Key": api_key})

    def _url(self, endpoint: str, version: int = 1) -> str:
        if not endpoint or endpoint == "/":
            raise ValueError("endpoint must not be empty")
        if endpoint[0] == "/":
            endpoint = endpoint[1:]

        return f"{self.base_url}/api/v{version}/{endpoint}"

    async def get_user(self, user_id: int) -> OverseerrUser | None:
        if user_id not in self._user_by_id:
            async with self.client as client:
                try:
                    r = await client.get(self._url(f"/user/{user_id}"))
                    data = self.parse_response_json(r)
                    self._user_by_id[user_id] = OverseerrUser.parse_obj(data)
                except HTTPException as e:
                    if e.status_code != status.HTTP_404_NOT_FOUND:
                        raise

                    self._user_by_id[user_id] = None

        return self._user_by_id[user_id]
