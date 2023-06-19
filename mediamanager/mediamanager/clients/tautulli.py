from ..models.tautulli import OrderDirection, TautulliLibrary, TautulliMediaDetail, TautulliMediaSummary
from ._base import BaseHTTPClient


class TautulliClient(BaseHTTPClient):
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = self._parse_base_url(base_url)
        return super().__init__(base_params={"apikey": api_key})

    @classmethod
    def _parse_base_url(cls, base_url: str) -> str:
        base_url = super()._parse_base_url(base_url)
        return f"{base_url}/api/v2"

    def _request_params(self, cmd: str, ignore_null: bool = True, **kwargs) -> dict[str, str]:
        if not ignore_null:
            return {"cmd": cmd, **kwargs}
        else:
            return {"cmd": cmd, **{k: v for k, v in kwargs.items() if v is not None}}

    async def get_libraries(self) -> list[TautulliLibrary]:
        async with self.client as client:
            r = await client.get(self.base_url, params=self._request_params("get_libraries"))
            data: dict = self.parse_response_json(r)  # type: ignore

        return [TautulliLibrary.parse_obj(lib) for lib in data["response"]["data"]]

    async def get_library_media_summaries(
        self,
        section_id: str,
        order_column: str | None = None,
        order_dir: OrderDirection | None = None,
        length: int = 10,
        **kwargs,
    ) -> list[TautulliMediaSummary]:
        async with self.client as client:
            r = await client.get(
                self.base_url,
                params=self._request_params(
                    "get_library_media_info",
                    section_id=section_id,
                    order_column=order_column,
                    order_dir=order_dir.value if order_dir else None,
                    length=length,
                    **kwargs,
                ),
            )
            data: dict = self.parse_response_json(r)  # type: ignore

        return [TautulliMediaSummary.parse_obj(media) for media in data["response"]["data"]["data"]]

    async def get_library_media_detail(self, rating_key: str) -> TautulliMediaDetail:
        async with self.client as client:
            r = await client.get(self.base_url, params=self._request_params("get_metadata", rating_key=rating_key))
            data: dict = self.parse_response_json(r)  # type: ignore

        return TautulliMediaDetail.parse_obj(data["response"]["data"])
