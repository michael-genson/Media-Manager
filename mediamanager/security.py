from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .models.users.exceptions import UserAuthenticationError
from .models.users.users import User
from .services.factory import ServiceFactory

UNAUTHORIZED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/authorization/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Gets the currently authenticated user"""

    svcs = ServiceFactory()
    try:
        return svcs.users.get_authenticated_user_from_token(token)
    except UserAuthenticationError:
        raise UNAUTHORIZED_ERROR


async def get_any_user(token: str = Depends(oauth2_scheme)) -> User:
    """Gets the currently authenticated user, even if they are a default user"""
    svcs = ServiceFactory()
    try:
        return svcs.users.get_authenticated_user_from_token(token, allow_default=True)
    except UserAuthenticationError:
        raise UNAUTHORIZED_ERROR


async def get_default_user(token: str = Depends(oauth2_scheme)) -> User:
    """Gets the currently authenticated user"""

    try:
        user = await get_any_user(token)
        if user.is_default_user:
            return user
        else:
            raise UNAUTHORIZED_ERROR

    except UserAuthenticationError:
        raise UNAUTHORIZED_ERROR
