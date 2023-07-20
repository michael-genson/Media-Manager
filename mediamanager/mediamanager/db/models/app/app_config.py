from sqlalchemy.orm import Mapped, mapped_column

from ..._model_base import SqlAlchemyBase


class AppConfig(SqlAlchemyBase):
    __tablename__ = "app_config"
    id: Mapped[str] = mapped_column(primary_key=True, default=SqlAlchemyBase.generate_guid)

    ombi_url: Mapped[str | None] = mapped_column()
    ombi_api_key: Mapped[str | None] = mapped_column()

    qbittorrent_url: Mapped[str | None] = mapped_column()
    qbittorrent_username: Mapped[str | None] = mapped_column()
    qbittorrent_password: Mapped[str | None] = mapped_column()

    tautulli_url: Mapped[str | None] = mapped_column()
    tautulli_api_key: Mapped[str | None] = mapped_column()

    radarr_url: Mapped[str | None] = mapped_column()
    radarr_api_key: Mapped[str | None] = mapped_column()

    sonarr_url: Mapped[str | None] = mapped_column()
    sonarr_api_key: Mapped[str | None] = mapped_column()

    smtp_server: Mapped[str | None] = mapped_column()
    smtp_port: Mapped[int | None] = mapped_column()
    smtp_sender: Mapped[str | None] = mapped_column()
    smtp_username: Mapped[str | None] = mapped_column()
    smtp_password: Mapped[str | None] = mapped_column()
