from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseMixins:
    """
    `self.update` method which directly passing arguments to the `__init__`
    """

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)


class SqlAlchemyBase(DeclarativeBase, BaseMixins):
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.now, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
