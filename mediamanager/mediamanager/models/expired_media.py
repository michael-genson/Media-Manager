import time
from typing import Any

from pydantic import BaseModel

from .data_exporter import Exportable
from .ombi import OmbiUser
from .tautulli import TautulliMedia


class ExpiredMediaIgnoredItemIn(BaseModel):
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


class ExpiredMediaIgnoredItems(BaseModel):
    items: list[ExpiredMediaIgnoredItem]


class ExpiredMedia(BaseModel, Exportable):
    media: TautulliMedia
    media_url: str | None = None
    user: OmbiUser | None = None

    def to_csv(self) -> dict[str, Any]:
        return {
            "rating_key": self.media.media_summary.rating_key,
            "media_type": self.media.media_summary.media_type.value,
            "title": self.media.media_summary.title,
            "added_at": self.media.media_summary.added_at.date().isoformat(),
            "url": self.media_url,
            "requesting_user_name": self.user.user_name if self.user else None,
            "requesting_user_email": self.user.email_address if self.user else None,
            "requesting_user_alias": self.user.alias if self.user else None,
        }
