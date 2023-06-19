from datetime import datetime

from humps import camelize
from pydantic import BaseModel


class OmbiUser(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    id: str
    user_name: str
    email_address: str

    alias: str
    """Friendly name for the user, if set, otherwise an empty string"""

    last_logged_in: datetime | None
    has_logged_in: bool
