import time

from .._base import APIBase


class ExpiredMediaIgnoredItemIn(APIBase):
    rating_key: str
    """The unique id of the media item in Tautulli"""

    name: str | None = None
    ttl: int | None = None
    """The time this item is removed from the ignore list, in seconds since epoch"""


class ExpiredMediaIgnoredItem(ExpiredMediaIgnoredItemIn):
    name: str

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.ttl if self.ttl else False


class ExpiredMediaIgnoredItems(APIBase):
    items: list[ExpiredMediaIgnoredItem]
