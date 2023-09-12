from ..app.api import APIBase


class ExpiredMediaIgnoredItemIn(APIBase):
    rating_key: str
    """The unique id of the media item in Tautulli"""

    name: str | None = None
    ttl: int | None = None
    """The time this item is removed from the ignore list, in seconds since epoch"""


class ExpiredMediaIgnoredItem(ExpiredMediaIgnoredItemIn):
    id: str
    name: str

    class Config:
        orm_mode = True
