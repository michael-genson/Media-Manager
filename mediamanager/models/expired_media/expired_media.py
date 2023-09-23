from typing import Any

from ..app.api import APIBase
from ..app.data_exporter import Exportable
from ..manage_media.overseerr import OverseerrUser
from ..manage_media.tautulli import TautulliMedia


class ExpiredMedia(APIBase, Exportable):
    media: TautulliMedia
    media_url: str | None = None
    user: OverseerrUser | None = None

    def to_csv(self) -> dict[str, Any]:
        return {
            "rating_key": self.media.media_summary.rating_key,
            "media_type": self.media.media_summary.media_type.value,
            "title": self.media.media_summary.title,
            "added_at": self.media.media_summary.added_at.date().isoformat(),
            "url": self.media_url,
            "requesting_user_name": self.user.name if self.user else None,
            "requesting_user_email": self.user.email if self.user else None,
        }
