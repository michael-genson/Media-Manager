from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..models.users.users import Token, User
from ..security import UNAUTHORIZED_ERROR, get_current_user
from ..services.factory import ServiceFactory

router = APIRouter(prefix="/api/authorization", tags=["Authorization"])


@router.post("/token", response_model=Token)
async def log_in_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Generates a new token from a username and password"""

    svcs = ServiceFactory()
    user = svcs.users.get_authenticated_user(form_data.username, form_data.password)
    if user:
        return Token(access_token=user.create_token())
    else:
        raise UNAUTHORIZED_ERROR


@router.post("/token/refresh", response_model=Token)
def refresh_token(user: User = Depends(get_current_user)) -> Token:
    return Token(access_token=user.create_token())


@router.get("/me", response_model=User)
async def get_logged_in_user(user: User = Depends(get_current_user)) -> User:
    return user
