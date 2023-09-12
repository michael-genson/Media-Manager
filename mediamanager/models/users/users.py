from datetime import datetime, timedelta

from jose import jwt
from pydantic import BaseModel

from ...settings import app_settings
from ..app.api import APIBase

secrets = app_settings.AppSecrets()


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class User(APIBase):
    id: str
    email: str
    is_default_user: bool

    class Config:
        orm_mode = True

    def create_token(self, expires: timedelta | None = None) -> str:
        """Creates an access token for this user. Optionally specify an expiration time"""

        if not expires:
            expires = timedelta(minutes=60 * 24 * 30)  # TODO: make this configurable

        expiration = datetime.utcnow() + expires
        data = {"sub": self.email, "exp": expiration}
        return jwt.encode(data, secrets.db_secret_key, algorithm=secrets.db_algorithm)


class PrivateUser(User):
    """Used only for verifying passwords"""

    password: str
    """a user's hashed password"""
