from typing import Any

from mediamanager.mediamanager.models.tautulli import OrderDirection, TautulliMedia

from ...clients.mock_http_client import HTTPMethod
from .._base import BaseMockDatabase


class TautulliMockDatabase(BaseMockDatabase):
    LIBRARIES = "libraries"
    SUMMARIES = "summaries"
    DETAILS = "details"

    def _get_sorted_summaries(
        self,
        section_id: str,
        order_column: str | None = None,
        order_dir: OrderDirection | None = None,
        length: int = -1,
        *args,
        **kwargs,
    ) -> list[dict[str, Any]]:
        data = [d for d in self._get_all(self.SUMMARIES) if d["section_id"] == section_id]
        if order_column is not None:
            data.sort(key=lambda x: x.get(order_column or "", ""), reverse=order_dir is OrderDirection.descending)
        if length > 0:
            data = data[:length]

        return data

    def insert_media(self, media: TautulliMedia) -> None:
        self._insert(self.LIBRARIES, media.library.section_id, media.library.dict())
        self._insert(self.SUMMARIES, media.media_summary.rating_key, media.media_summary.dict())
        self._insert(self.DETAILS, media.media_detail.rating_key, media.media_detail.dict())

    def route(
        self,
        method: HTTPMethod,
        url: str,
        *args,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        **kwargs,
    ):
        if not (params and "cmd" in params):
            raise Exception("Invalid Command")

        command = params["cmd"]
        if command == "get_libraries" and method == HTTPMethod.GET:
            return self._200({"response": {"data": self._get_all(self.LIBRARIES)}})
        elif command == "get_library_media_info" and method == HTTPMethod.GET:
            return self._200({"response": {"data": {"data": self._get_sorted_summaries(**params)}}})
        elif command == "get_metadata" and method == HTTPMethod.GET:
            data = self._get(self.DETAILS, params["rating_key"])
            return self._200({"response": {"data": data}}) if data is not None else self._404()
        else:
            return self._404()
