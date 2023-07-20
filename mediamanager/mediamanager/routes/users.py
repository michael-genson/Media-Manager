from fastapi import APIRouter, Depends, HTTPException, status

from .. import security
from ..models.users.users import User
from ..services.factory import ServiceFactory

router = APIRouter(prefix="/api/users", tags=["Users"], dependencies=[Depends(security.get_current_user)])


@router.get("/", response_model=list[User])
def get_all_users() -> list[User]:
    svcs = ServiceFactory()
    return svcs.users.get_all_users()


@router.get("/{id}", response_model=User)
def get_user(id: str) -> User:
    svcs = ServiceFactory()
    user = svcs.users.get_public_user(id)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    else:
        return user


@router.get("/email/{email}", response_model=User)
def get_user_by_email(email: str) -> User:
    svcs = ServiceFactory()
    user = svcs.users.get_public_user_by_email(email)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    else:
        return user
