from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from ..app import secrets
from ..db.db_setup import session_context
from ..db.models.users.users import UserInDB
from ..models.users.exceptions import (
    InvalidPasswordError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)
from ..models.users.users import User, _PrivateUser

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @classmethod
    def _sanitize_email(cls, email: str) -> str:
        return email.strip().lower()

    def get_private_user(self, email: str) -> _PrivateUser | None:
        """Gets an unauthenticated user, if they exist"""

        with session_context() as session:
            user_in_db = session.query(UserInDB).filter_by(email=self._sanitize_email(email)).first()

        return _PrivateUser.from_orm(user_in_db) if user_in_db else None

    def delete_user(self, email: str) -> None:
        with session_context() as session:
            user_in_db = session.query(UserInDB).filter_by(email=self._sanitize_email(email)).first()
            if not user_in_db:
                return

            session.delete(user_in_db)
            session.commit()

    def authenticate_user(self, user: _PrivateUser, password: str) -> User:
        """Returns a validated user only if the provided password is correct, otherwise raises `InvalidPasswordError`"""

        if not _pwd_context.verify(password, user.password):
            raise InvalidPasswordError()

        return user.cast(User)

    def get_authenticated_user(self, email: str, password: str) -> User | None:
        """Fetches a user from the database, if it exists, and the password is correct"""

        private_user = self.get_private_user(email)
        if not private_user:
            return None

        try:
            return self.authenticate_user(private_user, password)
        except InvalidPasswordError:
            return None

    def get_authenticated_user_from_token(self, token: str) -> User:
        """Fetches a user using a valid access token"""

        try:
            payload = jwt.decode(token, secrets.db_secret_key, algorithms=[secrets.db_algorithm])
            email: str | None = payload.get("sub")

        except JWTError:
            raise InvalidTokenError()

        if not email:
            raise InvalidTokenError()

        user = self.get_private_user(email)
        if not user:
            raise UserDoesntExistError()

        return user.cast(User)

    def create_user(self, email: str, password: str, is_default_user: bool = False) -> User:
        """
        Creates a new user if the username isn't taken

        If the username is taken, raises `UserAlreadyExistsError`
        """

        with session_context() as session:
            new_user = UserInDB(email=email, password=_pwd_context.hash(password), is_default_user=is_default_user)
            try:
                session.add(new_user)
                session.commit()
            except IntegrityError as e:
                raise UserAlreadyExistsError from e

            return User.from_orm(new_user)
