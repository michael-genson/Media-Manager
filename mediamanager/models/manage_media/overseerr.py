from datetime import datetime

from ..app.api import APIBase


class OverseerrUser(APIBase):
    id: int
    email: str
    username: str | None = None
    display_name: str | None = None

    plex_id: int | None = None
    plex_username: str | None = None
    avatar: str | None = None

    created_at: datetime
    updated_at: datetime

    @property
    def name(self) -> str:
        """The best representation of this user's name available. Guaranteed to not be empty"""

        if self.display_name:
            return self.display_name
        elif self.username:
            return self.username
        elif self.plex_username:
            return self.plex_username
        else:
            return self.email
