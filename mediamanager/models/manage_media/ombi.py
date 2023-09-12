from datetime import datetime

from ..app.api import APIBase


class OmbiUser(APIBase):
    id: str
    user_name: str
    email_address: str

    alias: str
    """Friendly name for the user, if set, otherwise an empty string"""

    last_logged_in: datetime | None
    has_logged_in: bool
