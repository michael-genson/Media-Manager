from sqlalchemy.orm import Mapped, mapped_column

from ..._model_base import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)

    email: Mapped[str | None] = mapped_column(index=True, unique=True)
    password: Mapped[str | None] = mapped_column()

    is_default_user: Mapped[bool] = mapped_column(default=False)
