from sqlalchemy.orm import Mapped, mapped_column

from ..._model_base import SqlAlchemyBase


class ExpiredMediaIgnoredItem(SqlAlchemyBase):
    __tablename__ = "expired_media_ignored_item"
    id: Mapped[str] = mapped_column(primary_key=True, default=SqlAlchemyBase.generate_guid)

    rating_key: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    ttl: Mapped[int | None] = mapped_column()
