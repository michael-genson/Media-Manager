from .._base import APIBase


class User(APIBase):
    id: str
    email: str
    is_default_user: bool


class _PrivateUser(User):
    """Used only for verifying passwords"""

    password: str
