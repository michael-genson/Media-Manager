from fastapi import APIRouter, Body, Depends, HTTPException, status

from .. import security
from ..models.users.exceptions import UserAlreadyExistsError
from ..models.users.users import User
from ..services.factory import ServiceFactory

router = APIRouter(prefix="/api/users", tags=["Users"], dependencies=[Depends(security.get_current_user)])
default_user_router = APIRouter(
    prefix="/api/users", tags=["Users"], dependencies=[Depends(security.get_default_user)], include_in_schema=False
)


@default_user_router.post("/replace-default")
def replace_default_user(email: str = Body(...), password: str = Body(...)) -> User:
    """Create a new user and delete all default users"""

    svcs = ServiceFactory()
    try:
        new_user = svcs.users.create_user(email, password)
    except UserAlreadyExistsError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "user already exists") from e

    svcs.users.delete_default_users()
    return new_user


@router.get("", response_model=list[User])
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


@router.post("", response_model=User)
def create_user(email: str = Body(...), password: str = Body(...)) -> User:
    svcs = ServiceFactory()
    try:
        return svcs.users.create_user(email, password)
    except UserAlreadyExistsError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "user already exists") from e


@router.delete("/{id}", response_model=None)
def delete_user(id: str) -> None:
    svcs = ServiceFactory()
    svcs.users.delete_user(id)
